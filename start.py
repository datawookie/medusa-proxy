#!/usr/bin/env python3

import os, sys
import time
import atexit

from proxy import log, Tor, Haproxy, Privoxy

tors = int(os.environ.get('TORS', 5))

haproxy = Haproxy([Tor(i) for i in range(tors)])
privoxy = Privoxy(haproxy)

def shutdown():
    log.info("Shutting down.")
    for proxy in haproxy.proxies:
        proxy.stop()

def main():
    while True:
        for i in range(3):
            log.info("Testing proxies.")
            for proxy in haproxy.proxies:
                if not proxy.working:
                    log.warning("Restarting.")
                    proxy.restart()

            log.info("Sleeping.")
            time.sleep(60)

        for proxy in haproxy.proxies:
            proxy.cycle()

atexit.register(shutdown)

try:
    main()
except KeyboardInterrupt:
    shutdown()
    try:
        sys.exit(0)
    except SystemExit:
        os._exit(0)