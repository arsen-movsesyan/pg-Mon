import logging
import psycopg2
import logging.config
from os import getcwd
from time import timezone

from uuid import uuid1
from socket import gethostname



def get_my_mac():
    my_uuid=uuid1()
    mac_addr="{0:0>12}".format(hex(my_uuid.node)[2:-1])
    return mac_addr[:2] + ":" + ":".join([mac_addr[i] + mac_addr[i+1] for i in range(2,12,2)])



DATABASE = {
    'db_mon': {
	'DBNAME': 'db_mon',
	'USER': 'postgres',
	'PASSWORD': '',
	'HOST': '127.0.0.1',
	'PORT': '5432',
	'SSLMODE': 'prefer',
    },
    'lms': {
	'DBNAME': 'lms_db',
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
	    'filename': 'db_mon.log',
	    'mode': 'a',
	    'maxBytes': 1048576,
	    'backupCount': 5,
	},
    },
    'loggers': {
	'dbmon_logger': {
	    'handlers': ['main_file_handler'],
	    'level': 'ERROR',
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

db_handler=psycopg2.connect(custom_dsn('db_mon'))

prod_handler=psycopg2.connect(custom_dsn('lms'))

db_handler.autocommit=True

BUFF_FILE=getcwd()+'/tmp/trans_temp_bin'
READY_FILE=getcwd()+'/ready/trans_ready_bin'

MAX_KEEP_READY_FILES=20

TRANS_TEMPLATE=dict(
    header=dict(
	product_name='MAS',
	product_model='FireEye 4310',
	host_name=gethostname(),
	transfer_timestamp=None,
	host_timezone=timezone,
	host_id=get_my_mac(),
    ),
#    crc_checksum=0,
    basic=dict(
	os_info=None,
	soft_release=None,
	license_info=None,
    ),
    stat_content=dict(
	db_stat=dict(
	    counter=0,
	),
	jabe_stat=None,
	bott_stat=None,
	network_stat=dict(
	    interface_stat=None,
	    net_proto_stat=None,
	),
	cpu_stat=None,
    ),
    config=dict(
	security_cfg=None,
	db_cfg=None,
    ),
    custom=dict(
	counter=0,
    ),
)

