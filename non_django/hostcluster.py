import psycopg2
from table import *
from Logger import logger

class HostCluster(genericName):
    table='host_cluster'
    prod_conn=None
    sub_table='database_name'
    sub_fk='hc_id'

    def __init__(self,id=None):
	if id:
	    super(HostCluster,self).__init__(id)
	else:
	    super(HostCluster,self).__init__()
	self.stat_obj.set_fk_field('hc_id')
	self.stat_obj.set_table_name('bgwriter_stat')

    def get_conn_string(self):
	self.cursor.execute("SELECT get_conn_string({0})".format(self.id))
	string=self.cursor.fetchone()
	return string[0]

    def get_self_db_conn(self):
	if not self.prod_conn:
	    try:
		self.prod_conn=psycopg2.connect(self.get_conn_string())
	    except Exception, e:
		logger.warning("Cannot connect to postgres: {0}".format(self.get_conn_string()))
		return False
#	    logger.debug('Connection to DB for host "{0}" obtained succsessfully'.format(self.db_fields['hostname']))
	    return True
	else:
	    return False


    def stat(self,time_id):
	if not self.get_self_db_conn():
	    return
	cur=self.prod_conn.cursor()
	sql_stat="""SELECT
pg_stat_get_bgwriter_timed_checkpoints() AS checkpoints_timed,
pg_stat_get_bgwriter_requested_checkpoints() AS checkpoints_req,
pg_stat_get_bgwriter_buf_written_checkpoints() AS buffers_checkpoint,
pg_stat_get_bgwriter_buf_written_clean() AS buffers_clean,
pg_stat_get_bgwriter_maxwritten_clean() AS maxwritten_clean,
pg_stat_get_buf_written_backend() AS buffers_backend,
pg_stat_get_buf_alloc() AS buffers_alloc"""
	self.create_stat(time_id,sql_stat,cur)
	cur.close()

    def __del__(self):
	if self.prod_conn:
	    if not self.prod_conn.closed:
		self.prod_conn.close()

