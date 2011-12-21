#!/usr/bin/env python

from django.core.management import setup_environ

import settings
setup_environ(settings)
from cluster.models import *

lt=LogTime()
lt.save()
time_id=lt.id

for hc in HostCluster.objects.filter(alive=True,observable=True):
    hc.bg_stat(time_id)
    for db in hc.databasename_set.filter(alive=True,observable=True):
	db.db_stat(time_id);
	conn_string=db.get_conn_string()
	for sc in db.schemaname_set.filter(alive=True,observable=True):
	    sc.discover_schema_functions(conn_string)
	    sc.discover_schema_tables(conn_string)
	    for tbl in sc.tablename_set.filter(alive=True):
		tbl.discover_indexes(conn_string)
		tbl.tbl_stat(time_id,conn_string)
		tbl.tbl_va_stat(time_id,conn_string)
		for idx in tbl.indexname_set.filter(alive=True):
		    idx.idx_stat(time_id,conn_string)
		for toast in tbl.tabletoastname_set.all():
		    toast.tbl_toast_stat(time_id,conn_string)
		    for t_idx in toast.indextoastname_set.all():
			t_idx.idx_toast_stat(time_id,conn_string)
	    for fn in sc.functionname_set.filter(alive=True):
		fn.func_stat(time_id,conn_string)
