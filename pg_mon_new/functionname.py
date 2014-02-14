import table
import settings

logger=settings.logger


class FunctionName(table.genericName):

    def __init__(self,in_db_conn,in_prod_dsn,in_id=None):
	super(FunctionName,self).__init__(in_db_conn,in_id)
	self.table='function_name'
	if in_id:
	    self._populate()
	    self.prod_dsn=in_prod_dsn
	    self.stat_obj=table.genericStat(self.db_conn,'function_stat','fn_id',in_id)
	    self.stat_query="""SELECT
pg_stat_get_function_calls(oid) AS func_calls,
pg_stat_get_function_total_time(oid) AS total_time,
pg_stat_get_function_self_time(oid) AS self_time
FROM pg_proc
WHERE oid={0}""".format(self.db_fields['pro_oid'])

