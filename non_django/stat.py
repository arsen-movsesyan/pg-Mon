#!/usr/local/bin/python -B


import database

from logtime import LogTime
from hostcluster import HostCluster
from dbname import DatabaseName
from schemaname import SchemaName
from tablename import TableName
from functionname import FunctionName
from indexname import IndexName
from tabletoastname import TableToastName
from indextoastname import IndexToastName



lt=LogTime()

work_cursor=database.db_conn.cursor()
work_cursor.execute("SELECT id FROM host_cluster WHERE alive AND observable")



for hc_id in work_cursor.fetchall():
    hc=HostCluster(hc_id[0])

    hc.stat(lt.id)
    for dbs in hc.get_dependants(obs=True):
	db_conn_string=hc.return_conn_string(dbs['db_name'])
	dn=DatabaseName(dbs['id'],db_conn_string)
	dn.stat(lt.id)
	db_cursor=dn.get_prod_cursor()
	if db_cursor:
	    for sn_id in dn.get_dependants():
		sn=SchemaName(sn_id)
		sn.discover_tables(db_cursor)
		sn.discover_functions(db_cursor)
		for tbl_id in sn.get_tables():
		    tn=TableName(tbl_id)
		    tn.stat(lt.id,db_cursor)
		    tn.va_stat(lt.id,db_cursor)
		    tn.discover_indexes(db_cursor)
		    for ind_id in tn.get_dependants():
			ind=IndexName(ind_id)
			ind.stat(lt.id,db_cursor)
		    tn.discover_toast(db_cursor)
		    toast_id=tn.get_toast_id()
		    if toast_id:
			ttn=TableToastName(toast_id)
			ttn.stat(lt.id,db_cursor)
			ttn.discover_index(db_cursor)
			tin=IndexToastName(ttn.get_tindex_id())
			tin.stat(lt.id,db_cursor)
		if hc.get_track_function():
		    for fnc_id in sn.get_functions():
			func=FunctionName(fnc_id)
			func.stat(lt.id,db_cursor)
	    if not db_cursor.closed:
		db_cursor.close()

work_cursor.close()
database.db_conn.close()

