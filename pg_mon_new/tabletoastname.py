import table
import settings

from indextoastname import IndexToastName

logger=settings.logger


class TableToastName(table.genericName):

    def __init__(self,in_db_conn,in_prod_dsn,in_id=None):
	super(TableToastName,self).__init__(in_db_conn,in_id)
	self.table='table_toast_name'
	self.toast_idx_id=None
	if in_id:
	    self._populate()
	    self.prod_dsn=in_prod_dsn
	    self.stat_obj=table.genericStat('table_toast_stat','ttn_id',in_id)
	    self.stat_query="""SELECT
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
	if not self.prod_conn or self.prod_conn.closed:
	    if not self.set_prod_conn():
		return False
	cur=self.prod_conn.cursor()
	try:
	    cur.execute("""SELECT i.oid,i.relname
FROM pg_class t
INNER JOIN pg_class i ON t.reltoastidxid=i.oid
WHERE t.relkind='t'
AND t.oid={0}""".format(self.db_fields['obj_oid']))
	except Exception as e:
	    logger.error("Canot execute toast index discovery query on Prod: {0}".format(e.pgerror))
	    return
	p_idx=cur.fetchone()
	cur.close()
	cur=self.db_conn.cursor()
	try:
	    cur.execute("SELECT obj_oid,tidx_name,id FROM index_toast_name WHERE ttn_id={0} AND alive".format(self.id))
	except Exception as e:
	    logger.error("Canot execute toast index discovery query on Local: {0}".format(e.pgerror))
	    return
	l_idx=cur.fetchone()
	cur.close()
	if l_idx and p_idx:
	    if not (l_idx[0]==p_idx[0] and l_idx[1]==p_idx[1]):
		logger.info("Retired TOAST index {0} for table {1}".format(l_idx[1],self.db_fields['ttbl_name']))
		old_tidx=IndexToastName(l_idx[2])
		old_tidx.retire()
		logger.info("Create new TOAST index {0} in table {1}".format(p_idx[1],self.db_fields['ttbl_name']))
		new_tidx=IndexToastName(self.db_conn,self.prod_dsn)
		new_tidx.set_fields(ttn_id=self.id,obj_oid=p_idx[0],tidx_name=p_idx[1])
		new_tidx._create()
		self.toast_idx_id=new_tidx.get_id()
	elif l_idx and not p_idx:
	    self.toast_idx_id=None
	    logger.info("Retired TOAST index {0} for table {1}".format(l_idx[1],self.db_fields['ttbl_name']))
	    old_tidx=IndexToastName(self.db_conn,self.prod_dsn,l_idx[2])
	    old_tidx.retire()
	elif not l_idx and p_idx:
	    logger.info("Create new TOAST index {0} in table {1}".format(p_idx[1],self.db_fields['ttbl_name']))
	    new_tidx=IndexToastName(self.db_conn,self.prod_dsn)
	    new_tidx.set_fields(ttn_id=self.id,obj_oid=p_idx[0],tidx_name=p_idx[1])
	    new_tidx._create()
	    self.toast_idx_id=new_tidx.get_id()
	self.db_conn.commit()


    def get_tindex_id(self):
	if not self.toast_idx_id:
	    cur=self.db_conn.cursor()
	    try:
		cur.execute("SELECT id FROM index_toast_name WHERE ttn_id={0} AND alive".format(self.id))
	    except Exception as e:
		logger.error("Canot toast index ID: {0}".format(e.pgerror))
		return
	    l_idx_id=cur.fetchone()
	    cur.close()
	    if l_idx_id:
		self.toast_idx_id=l_idx_id[0]
	return self.toast_idx_id
