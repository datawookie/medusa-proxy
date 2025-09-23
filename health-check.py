#!/usr/bin/env python3

import json
import requests
import sys

PROXY = "socks5h://127.0.0.1:1080"
TIMEOUT = 5  # secndss
URL = "https://check.torproject.org/api/ip"


def check_tor_connection():
    try:
        response = requests.get(URL, proxies={"https": PROXY}, timeout=TIMEOUT)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"Request failed due to: {e}", file=sys.stderr)
        return None


def main():
    body = check_tor_connection()
    if body and isinstance(body, dict) and body.get("IsTor"):
        sys.exit(0)
    sys.exit(1)


if __name__ == "__main__":
    main()
