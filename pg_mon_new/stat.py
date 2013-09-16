#!/usr/local/bin/python -B


import settings
import psycopg2

from sys import exit
from logtime import LogTime
from hostcluster import HostCluster
from dbname import DatabaseName
from schemaname import SchemaName
from tablename import TableName
from indexname import IndexName
from tabletoastname import TableToastName
from indextoastname import IndexToastName

from functionname import FunctionName



lt=LogTime()
lt_id=lt.get_id()

if not lt_id:
    exit(0)

conn=psycopg2.connect(settings.custom_dsn('pg_mon'))

cur=conn.cursor()
try:
    cur.execute("SELECT id FROM host_cluster WHERE alive AND observable")
except Exception as e:
    logger.critical("Cannot obtain list of clusters from pg_mon DB: {0}".format(e.pgerror))
    exit(1)

hc_ids=cur.fetchall()
cur.close()

for hc_id in hc_ids:
    hc=HostCluster(conn,hc_id[0])
    if not hc.discover_cluster_params():
	continue
    hc.stat(lt_id)
    for dbs in hc.get_dependants(True):
	db_dsn=dbs['db_dsn']
	dn=DatabaseName(conn,db_dsn,dbs['id'])
	dn.stat(lt_id)
	for sn in dn.get_dependants(True):
	    sn=SchemaName(conn,db_dsn,sn)
	    sn.discover_tables()
	    sn.discover_functions()
	    for tbl_id in sn.get_tables():
		tn=TableName(conn,db_dsn,tbl_id)
		tn.stat(lt_id)
		tn.va_stat(lt.get_id())
		tn.discover_indexes()
		for ind_id in tn.get_dependants():
		    ind=IndexName(conn,db_dsn,ind_id)
		    ind.stat(lt_id)

		tn.discover_toast()
		toast_id=tn.get_toast_id()
		if toast_id:
		    ttn=TableToastName(conn,db_dsn,toast_id)
		    ttn.stat(lt_id)
		    ttn.discover_index()
		    tin=IndexToastName(conn,db_dsn,ttn.get_tindex_id())
		    tin.stat(lt_id)

	    if hc.get_track_function() != 'none':
		for fnc_id in sn.get_functions():
		    func=FunctionName(conn,db_dsn,fnc_id)
		    func.stat(lt_id)


conn.close()

