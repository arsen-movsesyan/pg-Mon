import logging
import logging.config


APPLICATION_NAME= 'pg_mon'

DATABASE = {
    'pg_mon': {
	'DBNAME': 'pg_mon',
	'USER': 'postgres',
	'PASSWORD': '',
	'HOST': 'localhost',
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
	    'filename': 'pg_mon.log',
	    'mode': 'a',
	    'maxBytes': 1048576,
	    'backupCount': 5,
	},
    },
    'loggers': {
	'worker_logger': {
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

logging.config.dictConfig(LOGGING)

logger=logging.getLogger('worker_logger')

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
