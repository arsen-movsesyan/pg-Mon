import logtime_main

class LogTimeMT(logtime_main.LogTimeMain):

    def __init__(self,in_db_conn):
	super(LogTimeMT,self).__init__(in_db_conn)
	self.table_name='log_time_mt'
	self.truncate_unit='minute'
