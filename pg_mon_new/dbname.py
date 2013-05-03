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
	    self.prod_dsn=in_prod_dsn
	    self.stat_obj=table.genericStat('database_stat','dn_id',in_id)
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

    def get_conn_string(self):
	return self.prod.dsn




    def discover_schemas(self):
	if not self.prod_conn or self.prod_conn.closed:
	    if not self.set_prod_conn():
		return False

	cur=self.prod_conn.cursor()
	try:
	    cur.execute("SELECT oid,nspname FROM pg_namespace WHERE nspname NOT IN ('pg_catalog', 'information_schema') AND nspname !~ '^pg_toast' AND nspname !~ '^pg_temp'")
	except Exception as e:
	    logger.error("Canot execute schema discovery query on Prod {0}".format(e.pgerror))
	    cur.close()
	    return
	prod_schs=cur.fetchall()
	cur.close()
	cur=self.db_conn.cursor()
	try:
	    cur.execute("SELECT obj_oid,sch_name,id FROM schema_name WHERE dn_id={0} AND alive".format(self.id))
	except Exception as e:
	    logger.error("Canot execute schema discovery query on Local {0}".format(e.pgerror))
	    cur.close()
	    return
	local_schs=cur.fetchall()
	cur.close()
	for l_sch in local_schs:
	    for p_sch in prod_schs:
		if l_sch[0]==p_sch[0] and l_sch[1]==p_sch[1]:
		    break
	    else:
		old.sch=SchemaName(self.db_conn,self.prod_dsn,l_sch[2])
		old_sch.retire()
		logger.info("Retired schema {0} in database {1}".format(l_sch[1],self.db_fields['db_name']))
	for p_sch in prod_schs:
	    for l_sch in local_schs:
		if l_sch[0]==p_sch[0] and l_sch[1]==p_sch[1]:
		    break
	    else:
		new_sch=SchemaName(self.db_conn,self.prod_dsn)
		new_sch.set_fields(dn_id=self.id,obj_oid=p_sch[0],sch_name=p_sch[1])
		new_sch._create()
		logger.info("Create new schema {0} in database {1}".format(p_sch[1],self.db_fields['db_name']))
	self.db_conn.commit()
