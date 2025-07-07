# Medusa Rotating Tor Proxy

<img src="medusa-banner.webp">

The Docker image is based on the following:

- Python — 3.13-alpine
- Privoxy — 3.0.34
- HAProxy — 2.8.11-01c1056
- Tor — 0.4.8.13

## HAProxy

[HAProxy](https://www.haproxy.com/) is a high availability load balancer and proxy server that spreads requests across multiple services.

Here we are using HAProxy to distribute requests across a selection of Tor instances.

HAProxy exposes a SOCKS proxy.

## Privoxy

Privoxy exposes an HTTP proxy.

## Environment Variables

- `HEADS` — Number of Privoxy instances (default: 1).
- `TORS` — Number of Tor instances (default: 5).
- `HAPROXY_LOGIN` — Username for HAProxy (default: "admin").
- `HAPROXY_PASSWORD` — Password for HAProxy (default: "admin").
- `TOR_BRIDGES` - Bridge multiline string with bridges records (default : "").
- `TOR_EXIT_NODES` - Tor exit nodes config (default : "" , for example `TOR_EXIT_NODES=ru` or `TOR_EXIT_NODES=ru,en`).

## Tor Bridges

Tor bridges are private entry points to the Tor network that are not publicly listed. They are special Tor relays that act like normal entry nodes but are not included in the public Tor directory. They are typically distributed privately or through controlled channels.

Why are they useful? They can help you to bypass censorship in countries or networks that block access to the public Tor network. They also make it harder for governments, ISPs, or firewalls to detect or block Tor usage.

In summary, Tor bridges allow users to access Tor anonymously when regular access is blocked or surveilled. More information can be found in the [Tor Manual](https://torproject.github.io/manual/bridges/).

To enable the bridges feature, you must specify one or more bridges as follows (in order of decreasing priority):

1. Create a `bridges.lst` file. See `sample-bridges.lst` for an example.
2. Specify the `TOR_BRIDGES` environment variable. If you're adding multiple bridges then simply separate them with commas. You can do this either by (i) setting an environment variable in your shell prior to executing `docker run`, (ii) using the `-e` argument with `docker run` or (iii) by setting it in the `docker-compose.yaml` file (see `sample-docker-compose.yaml`).

Notes:

1. If no bridges are configured then the Tor bridges feature will be disabled.
2. The bridges in the examples may not work. Get working bridges from the Tor Project's [BridgeDB](https://bridges.torproject.org/options).

## Ports

- 1080 — HAProxy port
- 2090 — HAProxy statistics port
- 8888 — Privoxy port

## Usage

```bash
# Build Docker image
docker build -t datawookie/medusa-proxy .

# Pull Docker image
docker pull datawookie/medusa-proxy:latest

# Start docker container
docker run --rm --name medusa-proxy -e TORS=3 -e HEADS=2 \
    -p 8888:8888 -p 8889:8889 \
    -p 1080:1080 -p 1081:1081 \
    -p 2090:2090 \
    datawookie/medusa-proxy

# Test SOCKS proxy
curl --socks5 localhost:1080 http://httpbin.org/ip

# Test HTTP proxy
curl --proxy localhost:8888 http://httpbin.org/ip

# Run Chromium through the proxy
chromium --proxy-server="http://localhost:8888" \
    --host-resolver-rules="MAP * 0.0.0.0 , EXCLUDE localhost"

# Access monitor
#
# auth login:admin
# auth pass:admin
#
http://localhost:2090 or http://admin:admin@localhost:2090
```
