
import sys
import time
import signal
import psycopg2

import settings
from daemon import Daemon

import logtime
import logtime_mt

from hostcluster import HostCluster


logger=settings.logger

class PgmonDaemon(Daemon):

    def _get_current_time(self,time_format='%S'):
	return int(time.strftime(time_format))

    def __init__(self,pidfile, stdin='/dev/null', stdout='/dev/null', stderr='/dev/null'):
	super(PgmonDaemon,self).__init__(pidfile,stdin,stdout,stderr)
	self.pg_mon_conn=None

    def _sig_term(self,signum,frame):
	logger.debug("Signal Number {0} received".format(signum))
	if signum == signal.SIGTERM:
	    logger.debug("Exiting...")
	    sys.exit(0)
#	if signum == signal.SIGHUP:
#	    logger.debug("Reloading...")
#	    reload(settings)


    def _sig_reload(self,signum,frame):
	logger.debug("Signal Number {0} received. Reloading config...".format(signum))
	reload(settings)

    def _delay(self):
	delay_to_next=60 * (settings.runtime_stat_interval - self._get_current_time("%M") % settings.runtime_stat_interval) - self._get_current_time()
	logger.debug("Delay Invoked. Sec: {0}".format(delay_to_next))
	time.sleep(delay_to_next)


    def _set_pg_mon_conn(self):
	try:
	    self.pg_mon_conn=psycopg2.connect(settings.custom_dsn('pg_mon'))
	except Exception as e:
	    logger.critical("Cannot connect to pg_mon DB: {0}".format(e))
	    return False
	logger.debug("Successfully connected to pg_mon database")
	return True

    def _get_cursor(self):
	if not self.pg_mon_conn:
	    logger.error("Trying obtain cursor while DB connection to pg_mon is not set!")
	    return False
	return self.pg_mon_conn.cursor()

    def _rollback(self):
	logger.error("Rollback invoked!")
	self.pg_mon_conn.rollback()
	self.pg_mon_conn.close()
	self._delay()


    def run(self):
	signal.signal(signal.SIGTERM,self._sig_term)
	signal.signal(signal.SIGHUP,self._sig_reload)

	cur_minute=self._get_current_time('%M')
	delay=60*(settings.runtime_stat_interval - (cur_minute % settings.runtime_stat_interval)) - self._get_current_time()
	logger.info("Starting PgMon daemon")
	logger.debug("Delay to iterations: {0}".format(delay))
	time.sleep(delay)

	while True:

	    regular_stat=False
	    current_time_minute=self._get_current_time('%M')

	    lt_id=False
	    ltm_id=False


	    if not self._set_pg_mon_conn():
		self._delay()
		continue
	    if settings.runtime_stat_enable:
		ltm=logtime_mt.LogTimeMT(self.pg_mon_conn)
		ltm_id=ltm.get_id()
		if not ltm_id:
		    self._rollback()
		    continue
		self.pg_mon_conn.commit()
		logger.debug("Obtained ltm_id: {0}".format(ltm_id))

	    if (current_time_minute % settings.regular_stat_interval) == 0:
		lt=logtime.LogTime(self.pg_mon_conn)
		lt_id=lt.get_id()
		if not lt_id:
		    self._rollback()
		    continue
		regular_stat=True
		self.pg_mon_conn.commit()
		logger.debug("Obtained lt_id: {0}".format(lt_id))

	    cur=self._get_cursor()
	    try:
		cur.execute("SELECT id FROM host_cluster WHERE alive AND observable")
	    except Exception as e:
		logger.critical("Cannot obtain list of clusters from pg_mon DB: {0}".format(e.pgerror))
		cur.close()
		self._rollback()
		continue
	    hc_ids=cur.fetchall()
	    cur.close()


###############################################################
################# HostClusters ################################
	    for hc_id in hc_ids:
		logger.debug("hc_id: {0}".format(hc_id[0]))
		hc=HostCluster(self.pg_mon_conn,hc_id[0])
		if not hc.discover_cluster_params():
		    logger.critical("Cannot discover clusters params for HC: {0}".format(hc.get_field('hostname')))
#		    continue
		if not hc.discover_databases():
		    logger.critical("Cannot discover databases for host ID: {0}".format(hc_id))
		if settings.runtime_stat_enable:
		    logger.debug("Runtime is enabled")
		    if not hc.runtime_stat(ltm_id):
			logger.error("Error from hc.runtime_stat()")
		if regular_stat:
		    logger.debug("Getting hc regular stat")
		    if not hc.stat(lt_id):
			logger.error("Error from hc.stat()")
		hc.__del__()
	    self.pg_mon_conn.close()
	    self._delay()
