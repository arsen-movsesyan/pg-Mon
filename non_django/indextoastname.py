from table import *
from Logger import logger

class IndexToastName(genericName):
    table='index_toast_name'

    def __init__(self,id=None):
	if id:
	    super(IndexToastName,self).__init__(id)
	else:
	    super(IndexToastName,self).__init__()
	self.stat_obj.set_fk_field('tin_id')
	self.stat_obj.set_table_name('index_toast_stat')


    def stat(self,time_id,prod_cursor):
	sql_stat="""SELECT
pg_relation_size(oid) AS tidx_size,
pg_stat_get_numscans(oid) AS tidx_scan,
pg_stat_get_tuples_returned(oid) AS tidx_tup_read,
pg_stat_get_tuples_fetched(oid) AS tidx_tup_fetch,
pg_stat_get_blocks_fetched(oid) AS tidx_blks_fetch,
pg_stat_get_blocks_hit(oid) AS tidx_blks_hit
FROM pg_class WHERE oid={0}""".format(self.db_fields['obj_oid'])
	self.create_stat(time_id,sql_stat,prod_cursor)

