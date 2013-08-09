from sys import exit
from table import genericName,genericStat,zip_field_names
from settings import logger,db_handler

class IndexName(genericName):

    def __init__(self,id=None):
	if id:
	    super(IndexName,self).__init__(id)
	else:
	    super(IndexName,self).__init__()
	self.table='index_name'
	self.stat_obj.set_fk_field('in_id')
	self.stat_obj.set_table_name('index_stat')
	if id:
	    self.populate()
	    self.stat_stmt="""SELECT
pg_relation_size(oid) AS idx_size,
pg_stat_get_numscans(oid) AS idx_scan,
pg_stat_get_tuples_returned(oid) AS idx_tup_read,
pg_stat_get_tuples_fetched(oid) AS idx_tup_fetch,
pg_stat_get_blocks_fetched(oid) AS idx_blks_fetch,
pg_stat_get_blocks_hit(oid) AS idx_blks_hit
FROM pg_class WHERE oid={0}""".format(self.db_fields['obj_oid'])



###################################################################################################################
###################################################################################################################
###################################################################################################################
###################################################################################################################


class IndexToastName(genericName):

    def __init__(self,id=None):
	if id:
	    super(IndexToastName,self).__init__(id)
	else:
	    super(IndexToastName,self).__init__()
	self.stat_obj.set_fk_field('tin_id')
	self.stat_obj.set_table_name('index_toast_stat')
	self.table='index_toast_name'
	if id:
	    self.populate()
	    self.stat_stmt="""SELECT
pg_relation_size(oid) AS tidx_size,
pg_stat_get_numscans(oid) AS tidx_scan,
pg_stat_get_tuples_returned(oid) AS tidx_tup_read,
pg_stat_get_tuples_fetched(oid) AS tidx_tup_fetch,
pg_stat_get_blocks_fetched(oid) AS tidx_blks_fetch,
pg_stat_get_blocks_hit(oid) AS tidx_blks_hit
FROM pg_class WHERE oid={0}""".format(self.db_fields['obj_oid'])




###################################################################################################################
###################################################################################################################
###################################################################################################################
###################################################################################################################


class TableToastName(genericName):

    def __init__(self,id=None):
	if id:
	    super(TableToastName,self).__init__(id)
	else:
	    super(TableToastName,self).__init__()
	self.table='table_toast_name'
	self.sub_table='index_toast_name'
	self.sub_fk='ttn_id'
	self.toast_idx_id=None
	self.stat_obj.set_fk_field('ttn_id')
	self.stat_obj.set_table_name('table_toast_stat')
	if id:
	    self.populate()
	    self.stat_stmt="""SELECT
pg_relation_size(oid) AS ttbl_size,
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



    def discover_index(self):
	self.self_cursor.execute("SELECT obj_oid,tidx_name,id FROM index_toast_name WHERE ttn_id={0} AND alive".format(self.id))
	l_idx=self.self_cursor.fetchone()
	try:
	    self.prod_cursor.execute("""SELECT i.oid,i.relname
