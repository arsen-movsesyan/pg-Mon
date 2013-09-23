#!/usr/bin/env -S python -B

import hostcluster
import psycopg2
import settings

import argparse
import re
import sys

parser = argparse.ArgumentParser(description='Utility for adding host to pg-Mon')

parser.add_argument('hostname')
parser.add_argument('ip_address')

parser.add_argument('-d','--dbname',help="Maintenanse DB name. Default is \"postgres\"",dest='param_maintenance_dbname')

parser.add_argument('-U','--username',help="""Username to connect to PostgreSQL database on the host. Must have superuser privileges.
    Default is \"postgres\"""",dest='param_user')

parser.add_argument('-P','--password',help="""Password to connect to PostgreSQL database. Default is empty string.
    Assuming remote DB allows trusted connection for pg-Mon""",dest='param_password')

parser.add_argument('-p','--port',help='Remote port to connect. Default is 5432',type=int,dest='param_port')

#parser.add_argument('-s','--sslmode',help='SSL mode to connect. Default is "prefer"',
#    choices=['disable','allow','prefer','require','verify-ca','verify-full'])
parser.add_argument('-m','--master',action='store_true',help='Host is master',dest='is_master')
parser.add_argument('-o','--observable',action='store_true',help='Register as observable. pg-Mon will start collect information imediatelly')
parser.add_argument('-f','--fqdn',help='Fully qualified domain name')
parser.add_argument('-c','--description',help='Brief description. Text must be included in quotes')

args=parser.parse_args()

ip_regexp = r"^(([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\.){3}([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])$";
hostname_regexp = r"^(([a-zA-Z]|[a-zA-Z][a-zA-Z0-9\-]*[a-zA-Z0-9])\.)*([A-Za-z]|[A-Za-z][A-Za-z0-9\-]*[A-Za-z0-9])$";

ip_address_pattern=re.compile(ip_regexp)
hostname_pattern=re.compile(hostname_regexp)

if not re.match(ip_address_pattern,args.ip_address):
    print "Wrong IP address format"
    sys.exit(1)
if not re.match(hostname_pattern,args.hostname):
    print "Wrong hostname format"


conn=psycopg2.connect(settings.custom_dsn('pg_mon'))
hc=hostcluster.HostCluster(conn)

string="hc.add('"+args.ip_address+"','"+args.hostname+"'"

del(args.hostname)
del(args.ip_address)

for a,v in vars(args).iteritems():
    if v:
	string += ","+a+"="
	if type(v) is str:
	    string += "'"+str(v)+"'"
	elif type(v) is int or bool:
	    string+=str(v)
string+=")"

print string
#eval(string)
conn.close()
