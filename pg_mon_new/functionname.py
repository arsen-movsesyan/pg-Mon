import table
import settings

logger=settings.logger


class FunctionName(table.genericName):
#    table='function_name'
#    sub_table='database_name'
#    sub_fk='fn_id'

    def __init__(self,in_db_conn,in_prod_dsn,in_id=None):
	super(FunctionName,self).__init__(in_db_conn,in_id)
	self.table='function_name'
	if in_id:
	    self._populate()
	    self.prod_dsn=in_prod_dsn
	    self.stat_obj=table.genericStat('function_stat','fn_id',in_id)
	    self.stat_query="""SELECT
pg_relation_size(oid) AS relsize,
reltuples::bigint,
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
WHERE oid={0}""".format(self.db_fields['pro_oid'])

