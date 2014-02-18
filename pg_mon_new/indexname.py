import table
import settings

logger=settings.logger


class IndexName(table.genericName):

    def __init__(self,in_db_conn,in_prod_conn,in_id=None):
	super(IndexName,self).__init__(in_db_conn,in_id)
	self.table='index_name'
	self.prod_conn=in_prod_conn
	if in_id:
	    self._populate()
	    self.stat_obj=table.genericStat(self.db_conn,'index_stat','in_id',in_id)
	    self.stat_query="""SELECT
pg_relation_size(oid) AS idx_size,
pg_stat_get_numscans(oid) AS idx_scan,
pg_stat_get_tuples_returned(oid) AS idx_tup_read,
pg_stat_get_tuples_fetched(oid) AS idx_tup_fetch,
pg_stat_get_blocks_fetched(oid) AS idx_blks_fetch,
pg_stat_get_blocks_hit(oid) AS idx_blks_hit
FROM pg_class WHERE oid={0}""".format(self.db_fields['obj_oid'])

