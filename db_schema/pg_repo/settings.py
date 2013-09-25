TIME_ZONE = 'PST8PDT'
LANGUAGE_CODE = 'en-us'
APPLICATION_NAME= 'pg_repo'

DATABASE = {
    'db_handler_1': {
	'DBNAME': 'pg_mon',
	'USER': 'postgres',
	'PASSWORD': '',
	'HOST': 'localhost',
	'PORT': '5432',
	'SSLMODE': 'prefer',
    },
}

repo_file_name='repository'


##############################################
### !!! Do not modify below this point !!! ###
##############################################

get_last_applied_stmt="SELECT COALESCE(MAX(update_number),0) FROM db_update"
get_install_check_stmt="SELECT COUNT(1) FROM pg_class WHERE relname='db_update' AND relkind='r'"
install_stmt="""CREATE table db_update(
update_number integer NOT NULL PRIMARY KEY,
update_content text NOT NULL,
update_time timestamp with time zone NOT NULL DEFAULT now())"""

confirm_stmt="INSERT INTO db_update(update_number,update_content) VALUES (%s,%s)"


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
