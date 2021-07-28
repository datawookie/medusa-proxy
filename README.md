# Rotating Tor Proxy

## HAProxy

HAProxy exposes a SOCKS proxy.

## Privoxy

Privoxy exposes an HTTP proxy.
## Environment Variables

- `TORS` — Number of Tor instances (default: 5)
- `HAPROXY_LOGIN` — Username for HAProxy (default: "admin")
- `HAPROXY_PASSWORD` — Password for HAProxy (default: "admin")

## Ports

- 1080 — HAProxy port
- 2090 — HAProxy statistics port
- 8888 — Privoxy port
