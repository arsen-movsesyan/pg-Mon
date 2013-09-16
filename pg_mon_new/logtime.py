import logtime_main

class LogTime(logtime_main.LogTimeMain):

    def __init__(self):
	super(LogTime,self).__init__()
	self.table_name='log_time'
	self.truncate_unit='hour'
