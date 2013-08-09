
#from sys import exit
from table import generic
from settings import logger,db_handler


class LogTime(generic):

    def __init__(self):
	super(LogTime,self).__init__()
	self.table='central_log_time'
	self.iden_field='hour_truncate'

class HostCluster(generic):

    def __init__(self):
	super(HostCluster,self).__init__()
	self.table='host_cluster'
	self.iden_field='host_id'

