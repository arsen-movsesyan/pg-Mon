import logging
import psycopg2
import logging.config
from os import getcwd

DATABASE = {
    'db_stat': {
	'DBNAME': 'db_stat',
	'USER': 'postgres',
	'PASSWORD': '',
	'HOST': '127.0.0.1',
	'PORT': '5432',
	'SSLMODE': 'prefer',
    },
}

TIME_ZONE = 'PST8PDT'
LANGUAGE_CODE = 'en-us'

LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'handlers': {
	'main_file_handler': {
	    'class': 'logging.handlers.RotatingFileHandler',
	    'level': 'DEBUG',
	    'formatter': 'simple',
	    'filename': 'db_stat.log',
	    'mode': 'a',
	    'maxBytes': 1048576,
	    'backupCount': 5,
	},
    },
    'loggers': {
	'dbmon_logger': {
	    'handlers': ['main_file_handler'],
	    'level': 'DEBUG',
	    'propagate': True,
	},
    },
    'formatters': {
	'simple': {
	    'format': '%(asctime)s - %(levelname)s - %(module)s| %(message)s'
	}
    }
}

def custom_dsn(db_handler):
    for handler in DATABASE:
	if handler == db_handler:
	    portion=DATABASE[handler]
	    dbname=portion['DBNAME']
	    host=portion['HOST']
	    port=portion['PORT']
	    user=portion['USER']
	    password=portion['PASSWORD']
	    sslmode=portion['SSLMODE']
	    return "host="+host+" dbname="+dbname+" port="+port+" user="+user+" password="+password+" sslmode="+sslmode

logging.config.dictConfig(LOGGING)


##################################################################################################
##################################################################################################

logger=logging.getLogger('dbmon_logger')

db_handler=psycopg2.connect(custom_dsn('db_stat'))

db_handler.autocommit=True

RECIEVE_DIR=getcwd()+'/upload/'

