import logtime_main

class LogTime(logtime_main.LogTimeMain):

    def __init__(self,in_db_conn):
	super(LogTime,self).__init__(in_db_conn)
	self.table_name='log_time'
	self.truncate_unit='hour'
