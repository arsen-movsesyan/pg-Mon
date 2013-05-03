import table
import settings

from indexname import IndexName
from tabletoastname import TableToastName

logger=settings.logger


class TableName(table.genericName):

    def __init__(self,in_db_conn,in_prod_dsn,in_id=None):
	super(TableName,self).__init__(in_db_conn,in_id)
	self.table='table_name'
	self.toast_id=None
	if in_id:
	    self._populate()
	    self.prod_dsn=in_prod_dsn
	    self.sub_table='index_name'
	    self.sub_fk='tn_id'
	    self.stat_obj=table.genericStat('table_stat','tn_id',in_id)
	    self.va_stat_obj=table.genericStat('table_va_stat','tn_id',in_id)
	    self.stat_query="""SELECT
pg_relation_size(oid) AS tbl_size,
reltuples::bigint AS tbl_tuples,
pg_stat_get_numscans(oid) AS seq_scan,
pg_stat_get_tuples_returned(oid) AS seq_tup_read,
pg_stat_get_tuples_fetched(oid) AS seq_tup_fetch,
pg_stat_get_tuples_inserted(oid) AS n_tup_ins,
pg_stat_get_tuples_updated(oid) AS n_tup_upd,
pg_stat_get_tuples_deleted(oid) AS n_tup_del,
pg_stat_get_tuples_hot_updated(oid) AS n_tup_hot_upd,
pg_stat_get_live_tuples(oid) AS n_live_tup,
pg_stat_get_dead_tuples(oid) AS n_dead_tup,
pg_stat_get_blocks_fetched(oid) AS heap_blks_fetch,
pg_stat_get_blocks_hit(oid) AS heap_blks_hit
FROM pg_class
WHERE oid={0}""".format(self.db_fields['obj_oid'])
	    self.va_stat_query="""SELECT
pg_stat_get_last_vacuum_time(oid) AS last_vacuum,
pg_stat_get_last_autovacuum_time(oid) AS last_autovacuum,
pg_stat_get_last_analyze_time(oid) AS last_analyze,
pg_stat_get_last_autoanalyze_time(oid) AS last_autoanalyze
FROM pg_class WHERE oid={0}""".format(self.db_fields['obj_oid'])



    def va_stat(self,in_time_id):
	if not self.prod_conn or self.prod_conn.closed:
	    if not self.set_prod_conn():
		return False
	cur=self.prod_conn.cursor()
	try:
	    cur.execute(self.va_stat_query)
	except Exception as e:
	    logger.error("Canot get statistic info: {0}".format(e.pgerror))
	    return
	self.va_stat_obj.set_field_dict(table.zip_field_names(cur.fetchone(),cur.description))
	self.va_stat_obj.set_field('time_id',in_time_id)
	cur.close()
	if self.va_stat_obj._create(self.db_conn.cursor()):
	    self.db_conn.commit()



    def discover_indexes(self):
	if not self.prod_conn or self.prod_conn.closed:
	    if not self.set_prod_conn():
		return False
	cur=self.prod_conn.cursor()
	try:
	    cur.execute("""SELECT i.indexrelid,c.relname,i.indisunique,i.indisprimary
FROM pg_index i
JOIN pg_class c ON i.indexrelid=c.oid
WHERE i.indrelid={0}""".format(self.db_fields['obj_oid']))
	except Exception as e:
	    logger.error("Canot execute index discovery query on Prod: {0}".format(e.pgerror))
	    return
	prod_idxs=cur.fetchall()
	cur.close()
	cur=self.db_conn.cursor()
	try:
	    cur.execute("SELECT obj_oid,idx_name,id FROM index_name WHERE tn_id={0} AND alive".format(self.id))
	except Exception as e:
	    logger.error("Canot execute index discovery query on Local: {0}".format(e.pgerror))
	    return
	local_idxs=cur.fetchall()
	cur.close()
	for l_idx in local_idxs:
	    for p_idx in prod_idxs:
		if l_idx[0]==p_idx[0] and l_idx[1]==p_idx[1]:
		    break
	    else:
		logger.info("Retired index {0} in table {1}".format(l_idx[1],self.db_fields['tbl_name']))
		old_idx=IndexName(self.db_conn,self.prod_dsn,l_idx[2])
		old_idx.retire()
	for p_idx in prod_idxs:
	    for l_idx in local_idxs:
		if l_idx[0]==p_idx[0] and l_idx[1]==p_idx[1]:
		    break
	    else:
		new_index=IndexName(self.db_conn,self.prod_dsn)
		new_index.set_fields(tn_id=self.id,obj_oid=p_idx[0],idx_name=p_idx[1],is_unique=p_idx[2],is_primary=p_idx[3])
		new_index._create()
		logger.info("Create new index {0} in table {1}".format(p_idx[1],self.db_fields['tbl_name']))
	self.db_conn.commit()


    def discover_toast(self):
	if not self.prod_conn or self.prod_conn.closed:
	    if not self.set_prod_conn():
		return False
	cur=self.prod_conn.cursor()
	try:
	    cur.execute("""SELECT r.reltoastrelid,t.relname
FROM pg_class r
INNER JOIN pg_class t ON r.reltoastrelid=t.oid
WHERE r.relkind='r'
AND t.relkind='t'
AND r.oid={0}""".format(self.db_fields['obj_oid']))
	except Exception as e:
	    logger.error("Canot execute toast discovery query on Prod: {0}".format(e.pgerror))
	    return
	prod_ttbl=cur.fetchone()
	cur.close()
	cur=self.db_conn.cursor()
	try:
	    cur.execute("SELECT obj_oid,ttbl_name,id FROM table_toast_name WHERE tn_id={0} AND alive".format(self.id))
	except Exception as e:
	    logger.error("Canot execute toast discovery query on Local: {0}".format(e.pgerror))
	    return
	local_ttbl=cur.fetchone()
	cur.close()
	if local_ttbl and prod_ttbl:
	    if not (local_ttbl[0] == prod_ttbl[0] and local_ttbl[1] == prod_ttbl[1]):
		logger.info("Retired TOAST table {0} for table {1}".format(local_ttbl[1],self.db_fields['tbl_name']))
		old_ttbl=TableToastName(self.db_conn,self.prod_dsn,local_ttbl[2])
		old_ttbl.retire()
		logger.info("Create new TOAST table {0} in table {1}".format(prod_ttbl[1],self.db_fields['tbl_name']))
		new_ttbl=TableToastName(self.db_conn,self.prod_dsn)
		new_ttbl.set_fields(tn_id=self.id,obj_oid=prod_ttbl[0],ttbl_name=prod_ttbl[1])
		new_ttbl._create()
		self.toast_id=local_ttbl[2]
	elif local_ttbl and not prod_ttbl:
	    self.toast_id=None
	    logger.info("Retired TOAST table {0} for table {1}".format(local_ttbl[1],self.db_fields['tbl_name']))
	    old_ttbl=TableToastName(self.db_conn,self.prod_dsn,local_ttbl[2])
	    old_ttbl.retire()
	elif not local_ttbl and prod_ttbl:
	    logger.info("Create new TOAST table {0} in table {1}".format(prod_ttbl[1],self.db_fields['tbl_name']))
	    new_ttbl=TableToastName(self.db_conn,self.prod_dsn)
	    new_ttbl.set_fields(tn_id=self.id,obj_oid=prod_ttbl[0],ttbl_name=prod_ttbl[1])
	    new_ttbl._create()
	    self.toast_id=new_ttbl.get_id()
	self.db_conn.commit()



    def get_toast_id(self):
	if not self.toast_id:
	    cur=self.db_conn.cursor()
	    try:
		cur.execute("SELECT id FROM table_toast_name WHERE tn_id={0} AND alive".format(self.id))
	    except Exception as e:
		logger.error("Canot get toast ID: {0}".format(e.pgerror))
		return
	    local_ttbl=cur.fetchone()
	    cur.close()
	    if local_ttbl:
		self.toast_id=local_ttbl[0]
	return self.toast_id
