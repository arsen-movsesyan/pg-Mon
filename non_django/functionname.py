from table import *
from Logger import logger

class FunctionName(genericName):
    table='function_name'
#    sub_table='database_name'
#    sub_fk='fn_id'

    def __init__(self,id=None):
	if id:
	    super(FunctionName,self).__init__(id)
	else:
	    super(FunctionName,self).__init__()
	self.stat_obj.set_fk_field('fn_id')
	self.stat_obj.set_table_name('function_stat')


    def stat(self,time_id,prod_cursor):
	pass
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

