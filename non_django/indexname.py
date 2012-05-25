from table import *
from Logger import logger

class IndexName(genericName):
    table='index_name'

    def __init__(self,id=None):
	if id:
	    super(IndexName,self).__init__(id)
	else:
	    super(IndexName,self).__init__()
	self.stat_obj.set_fk_field('in_id')
	self.stat_obj.set_table_name('index_stat')


    def stat(self,time_id,prod_cursor):
	sql_stat="""SELECT
pg_relation_size(oid) AS idx_size,
pg_stat_get_numscans(oid) AS idx_scan,
pg_stat_get_tuples_returned(oid) AS idx_tup_read,
pg_stat_get_tuples_fetched(oid) AS idx_tup_fetch,
pg_stat_get_blocks_fetched(oid) AS idx_blks_fetch,
pg_stat_get_blocks_hit(oid) AS idx_blks_hit
FROM pg_class WHERE oid={0}""".format(self.db_fields['obj_oid'])
	self.create_stat(time_id,sql_stat,prod_cursor)

