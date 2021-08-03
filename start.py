#!/usr/bin/env python3

import os, sys
import time
import atexit

from proxy import log, Privoxy

NTOR = int(os.environ.get('NTOR', 5))
NPRIVOXY = int(os.environ.get('NPRIVOXY', 2))

privoxy = [Privoxy(NTOR, i) for i in range(NPRIVOXY)]

def shutdown():
    log.info("Shutting down.")
    # for proxy in haproxy.proxies:
    #     proxy.stop()

def main():
    while True:
        for i in range(3):
            log.info("Testing proxies.")
            for http in privoxy:
                log.info(f"* Privoxy {http.id}")
                socks = http.haproxy
                for proxy in socks.proxies:
                    if not proxy.working:
                        log.warning("Restarting.")
                        proxy.restart()

            log.info("Sleeping.")
            time.sleep(60)

        
        for http in privoxy:
            http.cycle()

atexit.register(shutdown)

try:
    main()
except KeyboardInterrupt:
    shutdown()
    try:
        sys.exit(0)
    except SystemExit:
        os._exit(0)