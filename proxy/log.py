from logging import INFO, WARNING, basicConfig, debug, getLogger, info, warning

LOG_LEVEL = INFO

__all__ = ["debug", "info", "warning"]

basicConfig(level=LOG_LEVEL, format="%(asctime)s [%(levelname)7s] %(message)s")
getLogger("urllib3").setLevel(WARNING)
