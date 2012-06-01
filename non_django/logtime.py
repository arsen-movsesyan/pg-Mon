from sys import exit
from Logger import logger
import database


###################################################################################################
###################################################################################################

class LogTime():
    cursor=database.db_conn.cursor()

    def __init__(self):
	time_check_query="""SELECT CASE
    WHEN (SELECT COUNT(1) FROM log_time WHERE hour_truncate=(SELECT date_trunc('hour',now())::timestamp without time zone)) > 0 
	THEN NULl
    ELSE 
	LOCALTIMESTAMP END AS actual_time,date_trunc('hour',LOCALTIMESTAMP) AS hour_truncate"""
	self.cursor.execute(time_check_query)

	time_data=self.cursor.fetchone()
	if not time_data[0]:
	    logger.critical('Appropriate record for "{0}" already exists'.format(time_data[1]))
	    self.cursor.close()
	    database.db_conn.close()
	    exit()
#	logger.debug('Log time obtained. Actual Time: {0}\tHour Truncate: {1}'.format(time_data[0],time_data[1]))
	self.actual_time=time_data[0]
	self.hour_truncate=time_data[1]
	self.cursor.execute("INSERT INTO log_time (hour_truncate,actual_time) VALUES ('{0}','{1}') RETURNING id".format(time_data[1],time_data[0]))
	self.id=self.cursor.fetchone()[0]
#	database.db_conn.commit()


    def __del__(self):
	if not self.cursor.closed:
	    self.cursor.close()

    def get_id(self):
	return self.id


###################################################################################################

