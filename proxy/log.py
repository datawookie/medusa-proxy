from logging import *

from config import LOG_LEVEL

basicConfig(level=LOG_LEVEL, format="%(asctime)s [%(levelname)7s] %(message)s")
getLogger("urllib3").setLevel(WARNING)
