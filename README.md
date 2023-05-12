# Rotating Tor Proxy

## HAProxy

[HAProxy](https://www.haproxy.com/) is a high availability load balancer and proxy server that spreads requests across multiple services.

Here we are using HAProxy to distribute requests across a selection of Tor instances.

HAProxy exposes a SOCKS proxy.

## Privoxy

Privoxy exposes an HTTP proxy.

## Environment Variables

- `HEADS` — Number of Privoxy instances (default: 1)
- `TORS` — Number of Tor instances (default: 5)
- `HAPROXY_LOGIN` — Username for HAProxy (default: "admin")
- `HAPROXY_PASSWORD` — Password for HAProxy (default: "admin")

## Ports

- 1080 — HAProxy port
- 2090 — HAProxy statistics port
- 8888 — Privoxy port

## Usage

```bash
# Build Docker image
docker build -t datawookie/tor-proxy-rotating .

# Pull Docker image
docker pull datawookie/tor-proxy-rotating:latest

# Start docker container
docker run --rm --name tor-proxy-rotating -e TORS=3 -e HEADS=2 \
    -p 8888:8888 -p 8889:8889 \
    -p 1080:1080 -p 1081:1081 \
    -p 2090:2090 \
    datawookie/tor-proxy-rotating

# Test SOCKS proxy
curl --socks5 localhost:5566 http://httpbin.org/ip

# Test HTTP proxy
curl --proxy localhost:8888 http://httpbin.org/ip

# Run Chromium through the proxy
chromium --proxy-server="http://localhost:8118" \
    --host-resolver-rules="MAP * 0.0.0.0 , EXCLUDE localhost"

# Access monitor
#
# auth login:admin
# auth pass:admin
#
http://localhost:2090 or http://admin:admin@localhost:2090
```
