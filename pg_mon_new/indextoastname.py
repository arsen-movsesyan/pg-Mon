import table
import settings

logger=settings.logger

class IndexToastName(table.genericName):

    def __init__(self,in_db_conn,in_prod_dsn,in_id=None):
	super(IndexToastName,self).__init__(in_db_conn,in_id)
	self.table='index_toast_name'
	if in_id:
	    self._populate()
	    self.prod_dsn=in_prod_dsn
	    self.stat_obj=table.genericStat('index_toast_stat','tin_id',in_id)
	    self.stat_query="""SELECT
pg_relation_size(oid) AS tidx_size,
pg_stat_get_numscans(oid) AS tidx_scan,
pg_stat_get_tuples_returned(oid) AS tidx_tup_read,
pg_stat_get_tuples_fetched(oid) AS tidx_tup_fetch,
pg_stat_get_blocks_fetched(oid) AS tidx_blks_fetch,
pg_stat_get_blocks_hit(oid) AS tidx_blks_hit
FROM pg_class WHERE oid={0}""".format(self.db_fields['obj_oid'])