FROM pg_class t
INNER JOIN pg_class i ON t.reltoastidxid=i.oid
WHERE t.relkind='t'
AND t.oid={0}""".format(self.db_fields['obj_oid']))
	except Exception as e:
	    logger.error("Cannot execute TOAST index discovery query: {0}".format(e.pgerror))
	    return
	p_idx=self.prod_cursor.fetchone()
	if l_idx and p_idx:
	    if not (l_idx[0]==p_idx[0] and l_idx[1]==p_idx[1]):
		logger.info("Retired TOAST index {0} for table {1}".format(l_idx[1],self.db_fields['ttbl_name']))
		old_tidx=IndexToastName(l_idx[2])
		old_tidx.retire()
		logger.info("Create new TOAST index {0} in table {1}".format(p_idx[1],self.db_fields['ttbl_name']))
		new_tidx=IndexToastName()
		new_tidx.set_fields(ttn_id=self.id,obj_oid=p_idx[0],tidx_name=p_idx[1])
		new_tidx.create()
		self.toast_idx_id=new_tidx.get_id()
		new_tidx.truncate()
	elif l_idx and not p_idx:
	    self.toast_idx_id=None
	    logger.info("Retired TOAST index {0} for table {1}".format(l_idx[1],self.db_fields['ttbl_name']))
	    old_tidx=IndexToastName(l_idx[2])
	    old_tidx.retire()
	elif not l_idx and p_idx:
	    logger.info("Create new TOAST index {0} in table {1}".format(p_idx[1],self.db_fields['ttbl_name']))
	    new_tidx=IndexToastName()
	    new_tidx.set_fields(ttn_id=self.id,obj_oid=p_idx[0],tidx_name=p_idx[1])
	    new_tidx.create()
	    self.toast_idx_id=new_tidx.get_id()
	    new_tidx.truncate()


    def get_tindex_id(self):
	if not self.toast_idx_id:
	    self.self_cursor.execute("SELECT id FROM index_toast_name WHERE ttn_id={0} AND alive".format(self.id))
	    l_idx_id=self.self_cursor.fetchone()
	    if l_idx_id:
		self.toast_idx_id=l_idx_id[0]
	return self.toast_idx_id



###################################################################################################################
###################################################################################################################
###################################################################################################################
###################################################################################################################



class TableName(genericName):

    def __init__(self,id=None):
	if id:
	    super(TableName,self).__init__(id)
	else:
	    super(TableName,self).__init__()
	self.stat_obj.set_fk_field('tn_id')
	self.stat_obj.set_table_name('table_stat')
	self.table='table_name'
	self.sub_table='index_name'
	self.sub_fk='tn_id'
	self.toast_id=None
	if id:
	    self.populate()
	    self.stat_stmt="""SELECT
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


    def va_stat(self,time_id):
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
	    self.prod_cursor.execute(va_stat_q)
	except Exception, e:
	    logger.warning("Details: {0}".format(e.pgerror))
	    return
	result=self.prod_cursor.fetchone()
	desc=self.prod_cursor.description
	va_stat.set_field_dict(zip_field_names(result,desc))
	va_stat.create()
	va_stat.truncate()


    def discover_indexes(self):
	self.self_cursor.execute("SELECT obj_oid,idx_name,id FROM index_name WHERE tn_id={0} AND alive".format(self.id))
	local_idxs=self.self_cursor.fetchall()
	try:
	    self.prod_cursor.execute("""SELECT i.indexrelid,c.relname,i.indisunique,i.indisprimary
FROM pg_index i
JOIN pg_class c ON i.indexrelid=c.oid
WHERE i.indrelid={0}""".format(self.db_fields['obj_oid']))
	except Exception as e:
	    logger.error("Cannot execute index discovery query: {0}".format(e.pgerror))
	    return
	prod_idxs=self.prod_cursor.fetchall()
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


    def discover_toast(self):
	self.self_cursor.execute("SELECT obj_oid,ttbl_name,id FROM table_toast_name WHERE tn_id={0} AND alive".format(self.id))
	local_ttbl=self.self_cursor.fetchone()
	try:
	    self.prod_cursor.execute("""SELECT r.reltoastrelid,t.relname
FROM pg_class r
INNER JOIN pg_class t ON r.reltoastrelid=t.oid
WHERE r.relkind='r'
AND t.relkind='t'
AND r.oid={0}""".format(self.db_fields['obj_oid']))
	except Exception as e:
	    logger.error("Cannot execute toast table discovery query: {0}".format(e.pgerror))
	    return
	prod_ttbl=self.prod_cursor.fetchone()
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
	    self.self_cursor.execute("SELECT id FROM table_toast_name WHERE tn_id={0} AND alive".format(self.id))
	    local_ttbl=self.self_cursor.fetchone()
	    if local_ttbl:
		self.toast_id=local_ttbl[0]
	return self.toast_id



###################################################################################################################
###################################################################################################################
###################################################################################################################
###################################################################################################################



class FunctionName(genericName):

    def __init__(self,id=None):
	if id:
	    super(FunctionName,self).__init__(id)
	else:
	    super(FunctionName,self).__init__()
	self.table='function_name'
	self.stat_obj.set_fk_field('fn_id')
	self.stat_obj.set_table_name('function_stat')
	if id:
	    self.populate()

