from table import genericName,genericStat
from Logger import logger
import psycopg2

from schemaname import SchemaName

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


    def discover_schemas(self):
	if not self.get_self_db_conn():
	    return
	cur=self.prod_conn.cursor()
	try:
	    cur.execute("SELECT oid,nspname FROM pg_namespace WHERE nspname NOT IN ('pg_catalog', 'information_schema') AND nspname !~ '^pg_toast' AND nspname !~ '^pg_temp'")
	except Exception as e:
	    logger.error("Canot get schema info for database {0}".format(self.db_fields['db_name']))
	    cur.close()
	    return
	prod_schs=cur.fetchall()
	cur.close()
	self.cursor.execute("SELECT obj_oid,sch_name,id FROM schema_name WHERE dn_id={0} AND alive".format(self.id))
	local_schs=self.cursor.fetchall()
	for l_sch in local_schs:
	    for p_sch in prod_schs:
		if l_sch[0]==p_sch[0] and l_sch[1]==p_sch[1]:
		    break
	    else:
		logger.info("Retired schema {0} in database {1}".format(l_sch[1],self.db_fields['db_name']))
		old.sch=SchemaName(l_sch[2])
		old_sch.retire()
	for p_sch in prod_schs:
	    for l_sch in local_schs:
		if l_sch[0]==p_sch[0] and l_sch[1]==p_sch[1]:
		    break
	    else:
		logger.info("Create new schema {0} in database {1}".format(p_sch[1],self.db_fields['db_name']))
		new_sch=SchemaName()
		new_sch.set_fields(dn=self.id,obj_oid=p_sch[0],sch_name=p_sch[1])
		new_sch.create()
		new_sch.truncate()
