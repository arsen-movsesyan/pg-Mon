from table import *
from Logger import logger
from indextoastname import IndexToastName

class TableToastName(genericName):
    table='table_toast_name'
    sub_table='index_toast_name'
    sub_fk='ttn_id'
    toast_idx_id=None

    def __init__(self,id=None):
	if id:
	    super(TableToastName,self).__init__(id)
	else:
	    super(TableToastName,self).__init__()
	self.stat_obj.set_fk_field('ttn_id')
	self.stat_obj.set_table_name('table_toast_stat')


    def stat(self,time_id,prod_cursor):
	sql_stat="""SELECT
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
	self.create_stat(time_id,sql_stat,prod_cursor)



    def discover_index(self,prod_cursor):
	self.cursor.execute("SELECT obj_oid,tidx_name,id FROM index_toast_name WHERE ttn_id={0} AND alive".format(self.id))
	l_idx=self.cursor.fetchone()
	try:
	    prod_cursor.execute("""SELECT i.oid,i.relname
FROM pg_class t
INNER JOIN pg_class i ON t.reltoastidxid=i.oid
WHERE t.relkind='t'
AND t.oid={0}""".format(self.db_fields['obj_oid']))
	except Exception as e:
	    logger.error("Cannot execute TOAST index discovery query: {0},{1}".format(e.pgcode,e.pgerror))
	    return
	p_idx=prod_cursor.fetchone()
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
	    self.cursor.execute("SELECT id FROM index_toast_name WHERE ttn_id={0} AND alive".format(self.id))
	    l_idx_id=self.cursor.fetchone()
	    if l_idx_id:
		self.toast_idx_id=l_idx_id[0]
	return self.toast_idx_id
