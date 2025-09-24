#!/usr/bin/env python3

import requests
import sys

PROXY = "socks5h://127.0.0.1:1080"
URL = "https://check.torproject.org/api/ip"
# Timeout for the HTTP request to the Tor check service in seconds.
TIMEOUT = 5


def message(message: str, code: int | None = None) -> None:
    """
    Print a message without a trailing newline and exit with the given code.
    """
    print(message, end="")
    if code:
        sys.exit(code)

def check_tor_connection():
    try:
        response = requests.get(URL, proxies={"https": PROXY}, timeout=TIMEOUT)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        message(f"Request failed due to: {e}", file=sys.stderr)
        return None


def main():
    body = check_tor_connection()
    if body and isinstance(body, dict):
        if body.get("IsTor") is True:
            message(f"✅ Healthy: {body.get('IP')} is a Tor exit node", 0)
        else:
            message(f"⚠️ Unhealthy: {body.get('IP')} is NOT a Tor exit node", 1)
    else:
        message("⛔ Unhealthy: no response or invalid body", 1)


if __name__ == "__main__":
    main()
