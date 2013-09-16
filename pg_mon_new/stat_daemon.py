
import sys
import time
import signal
#import psycopg2
import settings
import logtime
import logtime_mt

from daemon import Daemon

logger=settings.logger

class StatDaemon(Daemon):

    def __init__(self,pidfile, stdin='/dev/null', stdout='/dev/null', stderr='/dev/null'):
	super(StatDaemon,self).__init__(pidfile,stdin,stdout,stderr)

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

	logger.debug("Starting Stat daemon")
	delay=int(time.strftime("%S"))
	time.sleep(10-(delay % 10))

	lt=logtime.LogTime()
	ltm=logtime_mt.LogTimeMT()
	conn=psycopg2.connect(settings.custom_dsn('pg_mon'))

	while True:
	    cur=conn.cursor()
	    try:
		cur.execute("SELECT id FROM host_cluster WHERE alive AND observable")
	    except Exception as e:
		logger.critical("Cannot obtain list of clusters from pg_mon DB: {0}".format(e.pgerror))
		cur.close()
		conn.close()
		exit(1)
	    hc_ids=cur.fetchall()
	    cur.close()
	    for hc_id in hc_ids:
		hc=HostCluster(conn,hc_id[0])
		if not hc.discover_cluster_params():
		    continue
		hc.runtime_stat(lt_id)

	    logger.debug("Iteration in \"run\". Second {0}".format(int(time.strftime("%S"))))
	    time.sleep(settings.runtime_stat_interval * 60)
