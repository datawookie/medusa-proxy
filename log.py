from logging import *

basicConfig(
  level=DEBUG,
  format='%(asctime)s [%(levelname)7s] %(message)s'
)
getLogger('urllib3').setLevel(WARNING)
