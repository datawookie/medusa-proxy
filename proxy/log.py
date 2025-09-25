from logging import basicConfig, getLogger, INFO, WARNING, info, debug, warning

LOG_LEVEL = INFO

__all__ = ["info", "debug", "warning"]

basicConfig(level=LOG_LEVEL, format="%(asctime)s [%(levelname)7s] %(message)s")
getLogger("urllib3").setLevel(WARNING)