#    def stat(self,time_id):
#	pass
#	sql_stat="""SELECT
#pg_relation_size(oid) AS relsize,
#reltuples::bigint,
#pg_stat_get_numscans(oid) AS seq_scan,
#pg_stat_get_tuples_returned(oid) AS seq_tup_read,
#pg_stat_get_tuples_fetched(oid) AS seq_tup_fetch,
#pg_stat_get_tuples_inserted(oid) AS n_tup_ins,
#pg_stat_get_tuples_updated(oid) AS n_tup_upd,
#pg_stat_get_tuples_deleted(oid) AS n_tup_del,
#pg_stat_get_tuples_hot_updated(oid) AS n_tup_hot_upd,
#pg_stat_get_live_tuples(oid) AS n_live_tup,
#pg_stat_get_dead_tuples(oid) AS n_dead_tup,
#pg_stat_get_blocks_fetched(oid) AS heap_blks_fetch,
#pg_stat_get_blocks_hit(oid) AS heap_blks_hit
#FROM pg_class
#WHERE oid={0}""".format(self.db_fields['obj_oid'])

#	self.create_stat(time_id,sql_stat,prod_cursor)
#	prod_cursor.close()




###################################################################################################################
###################################################################################################################
###################################################################################################################
###################################################################################################################


class SchemaName(genericName):

    def __init__(self):
	super(SchemaName,self).__init__(1)
	self.table='schema_name'
	self.sub_fk='sn_id'
	self.populate()


    def discover_tables(self):
	self.self_cursor.execute("SELECT obj_oid,tbl_name,id FROM table_name WHERE {0}={1} AND alive".format(self.sub_fk,self.id))
	local_tbls=self.self_cursor.fetchall()
	try:
	    self.prod_cursor.execute("""SELECT r.oid,r.relname,
CASE WHEN h.inhrelid IS NULL THEN 'f'::boolean ELSE 't'::boolean END AS has_parent
FROM pg_class r
LEFT JOIN pg_inherits h ON r.oid=h.inhrelid
WHERE r.relkind='r'
AND r.relnamespace=(SELECT oid FROM pg_namespace WHERE nspname='public')""")
	except Exception as e:
	    logger.error("Cannot execute tables discovery query: {0}".format(e.pgerror))
	    return
	prod_tbls=self.prod_cursor.fetchall()
	for l_table in local_tbls:
	    for p_table in prod_tbls:
		if l_table[0]==p_table[0] and l_table[1]==p_table[1]:
		    break
	    else:
		logger.info("Retired table {0} in schema {1}".format(l_table[1],self.db_fields['sch_name']))
		old_table=TableName(l_table[2])
#		old_table.populate()
		old_table.retire()
	for p_table in  prod_tbls:
	    for l_table in local_tbls:
		if p_table[0]==l_table[0] and p_table[1]==l_table[1]:
		    break
	    else:
		logger.info("Created new table: {0} in schema {1}".format(p_table[1],self.db_fields['sch_name']))
		new_table=TableName()
		new_table.set_fields(sn_id=self.id,tbl_name=p_table[1],obj_oid=p_table[0],has_parent=p_table[2])
		new_table.create()
		new_table.truncate()



    def discover_functions(self):
	self.self_cursor.execute("SELECT pro_oid,func_name,id FROM function_name WHERE {0}={1} AND alive".format(self.sub_fk,self.id))
	local_funcs=self.self_cursor.fetchall()
	try:
	    self.prod_cursor.execute("""SELECT p.oid AS pro_oid,p.proname AS funcname,p.proretset,t.typname,l.lanname
FROM pg_proc p
LEFT JOIN pg_namespace n ON n.oid = p.pronamespace
JOIN pg_type t ON p.prorettype=t.oid
JOIN pg_language l ON p.prolang=l.oid
WHERE (p.prolang <> (12)::oid)
AND n.oid=(SELECT oid FROM pg_namespace WHERE nspname='public')""")
	except Exception as e:
	    logger.error("Cannot execute function discovery query: {0}".format(e.pgerror))
	    return
	prod_funcs=self.prod_cursor.fetchall()
	for l_func in local_funcs:
	    for p_func in prod_funcs:
		if l_func[0]==p_func[0] and l_func[1]==p_func[1]:
		    break
	    else:
		logger.info("Retired function {0} in schema {1}".format(l_func[1],self.db_fields['sch_name']))
		old_func=FunctionName(l_func[2])
