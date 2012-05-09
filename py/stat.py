#!/usr/bin/env python

import settings
import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")

from cluster.models import *

lt=LogTime()

for hc in HostCluster.objects.filter(alive=True,observable=True):
    hc.bg_stat(lt.id)
    for db in hc.databasename_set.filter(alive=True,observable=True):
	db.db_stat(lt.id);
	prod_conn=db.obtain_database_connection()
	for sn in db.schemaname_set.filter(alive=True,observable=True):
	    sn.discover_schema_tables(prod_conn)
	    sn.discover_schema_functions(prod_conn)
	    if hc.track_functions != 'none':
		for fn in sn.functionname_set.filter(alive=True):
		    fn.func_stat(lt.id,prod_conn)
	    for tn in sn.tablename_set.filter(alive=True):
		tn.tbl_stat(lt.id,prod_conn)
		tn.tbl_va_stat(lt.id,prod_conn)
		for idx in tn.indexname_set.filter(alive=True):
		    idx.idx_stat(lt.id,prod_conn)
		tt=tn.tabletoastname_set.filter(alive=True)
		if len(tt) > 0:
		    tt[0].tbl_toast_stat(lt.id,prod_conn)
		    tidx=tt[0].indextoastname_set.filter(alive=True)
		    tidx[0].idx_toast_stat(lt.id,prod_conn)

