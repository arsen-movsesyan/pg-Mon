#!/usr/local/bin/python -B

import settings
import re
from hostcluster import HostCluster

import getopt,sys
import psycopg2

def usage():
    print "Usage: {0} -h <hostname> -d <database_name> -p <port>".format(sys.argv[0])
    print
    print "{0} is command line tool to get PostgreSQL connection string for".format(sys.argv[0])
    print "a given host, on given port for given database name"
    print "PostgreSQL cluster may be uniquely identified by hostname"
    print "(IP address) and listenning port. Additionally"
    print "database name optional parameter taken to obtain connection to specified database."
    print "Arguments are:"
    print "  -h, --host		Remote host IP address or FQDN (default \"localhost\")"
    print "  			  Please note, this parameter is not passed to DNS. Instead"
    print "  			  search in local database performed for existance"
    print "  -d, --dbname		Database name to connect to (default \"postgres\")"
    print "  -p, --port		PostgreSQL port to connect (default \"5432\")"
    print "  -s, --dsn		Output mode as DSN: host=<hostname>,port=<port_number>... (currently not supported)"
    print "    			Default is string mode: \"host=<hostname> port=<portnumber>...\""
    print "  --help		Print this help and exit"

try:
    a,b=getopt.getopt(sys.argv[1:],"d:p:h:s",["host=","port=","dbname=","help","dsn"])
except getopt.GetoptError as e:
    print
    print e
    usage()
    sys.exit(2)

if len(b) > 0:
    print
    print "Unrecognised param: {0}".format(b[0])
    usage()
    sys.exit(2)

host_search='fqdn'
db_name='postgres'
host='localhost'
port=5432
string_output=True


ip_regexp = r"^(([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\.){3}([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])$";
hostname_regexp = r"^(([a-zA-Z]|[a-zA-Z][a-zA-Z0-9\-]*[a-zA-Z0-9])\.)*([A-Za-z]|[A-Za-z][A-Za-z0-9\-]*[A-Za-z0-9])$";

for param, value in a:
    if param =='--help':
	usage()
	sys.exit(2)
    elif param in ('-h','--host'):
	if re.match(ip_regexp,value):
	    host=value
	    host_search='param_ip_address'
	elif re.match(hostname_regexp,value):
	    host=value
	else:
	    print "Incorrect hostname (or IP address) parameter: {0}".format(value)
	    sys.exit(2)
    elif param in ('-d','--dbname'):
	db_name=value
    elif param in ('-p','--port'):
	if not isinstance(value,int) and value <= 0:
	    print "Port parameter is incorrect: {0}".format(value)
	    sys.exit(2)
	else:
	    port=value
    elif param in ("-s","--dsn"):
	string_output=False

conn=psycopg2.connect(settings.custom_dsn('pg_mon'))

#cur=database.db_conn.cursor()
cur=conn.cursor()
get_stat=cur.mogrify("SELECT id FROM host_cluster WHERE {0}=%s AND param_port=%s".format(host_search),(host,port))
cur.execute(get_stat)
res_id=cur.fetchone()
print res_id
#sys.exit()
cur.close()
#conn.close()
if not res_id:
    print "No PostgreSQL cluster found for host: {0} port {1}".format(host,port)
#    cur.close()
    conn.close()
    sys.exit(2)


hc=HostCluster(conn,res_id[0])
for dbs in hc.get_dependants():
    print dbs
#    if dbs['db_name'] == db_name:
#	print hc.return_conn_string(dbname=db_name)
#	conn.close()
#	sys.exit(0)

print "No PostgreSQL cluster found for host: {0} port {1} database {2}".format(host,port,db_name)
#cur.close()
sys.exit(2)

