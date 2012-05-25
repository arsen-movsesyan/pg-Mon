#from sys import exit
#from Logger import logger
import psycopg2
from settings import DATABASE

def make_dsn():
    dbname=DATABASE['DBNAME']
    host=DATABASE['HOST']
    port=DATABASE['PORT']
    user=DATABASE['USER']
    password=DATABASE['PASSWORD']
    sslmode=DATABASE['SSLMODE']
    return "host="+host+" dbname="+dbname+" port="+port+" user="+user+" password="+password+" sslmode="+sslmode

db_conn=psycopg2.connect(make_dsn())

