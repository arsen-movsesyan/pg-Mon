import table
import settings

from indexname import IndexName
from tabletoastname import TableToastName
from indextoastname import IndexToastName

logger=settings.logger


class TableName(table.genericName):

    def __init__(self,in_db_conn,in_prod_conn,in_id=None):
	super(TableName,self).__init__(in_db_conn,in_id)
	self.table='table_name'
	self.toast_id=None
	self.sub_table='index_name'
	self.sub_fk='tn_id'
	self.prod_conn=in_prod_conn
	if in_id:
	    self._populate()
	    self.stat_obj=table.genericStat(self.db_conn,'table_stat','tn_id',in_id)
	    self.va_stat_obj=table.genericStat(self.db_conn,'table_va_stat','tn_id',in_id)
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
	p_cur=self._get_p_cursor()
	if not p_cur:
	    logger.error("Return from TN.va_stat No p_cur obtained")
	    return False
	try:
	    p_cur.execute(self.va_stat_query)
	except Exception as e:
	    logger.error("Canot get statistic info: {0}".format(e.pgerror))
	    p_cur.close()
	    return False
	self.va_stat_obj.set_field_dict(table.zip_field_names(p_cur.fetchone(),p_cur.description))
	self.va_stat_obj.set_field('time_id',in_time_id)
	p_cur.close()
	if not self.va_stat_obj._create():
	    logger.error("TN.va_stat() False from va_stat.create")
	return True


    def stat(self,in_time_id):
	if not super(TableName,self).stat(in_time_id):
	    logger.error("Return from TN.stat False from super.stat()")
	    return False
	idx_sets=self.get_dependants(False)
	if not idx_sets:
	    logger.info("TN.stat no ids_sets returned. Maybe no indexes present. Tabe {0}".format(self.db_fields['tbl_name']))
	    return True
	else:
	    for idx_set in idx_sets:
		idn=IndexName(self.db_conn,self.prod_dsn,idx_set)
		idn.set_prod_conn(self.prod_conn)
		if not idn.stat(in_time_id):
		    logger.error("TN.stat False from idn.stat")
	ttn_id=self.get_toast_id()
	if ttn_id:
	    ttn=TableToastName(self.db_conn,self.prod_dsn,ttn_id)
	    ttn.set_prod_conn(self.prod_conn)
	    if not ttn.stat(in_time_id):
		logger.error("TN.stat False from ttn.stat")
	    tin_id=ttn.get_tindex_id()
	    tin=IndexToastName(self.db_conn,self.prod_dsn,tin_id)
	    tin.set_prod_conn(self.prod_conn)
	    if not tin.stat(in_time_id):
		logger.error("TN.stat False from tin.stat")
	return True



    def discover_indexes(self):
	p_cur=self._get_p_cursor()
	if not p_cur:
	    logger.error("Returning from TN.discover_indexes No p_cur obtained")
	    return False
	try:
	    p_cur.execute("""SELECT i.indexrelid,c.relname,i.indisunique,i.indisprimary
    FROM pg_index i
    JOIN pg_class c ON i.indexrelid=c.oid
    WHERE i.indrelid={0}""".format(self.db_fields['obj_oid']))
	except Exception as e:
	    logger.error("Canot execute index discovery query on Prod: {0}".format(e.pgerror))
	    p_cur.close()
	    return False
	prod_idxs=p_cur.fetchall()
	p_cur.close()
	cur=self._get_cursor()
	if not cur:
	    logger.error("Returning from TN.discover_toast No cur obtained")
	    return False
	try:
	    cur.execute("SELECT obj_oid,idx_name,id FROM index_name WHERE tn_id={0} AND alive".format(self.id))
	except Exception as e:
	    logger.error("Canot execute index discovery query on Local: {0}".format(e.pgerror))
	    self.prod_conn.close()
	    return False
	local_idxs=cur.fetchall()
	cur.close()
	for l_idx in local_idxs:
	    for p_idx in prod_idxs:
		if l_idx[0]==p_idx[0] and l_idx[1]==p_idx[1]:
		    break
	    else:
		logger.info("Retired index {0} in table {1}".format(l_idx[1],self.db_fields['tbl_name']))
		old_idx=IndexName(self.db_conn,self.prod_dsn,l_idx[2])
		if not old_idx.retire():
		    logger.error("TN.discover_indexes Cannot retire old")
	for p_idx in prod_idxs:
	    for l_idx in local_idxs:
		if l_idx[0]==p_idx[0] and l_idx[1]==p_idx[1]:
		    break
	    else:
		new_index=IndexName(self.db_conn,self.prod_dsn)
		new_index.set_fields(tn_id=self.id,obj_oid=p_idx[0],idx_name=p_idx[1],is_unique=p_idx[2],is_primary=p_idx[3])
		if not new_index._create():
		    logger.error("TN.discover_indexes Cannot create new")
		logger.info("Create new index {0} in table {1}".format(p_idx[1],self.db_fields['tbl_name']))
	return True


    def discover_toast(self):
	p_cur=self._get_p_cursor()
	if not p_cur:
	    logger.error("Returning from TN.discover_toast No p_cur obtained")
	    return False
	try:
	    p_cur.execute("""SELECT r.reltoastrelid,t.relname
    FROM pg_class r
    INNER JOIN pg_class t ON r.reltoastrelid=t.oid
    WHERE r.relkind='r'
    AND t.relkind='t'
    AND r.oid={0}""".format(self.db_fields['obj_oid']))
	except Exception as e:
	    logger.error("Canot execute toast discovery query on Prod: {0}".format(e.pgerror))
	    p_cur.close()
	    return False
	prod_ttbl=p_cur.fetchone()
	p_cur.close()
	cur=self._get_cursor()
	if not cur:
	    logger.error("Returning from TN.discover_toast No cur obtained")
	    return False
	try:
	    cur.execute("SELECT obj_oid,ttbl_name,id FROM table_toast_name WHERE tn_id={0} AND alive".format(self.id))
	except Exception as e:
	    logger.error("Canot execute toast discovery query on Local: {0}".format(e.pgerror))
	    cur.close()
	    return False
	local_ttbl=cur.fetchone()
	cur.close()
	if local_ttbl and prod_ttbl:
	    if not (local_ttbl[0] == prod_ttbl[0] and local_ttbl[1] == prod_ttbl[1]):
		logger.info("Retired TOAST table {0} for table {1}".format(local_ttbl[1],self.db_fields['tbl_name']))
		old_ttbl=TableToastName(self.db_conn,self.prod_conn,local_ttbl[2])
		if not old_ttbl.retire():
		    logger.error("TN.discover_toast Cannot retire old to create new")
		logger.info("Create new TOAST table {0} in table {1}".format(prod_ttbl[1],self.db_fields['tbl_name']))
		new_ttbl=TableToastName(self.db_conn,self.prod_conn)
		new_ttbl.set_fields(tn_id=self.id,obj_oid=prod_ttbl[0],ttbl_name=prod_ttbl[1])
		if not new_ttbl._create():
		    logger.error("TN.discover_toast Cannot create new after retire old")
		self.toast_id=local_ttbl[2]
		if not new_ttbl.discover_index():
		    logger.error("TTN.discover_toast False from discover_index for new after retire")
	elif local_ttbl and not prod_ttbl:
	    self.toast_id=None
	    logger.info("Retired TOAST table {0} for table {1}".format(local_ttbl[1],self.db_fields['tbl_name']))
	    old_ttbl=TableToastName(self.db_conn,self.prod_conn,local_ttbl[2])
	    if not old_ttbl.retire():
		logger.error("TN.discover_toast Cannot retire old")
	elif not local_ttbl and prod_ttbl:
	    logger.info("Create new TOAST table {0} in table {1}".format(prod_ttbl[1],self.db_fields['tbl_name']))
	    new_ttbl=TableToastName(self.db_conn,self.prod_conn)
	    new_ttbl.set_fields(tn_id=self.id,obj_oid=prod_ttbl[0],ttbl_name=prod_ttbl[1])
	    if not new_ttbl._create():
		logger.error("TN.discover_toast Cannot create new")
	    self.toast_id=new_ttbl.get_id()
	    if not new_ttbl.discover_index():
		logger.error("TTN.discover_toast False from discover_index for new")
	return True



    def get_toast_id(self):
	if not self.toast_id:
	    cur=self._get_cursor()
	    if not cur:
		logger.error("Returning from TN.get_toast_id. No cur obtained")
#		self.prod_conn.close()
		return -1
	    try:
		cur.execute("SELECT id FROM table_toast_name WHERE tn_id={0} AND alive".format(self.id))
	    except Exception as e:
		logger.error("Canot get toast ID: {0}".format(e.pgerror))
		cur.close()
#		self.prod_conn.close()
		return -1
	    local_ttbl=cur.fetchone()
	    cur.close()
	    if local_ttbl:
		self.toast_id=local_ttbl[0]
	return self.toast_id
