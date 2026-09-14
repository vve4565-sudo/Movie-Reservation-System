from logging import getLogger
from logging.config import dictConfig

from .config import config

dictConfig(config.LOGGING_CONFIG)

lg = getLogger("app")

lg.setLevel(config.LOGGER_LEVEL.DEBUG)
