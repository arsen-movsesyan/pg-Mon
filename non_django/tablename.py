from table import *
from Logger import logger
from indexname import IndexName
from tabletoastname import TableToastName

class TableName(genericName):
    table='table_name'
    sub_table='index_name'
    sub_fk='tn_id'
    toast_id=None

    def __init__(self,id=None):
	if id:
	    super(TableName,self).__init__(id)
	else:
	    super(TableName,self).__init__()
	self.stat_obj.set_fk_field('tn_id')
	self.stat_obj.set_table_name('table_stat')


    def stat(self,time_id,prod_cursor):
	sql_stat="""SELECT
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
	self.create_stat(time_id,sql_stat,prod_cursor)


    def va_stat(self,time_id,prod_cursor):
	va_stat=genericStat()
	va_stat.set_fk_field('tn_id')
	va_stat.set_table_name('table_va_stat')
	va_stat.set_fk_value(self.id)
	va_stat.set_time_id(time_id)
	va_stat_q="""SELECT
pg_stat_get_last_vacuum_time(oid) AS last_vacuum,
pg_stat_get_last_autovacuum_time(oid) AS last_autovacuum,
pg_stat_get_last_analyze_time(oid) AS last_analyze,
pg_stat_get_last_autoanalyze_time(oid) AS last_autoanalyze
FROM pg_class WHERE oid={0}""".format(self.db_fields['obj_oid'])
	try:
	    prod_cursor.execute(va_stat_q)
	except Exception, e:
	    logger.warning("Details: {0},{1}".format(e.pgcode,e.pgerror))
	    return
	result=prod_cursor.fetchone()
	desc=prod_cursor.description
	va_stat.set_field_dict(zip_field_names(result,desc))
	va_stat.create()
	va_stat.truncate()


    def discover_indexes(self,prod_cursor):
	self.cursor.execute("SELECT obj_oid,idx_name,id FROM index_name WHERE tn_id={0} AND alive".format(self.id))
	local_idxs=self.cursor.fetchall()
	try:
	    prod_cursor.execute("""SELECT i.indexrelid,c.relname,i.indisunique,i.indisprimary
FROM pg_index i
JOIN pg_class c ON i.indexrelid=c.oid
WHERE i.indrelid={0}""".format(self.db_fields['obj_oid']))
	except Exception as e:
	    logger.error("Cannot execute index discovery query: {0},{1}".format(e.pgcode,e.pgerror))
	    return
	prod_idxs=prod_cursor.fetchall()
	for l_idx in local_idxs:
	    for p_idx in prod_idxs:
		if l_idx[0]==p_idx[0] and l_idx[1]==p_idx[1]:
		    break
	    else:
		logger.info("Retired index {0} in table {1}".format(l_idx[1],self.db_fields['tbl_name']))
		old_idx=IndexName(l_idx[2])
		old_idx.retire()
	for p_idx in prod_idxs:
	    for l_idx in local_idxs:
		if l_idx[0]==p_idx[0] and l_idx[1]==p_idx[1]:
		    break
	    else:
		logger.info("Create new index {0} in table {1}".format(p_idx[1],self.db_fields['tbl_name']))
		new_index=IndexName()
		new_index.set_fields(tn_id=self.id,obj_oid=p_idx[0],idx_name=p_idx[1],is_unique=p_idx[2],is_primary=p_idx[3])
		new_index.create()
		new_index.truncate()


    def discover_toast(self,prod_cursor):
	self.cursor.execute("SELECT obj_oid,ttbl_name,id FROM table_toast_name WHERE tn_id={0} AND alive".format(self.id))
	local_ttbl=self.cursor.fetchone()
	try:
	    prod_cursor.execute("""SELECT r.reltoastrelid,t.relname
FROM pg_class r
INNER JOIN pg_class t ON r.reltoastrelid=t.oid
WHERE r.relkind='r'
AND t.relkind='t'
AND r.oid={0}""".format(self.db_fields['obj_oid']))
	except Exception as e:
	    logger.error("Cannot execute toast table discovery query: {0},{1}".format(e.pgcode,e.pgerror))
	    return
	prod_ttbl=prod_cursor.fetchone()
	if local_ttbl and prod_ttbl:
	    if not (local_ttbl[0] == prod_ttbl[0] and local_ttbl[1] == prod_ttbl[1]):
		logger.info("Retired TOAST table {0} for table {1}".format(local_ttbl[1],self.db_fields['tbl_name']))
		old_ttbl=TableToastName(local_ttbl[2])
		old_ttbl.retire()
		logger.info("Create new TOAST table {0} in table {1}".format(prod_ttbl[1],self.db_fields['tbl_name']))
		new_ttbl=TableToastName()
		new_ttbl.set_fields(tn_id=self.id,obj_oid=prod_ttbl[0],ttbl_name=prod_ttbl[1])
		new_ttbl.create()
		self.toast_id=local_ttbl[2]
		new_ttbl.truncate()
	elif local_ttbl and not prod_ttbl:
	    self.toast_id=None
	    logger.info("Retired TOAST table {0} for table {1}".format(local_ttbl[1],self.db_fields['tbl_name']))
	    old_ttbl=TableToastName(local_ttbl[2])
	    old_ttbl.retire()
	elif not local_ttbl and prod_ttbl:
	    logger.info("Create new TOAST table {0} in table {1}".format(prod_ttbl[1],self.db_fields['tbl_name']))
	    new_ttbl=TableToastName()
	    new_ttbl.set_fields(tn_id=self.id,obj_oid=prod_ttbl[0],ttbl_name=prod_ttbl[1])
	    new_ttbl.create()
	    self.toast_id=new_ttbl.get_id()
	    new_ttbl.truncate()


    def get_toast_id(self):
	if not self.toast_id:
	    self.cursor.execute("SELECT id FROM table_toast_name WHERE tn_id={0} AND alive".format(self.id))
	    local_ttbl=self.cursor.fetchone()
	    if local_ttbl:
		self.toast_id=local_ttbl[0]
	return self.toast_id
