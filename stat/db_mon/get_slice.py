#!/usr/local/bin/python -B

from objects import *
from settings import logger,db_handler
import transfer
from sys import exit

db_handler.autocommit=False
self_cursor=db_handler.cursor()
stats=['bgwriter_stat','database_stat','table_stat','table_va_stat','index_stat','table_toast_stat','index_toast_stat']

try:
    self_cursor.execute("DELETE FROM queue_log_time RETURNING id,hour_truncate")
#    self_cursor.execute("SELECT * FROM queue_log_time ORDER BY hour_truncate")
except Exception as e:
    logger.critical("Cannot get queue ids! Details: {0}".format(e.pgerror))
    exit(1)
queue_ids=self_cursor.fetchall()

hc=HostCluster()
sn=SchemaName()

for log_id in queue_ids:
    output=dict()
    output['stat_payload']=dict()
    output['list_payload']=dict()
    output['hour_truncate']=log_id[1]

    s_payload=dict()

    for stat_tbl in stats:
	stmt="SELECT * FROM {0} WHERE time_id={1}".format(stat_tbl,log_id[0])
	try:
	    self_cursor.execute(stmt)
	except Exception as e:
	    logger.error("Cannot execute statement: {0}. Details: {1}".format(stmt,e.pgerror))
	    continue
	res=self_cursor.fetchall()
	s_payload[stat_tbl]=res

    output['stat_payload']=s_payload

    l_payload=dict()
    tables=[]
    toast_tables=[]
    toast_indexes=[]
    indexes=[]
    functions=[]

    for tn_id in sn.get_tables():
	tn=TableName(tn_id)
	tables.append(tn.db_dump())
	if tn.get_toast_id():
	    ttn=TableToastName(tn.get_toast_id())
	    toast_tables.append(ttn.db_dump())
	    tin=IndexToastName(ttn.get_tindex_id())
	    toast_indexes.append(tin.db_dump())
	for ind_id in tn.get_dependants():
	    ind=IndexName(ind_id)
	    indexes.append(ind.db_dump())
	l_payload['table_name']=tables
	l_payload['index_name']=indexes
	l_payload['table_toast_name']=toast_tables
	l_payload['index_toast_name']=toast_indexes

	for fn_id in sn.get_functions():
	    fn=FunctionName(fn_id)
	    functions.append(fn.db_dump())
	l_payload['function_name']=functions


    output['list_payload']=l_payload
    tr=transfer.Transfer()
    tr.set_db_data(output)

db_handler.commit()
self_cursor.close()
db_handler.close()
