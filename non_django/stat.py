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
time_id=lt.get_id()

hc=HostCluster(1)

hc.stat(time_id)
for db_id in hc.get_dependants(obs=True):
    dn=DatabaseName(db_id)
    dn.stat(time_id)
    db_cursor=dn.get_prod_cursor()
    if db_cursor:
	for sn_id in dn.get_dependants(obs=True):
	    sn=SchemaName(sn_id)
	    sn.discover_tables(db_cursor)
	    sn.discover_functions(db_cursor)
	    for tn_id in sn.get_tables():
		tn=TableName(tn_id)
		tn.stat(time_id,db_cursor)
		tn.va_stat(time_id,db_cursor)
		tn.discover_indexes(db_cursor)
		tn.discover_toast(db_cursor)

		for in_id in tn.get_dependants():
		    ind=IndexName(in_id)
		    ind.stat(time_id,db_cursor)
		ttn_id=tn.get_toast_id()
		if ttn_id:
		    ttn=TableToastName(ttn_id)
		    ttn.stat(time_id,db_cursor)
		    ttn.discover_index(db_cursor)
		    tidx_id=ttn.get_tindex_id()
		    if tidx_id:
			tindx=IndexToastName(tidx_id)
			tindx.stat(time_id,db_cursor)

	    if hc.get_field('track_functions') != 'none':
		for fn_id in sn.get_functions():
		    print "Fuct {0}".format(fn_id)
	db_cursor.close()
database.db_conn.close()

