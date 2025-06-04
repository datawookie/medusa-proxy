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

- `HEADS` — Number of Privoxy instances (default: 1)
- `TORS` — Number of Tor instances (default: 5)
- `HAPROXY_LOGIN` — Username for HAProxy (default: "admin")
- `HAPROXY_PASSWORD` — Password for HAProxy (default: "admin")
- `TOR_USEBRIDGES` - Enable bridge feature for tor (default: 0)
- `TOR_BRIDGES` - Bridge multiline string with bridges records (default : "")
- `TOR_EXITNODES` - Tor exit nodes config (default : "" , for example `TOR_EXITNODES={ru}` or `TOR_EXITNODES={ru},{en}`)


Note: If `TOR_BRIDGES` is empty `TOR_USEBRIDGES` will always `0`

## Tor Bridges config

To enable the Bridges function, you must set the value `TOR_USEBRIDGES=1` and specify the bridges using one of the following variations (to reduce priority):
- in the `/templates/bridges.lst` file

example file content
```
Bridge obfs4 37.18.133.75:44821 D40DA77CA68F39666F77CE8BA6FF332BF8DB3F31 cert=B4yVW8heE83luCJt+oQN1kDB/j4kWkNx6mtOc9O6GhLAV8zJx0lfUI6zWO9UxUoV5PX/Zw iat-mode=0
Bridge obfs4 51.81.26.157:443 8A7322A463C051DB6DC35B1159F119FC3373BB06 cert=kp6Czj/f+McG9OKwltQ4kGb41mjj8Mzp3flpTG8/VK5zXtfnZ+DToe33fumyq7Yq7WnbGA iat-mode=0
```

- in the `TOR_BRIDGES` environment variable in the `docker` command call

example for docker run command
```bash
docker run --rm --name medusa-proxy -e TORS=3 -e HEADS=2 \
    -e TOR_USEBRIDGES=1
    -e TOR_BRIDGES="Bridge obfs4 37.18.133.75:44821 D40DA77CA68F39666F77CE8BA6FF332BF8DB3F31 cert=B4yVW8heE83luCJt+oQN1kDB/j4kWkNx6mtOc9O6GhLAV8zJx0lfUI6zWO9UxUoV5PX/Zw iat-mode=0,Bridge obfs4 51.81.26.157:443 8A7322A463C051DB6DC35B1159F119FC3373BB06 cert=kp6Czj/f+McG9OKwltQ4kGb41mjj8Mzp3flpTG8/VK5zXtfnZ+DToe33fumyq7Yq7WnbGA iat-mode=0"
    -p 8888:8888 -p 8889:8889 \
    -p 1080:1080 -p 1081:1081 \
    -p 2090:2090 \
    datawookie/medusa-proxy
```

- in the `TOR_BRIDGES` environment variable `.env` file

example for env file
```ini
TOR_USEBRIDGES=1
TOR_BRIDGES="Bridge obfs4 37.18.133.75:44821 D40DA77CA68F39666F77CE8BA6FF332BF8DB3F31 cert=B4yVW8heE83luCJt+oQN1kDB/j4kWkNx6mtOc9O6GhLAV8zJx0lfUI6zWO9UxUoV5PX/Zw iat-mode=0,
Bridge obfs4 51.81.26.157:443 8A7322A463C051DB6DC35B1159F119FC3373BB06 cert=kp6Czj/f+McG9OKwltQ4kGb41mjj8Mzp3flpTG8/VK5zXtfnZ+DToe33fumyq7Yq7WnbGA iat-mode=0"
```

if bridges setted in `/templates/bridges.lst` file, it will ignore `TOR_BRIDGES` environment variable.

if file is not exist it will use `TOR_BRIDGES` environment variable.

if `TOR_BRIDGES` environment variable is missing it wiall ignore `TOR_USEBRIDGES` environment variable and disable Bridges feature


[info about tor bridges](https://torproject.github.io/manual/bridges/)

get briges records on [torproject](https://bridges.torproject.org/options)

for example
```
obfs4 37.18.133.75:44821 D40DA77CA68F39666F77CE8BA6FF332BF8DB3F31 cert=B4yVW8heE83luCJt+oQN1kDB/j4kWkNx6mtOc9O6GhLAV8zJx0lfUI6zWO9UxUoV5PX/Zw iat-mode=0
obfs4 51.81.26.157:443 8A7322A463C051DB6DC35B1159F119FC3373BB06 cert=kp6Czj/f+McG9OKwltQ4kGb41mjj8Mzp3flpTG8/VK5zXtfnZ+DToe33fumyq7Yq7WnbGA iat-mode=0

```

### note:

Bridges in examples may not works, before start using you need get own bridges on [torproject](https://bridges.torproject.org/options)

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
