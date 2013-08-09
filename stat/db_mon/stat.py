#!/usr/local/bin/python -B

from objects import *

lt=LogTime()


hc=HostCluster()
hc.create_stat(lt.id)

dn=DatabaseName()
dn.create_stat(lt.id)

sn=SchemaName()

#sn.discover_tables()
for tn_id in sn.get_tables():
    tn=TableName(tn_id)
    tn.create_stat(lt.id)
    tn.va_stat(lt.id)
#    tn.discover_indexes()
    for ind_id in tn.get_dependants():
	ind=IndexName(ind_id)
	ind.create_stat(lt.id)
    tn.discover_toast()
    toast_id=tn.get_toast_id()
    if toast_id:
	ttn=TableToastName(toast_id)
	ttn.create_stat(lt.id)
	ttn.discover_index()
	tin=IndexToastName(ttn.get_tindex_id())
	tin.create_stat(lt.id)

#sn.discover_functions()
if hc.get_field('track_functions') != 'none':
    for fn_id in sn.get_functions():
	fn=FunctionName(fn_id)
#	fn.create_stat()
