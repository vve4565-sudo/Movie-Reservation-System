from logging import getLogger
from logging.config import dictConfig

from app.config.config import LOGGER_LEVEL, LOGGING_CONFIG

dictConfig(LOGGING_CONFIG)

lg = getLogger("app")

lg.setLevel(LOGGER_LEVEL.DEBUG)
