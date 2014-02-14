import table
import settings
from schemaname import SchemaName

logger=settings.logger


class DatabaseName(table.genericName):

    def __init__(self,in_db_conn,in_prod_dsn,in_id=None):
	super(DatabaseName,self).__init__(in_db_conn,in_id)
	self.table='database_name'
	if in_id:
	    self._populate()
	    self.set_prod_dsn(in_prod_dsn)
	    self.stat_obj=table.genericStat(self.db_conn,'database_stat','dn_id',in_id)
	    self.runtime_stat_obj=table.genericStat(self.db_conn,'db_runtime_stat','dn_id',in_id)
	    self.sub_table='schema_name'
	    self.sub_fk='dn_id'
	    self.stat_query="""SELECT
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
	    self.runtime_stat_query="""SELECT
COALESCE(MAX(current_timestamp-query_start),now()-now()) AS max_interval_query_dur,
COALESCE(AVG(current_timestamp-query_start),now()-now()) AS avg_interval_query_dur,
CAST(COALESCE(EXTRACT(epoch FROM MAX(current_timestamp-query_start)),0) AS INTEGER) AS max_sec_query_dur,
CAST(COALESCE(EXTRACT(epoch FROM AVG(current_timestamp-query_start)),0) AS INTEGER) AS avg_sec_query_dur,
MAX(age(datfrozenxid)) AS tx_max_age
FROM pg_stat_activity psa
JOIN pg_database pd ON psa.datid=pd.oid
WHERE pd.oid='{0}'""".format(self.db_fields['obj_oid'])


    def get_conn_string(self):
	return self.prod.dsn


    def discover_schemas(self):
	cur=self._get_p_cursor()
	if not cur:
	    logger.error("Return from DN discover_schemas. No p_cur obtained")
	    return False
	try:
	    cur.execute("SELECT oid,nspname FROM pg_namespace WHERE nspname NOT IN ('pg_catalog', 'information_schema') AND nspname !~ '^pg_toast' AND nspname !~ '^pg_temp'")
	except Exception as e:
	    logger.error("Canot execute schema discovery query on Prod {0}".format(e.pgerror))
	    cur.close()
	    self.prod_conn.close()
	    return False
	prod_schs=cur.fetchall()
	cur.close()
	cur=self.db_conn.cursor()
	try:
	    cur.execute("SELECT obj_oid,sch_name,id FROM schema_name WHERE dn_id={0} AND alive".format(self.id))
	except Exception as e:
	    logger.error("Canot execute schema discovery query on Local {0}".format(e.pgerror))
	    cur.close()
	    self.prod_conn.close()
	    return False
	local_schs=cur.fetchall()
	cur.close()
	for l_sch in local_schs:
	    for p_sch in prod_schs:
		if l_sch[0]==p_sch[0] and l_sch[1]==p_sch[1]:
		    old_sch=SchemaName(self.db_conn,self.prod_dsn,l_sch[2])
		    if not old_sch.discover_tables():
			logger.error("Returning from DN.discover_schemas() False from discover_tables for old")
			self.prod_conn.close()
			return False
		    if not old_sch.discover_functions():
			logger.error("Returning from DN.discover_schemas() False from discover_functions for old")
			self.prod_conn.close()
			return False
		    break
	    else:
		old_sch=SchemaName(self.db_conn,self.prod_dsn,l_sch[2])
		if old_sch.retire():
		    logger.info("Retired schema {0} in database {1}".format(l_sch[1],self.db_fields['db_name']))
		else:
		    logger.error("Return from DN.discover_schemas() Cannot retire old")
		    self.prod.conn.close()
		    return False
	for p_sch in prod_schs:
	    for l_sch in local_schs:
		if l_sch[0]==p_sch[0] and l_sch[1]==p_sch[1]:
		    break
	    else:
		new_sch=SchemaName(self.db_conn,self.prod_dsn)
		new_sch.set_fields(dn_id=self.id,obj_oid=p_sch[0],sch_name=p_sch[1])
		if new_sch._create():
		    new_sch.set_prod_dsn(self.prod_dsn)
		    if not new_sch.discover_tables():
			logger.error("Returning from DN.discover_schemas() False from discover_tables for new")
			self.prod_conn.close()
			return False
		    if not new_sch.discover_functions():
			logger.error("Returning from DN.discover_schemas() False from discover_functions for new")
			self.prod_conn.close()
			return False
		    logger.info("Create new schema {0} in database {1}".format(p_sch[1],self.db_fields['db_name']))
		else:
		    logger.error("Return from DN.discover_schemas() Cannot create new")
		    self.prod.conn.close()
		    return False
	return True


    def stat(self,in_time_id):
	if not super(DatabaseName,self).stat(in_time_id):
	    self.prod_conn.close()
	    logger.error("Return from DN.stat False from super.stat()")
	    return False
	sn_sets=self.get_dependants(True)
	if not sn_sets:
	    logger.error("Return from DN.stat No dependants returned")
	    self.prod_conn.close()
	    return False
	for sn_set in sn_sets:
	    sn=SchemaName(self.db_conn,self.prod_dsn,sn_set)
	    sn.stat(in_time_id)
	return True


    def runtime_stat(self,in_time_id):
	if not super(DatabaseName,self).runtime_stat(in_time_id):
	    logger.error("Return from DN.runtime_stat False from super.stat()")
	    self.prod_conn.close()
	    return False
	sn_sets=self.get_dependants(True)
	if not sn_sets:
	    logger.error("Return from DN.runtime_stat No dependants returned")
	    self.prod_conn.close()
	    return False
############################################
# TEST HERE!!!
#	for sn_set in sn_sets:
#	    logger.debug("!!! sn_set={0}".format(sn_set))
#	    sn=SchemaName(self.db_conn,self.prod_dsn,sn_set)
	return True

