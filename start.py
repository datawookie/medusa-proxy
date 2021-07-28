#!/usr/bin/env python3

import os, sys
import time
import atexit
import requests

import log

from service import Service
from tor import Tor
from haproxy import Haproxy
from privoxy import Privoxy

tors = int(os.environ.get('TORS', 5))

haproxy = Haproxy([Tor(i) for i in range(tors)])
privoxy = Privoxy(haproxy)

def shutdown():
    log.info("Shutting down.")
    for proxy in haproxy.proxies:
        proxy.stop()

def main():
    while True:
        log.info("Testing proxies.")

        for proxy in haproxy.proxies:
            log.info(f"Testing proxy (port {proxy.port}).")
            if not proxy.working:
                log.warning("Restarting.")
                proxy.restart()

        log.info("Sleeping.")
        time.sleep(60)

atexit.register(shutdown)

try:
    main()
except KeyboardInterrupt:
    shutdown()
    try:
        sys.exit(0)
    except SystemExit:
        os._exit(0)