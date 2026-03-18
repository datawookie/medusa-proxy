#!/usr/bin/env python3

import os
import re
import signal
import subprocess
import sys
import time

from config import VERSION, parse_time_interval
from config import (
    HEADS,
    TORS,
    PROXY_CHECK_INTERVAL,
    PROXY_ROTATE_INTERVAL,
    PROXY_STARTUP_TIMEOUT,
)
from proxy import Privoxy, log

PROXY_LIST_TXT = "proxy-list.txt"
PROXY_LIST_PY = "proxy-list.py"


def reap_children(*_):
    """Reap any exited child process so PID 1 does not accumulate zombies."""
    while True:
        try:
            pid, _ = os.waitpid(-1, os.WNOHANG)
        except ChildProcessError:
            # No child processes.
            break

        if pid == 0:
            # Child processes still running, nothing to reap right now.
            break


def get_versions():
    for cmd in ["privoxy --version", "haproxy -v", "tor --version"]:
        result = subprocess.run(cmd.split(), stdout=subprocess.PIPE)

        version = result.stdout.decode("utf-8").partition("\n")[0]
        version = re.sub(r" +([0-9/]{10})?[ -]*\(?(https://.*)?\)?\.?$", "", version)
        version = re.sub(r" version", ":", version)
        version = re.sub(r"\.$", "", version)

        log.info("- " + version)


def main():
    signal.signal(signal.SIGCHLD, reap_children)

    log.info("========================================")
    log.info(f"Medusa Proxy: {VERSION}")
    log.info("")
    get_versions()
    log.info("========================================")

    # Log configuration
    log.info("Configuration:")
    log.info(f"  HEADS: {HEADS}")
    log.info(f"  TORS: {TORS}")
    log.info(f"  PROXY_CHECK_INTERVAL: {PROXY_CHECK_INTERVAL}")
    log.info(f"  PROXY_ROTATE_INTERVAL: {PROXY_ROTATE_INTERVAL}")
    log.info(f"  PROXY_STARTUP_TIMEOUT: {PROXY_STARTUP_TIMEOUT}")
    log.info("")

    # Create Privoxy instances with Tor backends
    privoxy_instances = [Privoxy(TORS, i) for i in range(HEADS)]

    # Parse intervals
    check_interval = parse_time_interval(PROXY_CHECK_INTERVAL).total_seconds()
    rotate_interval = parse_time_interval(PROXY_ROTATE_INTERVAL).total_seconds()
    startup_timeout = parse_time_interval(PROXY_STARTUP_TIMEOUT).total_seconds()

    # Wait for at least one Tor instance to become available
    log.info("Waiting for Tor instances to bootstrap...")
    startup_check_interval = 10  # Check every 10 seconds
    start_time = time.time()

    while time.time() - start_time < startup_timeout:
        # Check if any Tor instance is working
        any_working = False
        for instance in privoxy_instances:
            for tor_proxy in instance.haproxy.proxies:
                if tor_proxy.working:
                    any_working = True
                    break
            if any_working:
                break

        if any_working:
            log.info("At least one Tor instance is ready. Starting main loop.")
            break

        elapsed = time.time() - start_time
        remaining = startup_timeout - elapsed
        log.debug(
            f"  No Tor instances ready yet. Waiting... ({remaining:.0f}s remaining)"
        )
        time.sleep(startup_check_interval)
    else:
        log.warning(
            f"Startup timeout ({PROXY_STARTUP_TIMEOUT}) reached. Starting main loop anyway."
        )
        log.warning("Health check will attempt to restart non-working Tor instances.")

    log.info("Writing proxy list.")
    with open(PROXY_LIST_TXT, "wt") as file:
        for http in privoxy_instances:
            file.write("http://127.0.0.1:%d\n" % http.port)
    log.info("Done.")

    log.info("Serving proxy list.")
    os.spawnl(os.P_NOWAIT, sys.executable, sys.executable, PROXY_LIST_PY)

    # Track last rotation time
    last_rotation = time.time()

    # Main event loop
    while True:
        # Health check phase
        log.info("Testing proxies.")
        for instance in privoxy_instances:
            log.info(f"* Privoxy {instance.id}")
            haproxy = instance.haproxy
            for tor_proxy in haproxy.proxies:
                if not tor_proxy.working:
                    log.warning(f"  Restarting Tor on port {tor_proxy.port}.")
                    tor_proxy.restart()

        # Check if rotation is needed
        current_time = time.time()
        time_since_rotation = current_time - last_rotation

        if time_since_rotation >= rotate_interval:
            log.info(f"Rotating Tor circuits (interval: {PROXY_ROTATE_INTERVAL}).")
            for instance in privoxy_instances:
                instance.rotate_circuits()
            last_rotation = current_time
            log.info("Rotation complete.")
        else:
            remaining = rotate_interval - time_since_rotation
            log.debug(f"Next rotation in {remaining:.0f} seconds.")

        # Sleep until next health check
        log.info(f"Sleeping for {PROXY_CHECK_INTERVAL}.")
        time.sleep(check_interval)


try:
    main()
except KeyboardInterrupt:
    try:
        sys.exit(0)
    except SystemExit:
        os._exit(0)
