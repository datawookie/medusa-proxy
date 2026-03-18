import os
from datetime import timedelta

VERSION = "0.3.2"

# ============================================================================
# Time Parsing Utilities
# ============================================================================


def parse_time_interval(
    time_str: str, default: timedelta = timedelta(minutes=15)
) -> timedelta:
    """
    Parse time interval string into timedelta.

    Supported formats:
    - "30s" -> 30 seconds
    - "15m" -> 15 minutes
    - "1h"  -> 1 hour

    Args:
        time_str: Time string to parse
        default: Default value if parsing fails

    Returns:
        timedelta object
    """
    if not time_str:
        return default

    try:
        value = int(time_str[:-1])
        unit = time_str[-1].lower()

        if unit == "s":
            return timedelta(seconds=value)
        elif unit == "m":
            return timedelta(minutes=value)
        elif unit == "h":
            return timedelta(hours=value)
    except (ValueError, IndexError):
        pass

    return default


# ============================================================================
# Environment Configuration
# ============================================================================

# Number of Privoxy instances (HTTP proxy endpoints)
HEADS = int(os.environ.get("HEADS", 1))

# Number of Tor instances per Privoxy
TORS = int(os.environ.get("TORS", 5))

# Health check interval - how often to check if Tor instances are working
PROXY_CHECK_INTERVAL = os.environ.get("PROXY_CHECK_INTERVAL", "15m")

# Rotation interval - how often to rotate Tor circuits (change exit nodes)
# Default: 1 hour (1h)
PROXY_ROTATE_INTERVAL = os.environ.get("PROXY_ROTATE_INTERVAL", "1h")

# Startup timeout - maximum time to wait for at least one Tor instance to become available
# Default: 2 minutes (2m)
PROXY_STARTUP_TIMEOUT = os.environ.get("PROXY_STARTUP_TIMEOUT", "2m")

# Tor exit node countries (comma-separated country codes)
TOR_EXIT_NODES = os.environ.get("TOR_EXIT_NODES", "")
