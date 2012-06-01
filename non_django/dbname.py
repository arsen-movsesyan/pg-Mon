from table import genericName,genericStat
from Logger import logger
import psycopg2


class DatabaseName(genericName):
    table='database_name'
    prod_conn=None
    sub_table='schema_name'
    sub_fk='dn_id'
    conn_string=None

    def __init__(self,id=None,conn_string=None):
	self.conn_string=conn_string
	if id:
	    if not conn_string:
		logger.error("No connection string provided for database id {0} during init".format(id))
	    else:
		super(DatabaseName,self).__init__(id)
		self.conn_string=conn_string
	else:
	    super(DatabaseName,self).__init__()
	self.stat_obj.set_fk_field('dn_id')
	self.stat_obj.set_table_name('database_stat')

#    def get_conn_string(self):
#	self.cursor.execute("SELECT get_conn_string({0},{1})".format(self.db_fields['hc_id'],self.id))
#	string=self.cursor.fetchone()
#	return string[0]

    def get_self_db_conn(self):
	if not self.prod_conn:
	    try:
		self.prod_conn=psycopg2.connect(self.conn_string)
	    except Exception, e:
		logger.warning("Cannot connect to postgres: {0}".format(self.get_conn_string()))
		logger.warning("Details: {0}".format(e))
		return False
#	    logger.debug('Connection to DB "{0}" obtained succsessfully'.format(self.db_fields['db_name']))
	    return True
	else:
	    return False

    def get_prod_cursor(self):
	if not self.prod_conn:
	    if self.get_self_db_conn():
		return self.prod_conn.cursor()
	    else:
		return None
	else:
	    return self.prod_conn.cursor()


    def stat(self,time_id):
	if not self.get_self_db_conn():
	    return
	cur=self.prod_conn.cursor()
	sql_stat="""SELECT
pg_database_size(oid) AS db_size,
pg_stat_get_db_xact_commit(oid) AS xact_commit,
pg_stat_get_db_xact_rollback(oid) AS xact_rollback,
pg_stat_get_db_blocks_fetched(oid) AS blks_fetch,
pg_stat_get_db_blocks_hit(oid) AS blks_hit,
pg_stat_get_db_tuples_returned(oid) AS tup_returned,
pg_stat_get_db_tuples_fetched(oid) AS tup_fetched,
pg_stat_get_db_tuples_inserted(oid) AS tup_inserted,
pg_stat_get_db_tuples_updated(oid) AS tup_updated,
pg_stat_get_db_tuples_deleted(oid) AS tup_deleted
FROM pg_database
WHERE oid ={0}""".format(self.db_fields['obj_oid'])
	self.create_stat(time_id,sql_stat,cur)
	cur.close()

    def __del__(self):
	if self.prod_conn:
	    if not self.prod_conn.closed:
		self.prod_conn.close()