#		old_func.populate()
		old_func.retire()
	for p_func in  prod_funcs:
	    for l_func in local_funcs:
		if p_func[0]==l_func[0] and p_func[1]==l_func[1]:
		    break
	    else:
		logger.info("Created new function: {0} in schema {1}".format(p_func[1],self.db_fields['sch_name']))
		new_func=FunctionName()
		new_func.set_fields(sn_id=self.id,pro_oid=p_func[0],func_name=p_func[1],proretset=p_func[2],prorettype=p_func[3],prolang=p_func[4])
		new_func.create()
		new_func.truncate()



    def get_tables(self,alive=True):
	self.sub_table='table_name'
	return self.get_dependants(alive)

    def get_functions(self,alive=True):
	self.sub_table='function_name'
	return self.get_dependants(alive)



###################################################################################################################
###################################################################################################################
###################################################################################################################
###################################################################################################################


class DatabaseName(genericName):

    def __init__(self):
	super(DatabaseName,self).__init__(1)
	self.table='database_name'
	self.sub_table='schema_name'
	self.sub_fk='dn_id'

	self.stat_stmt="""SELECT
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
WHERE oid =(SELECT oid FROM pg_database WHERE datname='lms_db')"""

	self.stat_obj.set_fk_field('dn_id')
	self.stat_obj.set_table_name('database_stat')
	self.populate()



###################################################################################################################
###################################################################################################################
###################################################################################################################
###################################################################################################################


class HostCluster(genericName):

    def __init__(self):
	super(HostCluster,self).__init__(1)
	self.table='host_cluster'
	self.sub_fk='hc_id'
	self.sub_table='database_name'
	self.stat_stmt="""SELECT
pg_stat_get_bgwriter_timed_checkpoints() AS checkpoints_timed,
pg_stat_get_bgwriter_requested_checkpoints() AS checkpoints_req,
pg_stat_get_bgwriter_buf_written_checkpoints() AS buffers_checkpoint,
pg_stat_get_bgwriter_buf_written_clean() AS buffers_clean,
pg_stat_get_bgwriter_maxwritten_clean() AS maxwritten_clean,
pg_stat_get_buf_written_backend() AS buffers_backend,
pg_stat_get_buf_alloc() AS buffers_alloc"""

	self.stat_obj.set_fk_field('hc_id')
	self.stat_obj.set_table_name('bgwriter_stat')
	self.populate()



###################################################################################################################
###################################################################################################################
###################################################################################################################
###################################################################################################################



###################################################################################################
###################################################################################################

class LogTime():
    cursor=db_handler.cursor()

    def __init__(self):
	time_check_query="""SELECT CASE
    WHEN (SELECT TRUE FROM log_time WHERE hour_truncate=date_trunc('hour',now()))
	THEN NULl
    ELSE 
	LOCALTIMESTAMP END AS actual_time,date_trunc('hour',LOCALTIMESTAMP) AS hour_truncate"""
	self.cursor.execute(time_check_query)

	time_data=self.cursor.fetchone()
	if not time_data[0]:
	    logger.critical('Appropriate record for "{0}" already exists'.format(time_data[1]))
	    self.cursor.close()
	    db_handler.close()
	    exit()
	logger.debug('Log time obtained. Actual Time: {0}\tHour Truncate: {1}'.format(time_data[0],time_data[1]))
	self.actual_time=time_data[0]
	self.hour_truncate=time_data[1]
	self.cursor.execute("INSERT INTO log_time (hour_truncate,actual_time) VALUES ('{0}','{1}') RETURNING id".format(time_data[1],time_data[0]))
	self.id=self.cursor.fetchone()[0]
	db_handler.commit()


    def __del__(self):
#	if not self.cursor.closed:
	self.cursor.close()

    def get_id(self):
	return self.id


###################################################################################################

