import logging
import logging.config

from settings import LOGGING

logging.config.dictConfig(LOGGING)

logger=logging.getLogger('pg_mon_logger')

