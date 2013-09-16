import logtime_main

class LogTimeMT(logtime_main.LogTimeMain):

    def __init__(self):
	super(LogTimeMT,self).__init__()
	self.table_name='log_time_mt'
	self.truncate_unit='minute'
