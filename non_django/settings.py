APPLICATION_NAME= 'pg_mon'

DATABASE = {
    'DBNAME': 'pg_mon',
    'USER': 'postgres',
    'PASSWORD': '',
    'HOST': 'localhost',
    'PORT': '5432',
    'SSLMODE': 'prefer',
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
	'pg_mon_logger': {
	    'handlers': ['main_file_handler'],
	    'level': 'INFO',
	    'propagate': True,
	}
    },
    'formatters': {
	'simple': {
	    'format': '%(asctime)s - %(levelname)s - %(module)s| %(message)s'
	}
    }
}


##################################################################################################
##################################################################################################

