
import sys, os, time, atexit
from signal import SIGTERM,SIGHUP
from settings import logger

class Daemon(object):

    def __init__(self, pidfile, stdin='/dev/null', stdout='/dev/null', stderr='/dev/null'):
	self.stdin = stdin
	self.stdout = stdout
	self.stderr = stderr
	self.pidfile = pidfile

    def daemonize(self):
	try:
	    pid = os.fork()
	    if pid > 0:
		# exit first parent
		sys.exit(0)
	except OSError, e:
	    logger.error("Fork #1 failed: {0} ({1})".format(e.errno, e.strerror))
	    sys.exit(1)

	# decouple from parent environment
	os.chdir("/")
#	logger.debug("Fork #1 passed")
	os.setsid()
	os.umask(0)

	# do second fork
	try: 
	    pid = os.fork()
	    if pid > 0:
		# exit from second parent
		sys.exit(0)
	except OSError, e:
#	    sys.stderr.write("fork #2 failed: %d (%s)\n" % (e.errno, e.strerror))
	    logger.error("Fork #2 failed: {0} ({1})".format(e.errno, e.strerror))
	    sys.exit(1)

	# redirect standard file descriptors
#	logger.debug("Fork #2 passed")
	sys.stdout.flush()
	sys.stderr.flush()
	si = file(self.stdin, 'r')
	so = file(self.stdout, 'a+')
	se = file(self.stderr, 'a+', 0)
	os.dup2(si.fileno(), sys.stdin.fileno())
	os.dup2(so.fileno(), sys.stdout.fileno())
	os.dup2(se.fileno(), sys.stderr.fileno())

	# write pidfile
	atexit.register(self.delpid)
	pid = str(os.getpid())
	file(self.pidfile,'w+').write("%s\n" % pid)
#	logger.debug("Get pid: {0}".format(pid))

    def get_pid(self):
	try:
	    pf = file(self.pidfile,'r')
	    pid = int(pf.read().strip())
	    pf.close()
	except IOError:
	    pid = None
	    return None
	return int(pid)


    def delpid(self):
	os.remove(self.pidfile)

    def start(self):
	pid=self.get_pid()
	if pid:
	    message = "pidfile %s already exist. Daemon already running?\n"
	    sys.stderr.write(message % self.pidfile)
	    sys.exit(1)

	self.daemonize()
	self.run()


    def stop(self):
	# Try killing the daemon process
	pid=self.get_pid()
	if not pid:
	    message = "pidfile %s does not exist. Daemon not running?\n"
	    sys.stderr.write(message % self.pidfile)
	    return
	try:
	    while 1:
		os.kill(pid, SIGTERM)
		time.sleep(0.1)
	except OSError, err:
	    err = str(err)
	    if err.find("No such process") > 0:
		if os.path.exists(self.pidfile):
		    os.remove(self.pidfile)
	    else:
		print str(err)
		sys.exit(1)


    def restart(self):
	self.stop()
	self.start()

    def run(self):
	"""
	Override this method in child subclass. It will be called after the process has been
	daemonized by start() or restart().
	"""
