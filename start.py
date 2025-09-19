#!/usr/bin/env python3

import os
import sys
import re
import time
import subprocess

from config import *
from proxy import log, Privoxy

PROXY_LIST_TXT = "proxy-list.txt"
PROXY_LIST_PY = "proxy-list.py"

HEADS = int(os.environ.get("HEADS", 1))
PROXY_CHECK_INTERVAL = int(os.environ.get("PROXY_CHECK_INTERVAL", 15)) # In minutes
TORS = int(os.environ.get("TORS", 5))

def get_versions():
    for cmd in ["privoxy --version", "haproxy -v", "tor --version"]:
        result = subprocess.run(cmd.split(), stdout=subprocess.PIPE)

        version = result.stdout.decode("utf-8").partition("\n")[0]
        version = re.sub(r" +([0-9/]{10})?[ -]*\(?(https://.*)?\)?\.?$", "", version)
        version = re.sub(r" version", ":", version)
        version = re.sub(r"\.$", "", version)

        log.info("- " + version)

def main():
    log.info("========================================")
    log.info(f"Medusa Proxy: {VERSION}")
    log.info("")
    get_versions()
    log.info("========================================")

    privoxy = [Privoxy(TORS, i) for i in range(HEADS)]

    log.info("Writing proxy list.")
    with open(PROXY_LIST_TXT, "wt") as file:
        for http in privoxy:
            file.write("http://127.0.0.1:%d\n" % http.port)
    log.info("Done.")

    log.info("Serving proxy list.")
    os.spawnl(os.P_NOWAIT, os.curdir + os.sep + PROXY_LIST_PY, PROXY_LIST_PY)

    while True:
        for i in range(HEADS):
            log.info("Testing proxies.")
            for http in privoxy:
                log.info(f"* Privoxy {http.id}")
                socks = http.haproxy
                for proxy in socks.proxies:
                    if not proxy.working:
                        log.warning("Restarting.")
                        proxy.restart()
            log.info("Sleeping.")
            time.sleep(PROXY_CHECK_INTERVAL * 60)
        for http in privoxy:
            http.cycle()

try:
    main()
except KeyboardInterrupt:
    try:
        sys.exit(0)
    except SystemExit:
        os._exit(0)
