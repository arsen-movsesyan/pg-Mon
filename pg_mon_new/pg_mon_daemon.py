
import sys
import time
import signal
import psycopg2
import settings
import logtime
import logtime_mt

from daemon import Daemon

from hostcluster import HostCluster
from dbname import DatabaseName
from schemaname import SchemaName
from tablename import TableName
from indexname import IndexName
from tabletoastname import TableToastName
from indextoastname import IndexToastName

from functionname import FunctionName


logger=settings.logger

class PgmonDaemon(Daemon):

    def _get_current_time(self,time_format='%S'):
	return int(time.strftime(time_format))

    def __init__(self,pidfile, stdin='/dev/null', stdout='/dev/null', stderr='/dev/null'):
	super(PgmonDaemon,self).__init__(pidfile,stdin,stdout,stderr)

    def _sig_term(self,signum,frame):
#	self.__del__()
	logger.debug("Signal Number {0} received. Exiting...".format(signum))
	sys.exit(0)

    def _sig_reload(self,signum,frame):
	logger.debug("Signal Number {0} received. Reloading config...".format(signum))
	reload(settings)


    def run(self):
	signal.signal(signal.SIGTERM,self._sig_term)
	signal.signal(signal.SIGHUP,self._sig_reload)

	cur_minute=self._get_current_time('%M')
	delay=60*(settings.runtime_stat_interval - (cur_minute % settings.runtime_stat_interval)) - self._get_current_time()+10
	logger.debug("Starting PgMon daemon. Minute={0}  Delay={1}".format(cur_minute,delay))
	time.sleep(delay)

	lt=logtime.LogTime()
	ltm=logtime_mt.LogTimeMT()
	conn=psycopg2.connect(settings.custom_dsn('pg_mon'))

	while True:
	    current_time_minute=self._get_current_time('%M')
	    logger.debug("Iteration started. Minute {0}".format(current_time_minute))
	    if (current_time_minute % settings.runtime_stat_interval) == 0:
		logger.debug("Iteration in runtime_stat_interval. Minute {0}".format(current_time_minute))
		ltm_id=ltm.get_id()
		if not ltm_id:
		    continue
		cur=conn.cursor()
		try:
		    cur.execute("SELECT id FROM host_cluster WHERE alive AND observable")
		except Exception as e:
		    logger.critical("Cannot obtain list of clusters from pg_mon DB: {0}".format(e.pgerror))
		    cur.close()
		    continue
		hc_ids=cur.fetchall()
		cur.close()
		for hc_id in hc_ids:
		    hc=HostCluster(conn,hc_id[0])
		    if not hc.discover_cluster_params():
			logger.critical("Cannot discover clusters params for HC: {0}".format(hc.get_field('hostname')))
			continue
		    hc.runtime_stat(ltm_id)
		    hc.discover_cluster_databases()
		    if (current_time_minute % settings.regular_stat_interval) == 0:
			logger.debug("Iteration in regular_stat_interval. Minute {0}".format(current_time_minute))
			lt_id=lt.get_id()
			hc.stat(lt_id)
		    for dbs in hc.get_dependants(True):
			db_dsn=dbs['db_dsn']
			dn=DatabaseName(conn,db_dsn,dbs['id'])
			dn.runtime_stat(ltm_id)
			dn.discover_schemas()
			if (current_time_minute % settings.regular_stat_interval) == 0:
			    dn.stat(lt_id)
			    for sn in dn.get_dependants(True):
				sn=SchemaName(conn,db_dsn,sn)
				sn.discover_tables()
				sn.discover_functions()
				for tbl_id in sn.get_tables():
				    tn=TableName(conn,db_dsn,tbl_id)
				    tn.stat(lt_id)
				    tn.va_stat(lt_id)
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
			lt.reset_id()
		ltm.reset_id()

	    delay_to_next=60 * settings.runtime_stat_interval - self._get_current_time()+10
	    logger.debug("Iteration Done. Minute {0} Next delay {1}".format(current_time_minute,delay_to_next))
	    time.sleep(delay_to_next)
