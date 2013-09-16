import psycopg2
from settings import logger,custom_dsn

###################################################################################################
###################################################################################################

class LogTimeMain(object):

    def __init__(self):
	self.reset_id()
#	self.actual_time=None
#	self.hour_truncate=None
	self.db_conn=None
	self.table_name=None
	self.truncate_unit=None


    def _query_for_id(self):
	time_check_query="""SELECT CASE
    WHEN (SELECT COUNT(1) FROM {0} WHERE {1}_truncate=(SELECT date_trunc('{1}',now())::timestamp without time zone)) > 0 
	THEN NULL
    ELSE 
	LOCALTIMESTAMP END AS actual_time,date_trunc('{1}',LOCALTIMESTAMP) AS {1}_truncate""".format(self.table_name,self.truncate_unit)

	if not self.db_conn:
	    self.db_conn=psycopg2.connect(custom_dsn('pg_mon'))

	cur=self.db_conn.cursor()

	cur.execute(time_check_query)
	time_data=cur.fetchone()
	if not time_data[0]:
	    logger.critical('Appropriate record for "{0}" already exists'.format(time_data[1]))
	    cur.close()
	    return False
#	logger.debug('Log time obtained. Actual Time: {0}\tHour Truncate: {1}'.format(time_data[0],time_data[1]))
#	self.actual_time=time_data[0]
#	self.hour_truncate=time_data[1]
	cur.execute("INSERT INTO {0} ({1}_truncate,actual_time) VALUES (%s,%s) RETURNING id".format(self.table_name,self.truncate_unit),(time_data[1],time_data[0]))
	self.id=cur.fetchone()[0]
	cur.close()
	return True

    def reset_id(self):
	self.id=None

    def get_id(self):
	if not self.id:
	    if not self._query_for_id():
		return False
	self.db_conn.commit()
	return self.id

    def __del__(self):
	if self.db_conn:
	    if not self.db_conn.closed:
		self.db_conn.close()

#    def lt_commit(self):
#	self.db_conn.commit()


    def _dbg_clean(self):
	if self.id:
	    if not self.db_conn:
		self.db_conn=psycopg2.connect(custom_dsn('pg_mon'))
	    cur=self.db_conn.cursor()
	    cur.execute("DELETE FROM {0} WHERE id=%s".format(self.table_name),(self.id,))
	    cur.close()
	    self.db_conn.commit()


###################################################################################################

