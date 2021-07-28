# Rotating Tor Proxy

## HAProxy

HAProxy exposes a SOCKS proxy.
## Environment Variables

- `TORS` — Number of Tor instances
- `HAPROXY_LOGIN` — Username for HAProxy
- `HAPROXY_PASSWORD` — Password for HAProxy

## Ports

- 1080 — HAProxy port
- 2090 — HAProxy statistics port
- 8888 — Privoxy port
