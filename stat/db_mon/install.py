#!/usr/local/bin/python -B

from subprocess import check_output
exists=check_output(['psql','-U','postgres','-c',"SELECT 1 FROM pg_database WHERE datname='db_mon'",'-A','-t'])

from sys import exit

if str(exists).strip() == '1':
    exit(1)

install=check_output(['psql','-U','postgres','-f','db_mon.sql'])

#from uuid import uuid1
from settings import logger,db_handler,prod_handler
from objects import *

#def get_my_mac():
#    my_uuid=uuid1()
#    mac_addr="{0:0>12}".format(hex(my_uuid.node)[2:-1])
#    return mac_addr[:2] + ":" + ":".join([mac_addr[i] + mac_addr[i+1] for i in range(2,12,2)])


self_cursor=db_handler.cursor()
prod_cursor=prod_handler.cursor()
self_cursor.execute("INSERT INTO host_cluster VALUES (1,'t','t','t','localhost','{0}')".format(get_my_mac()))
self_cursor.execute("INSERT INTO database_name VALUES (1,1,'t','t','lms_db')") 
self_cursor.execute("INSERT INTO schema_name VALUES (1,1,'t','t','public')")

sn=SchemaName()
sn.discover_tables()
for tn_id in sn.get_tables():
    tn=TableName(tn_id)
    tn.discover_indexes()
    tn.discover_toast()
    toast_id=tn.get_toast_id()
    if toast_id:
	ttn=TableToastName(toast_id)
	ttn.discover_index()

sn.discover_functions()

try:
    prod_cursor.execute("SELECT current_setting('track_functions') AS track_functions")
except Exception as e:
    logger.error("Cannot get 'track_functions' configuraion param: {0}".format(e.pgerror))
    pass
else:
    track_changes=prod_cursor.fetchone()[0]
    if track_changes != 'none':
	self_cursor.execute("UPDATE host_cluster SET track_functions ='{0}'".format(track_changes))

prod_cursor.close()
self_cursor.close()
db_handler.close()
prod_handler.close()

