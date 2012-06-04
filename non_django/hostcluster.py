import psycopg2
from table import *
from Logger import logger

from dbname import DatabaseName
class HostCluster(genericName):
    table='host_cluster'

    __prod_conn=None
    sub_table='database_name'
    sub_fk='hc_id'
    conn_string=None

    def __init__(self,id=None):
	if id:
	    super(HostCluster,self).__init__(id)
	    self.conn_string=self.return_conn_string()
	else:
	    super(HostCluster,self).__init__()
	self.stat_obj.set_fk_field('hc_id')
	self.stat_obj.set_table_name('bgwriter_stat')

    def return_conn_string(self,dbname=None):
	if not dbname:
	    dbname=self.db_fields['param_maintenance_dbname']
	ret="host={0} dbname={1} port={2} user={3}".format(self.db_fields['param_ip_address'],dbname,self.db_fields['param_port'],self.db_fields['param_user'])
	if self.db_fields['param_password']:
	    ret+=" password={0}".format(self.db_fields['param_password'])
	sslmode=genericEnum('enum_sslmode')
	ssl=sslmode.get_name_by_id(self.db_fields['param_sslmode_id'])
	ret+=" sslmode={0}".format(ssl)
	return ret


    def get_conn_string(self,dbname=None):
	if not self.conn_string:
	    self.conn_string=self.return_conn_string()
	return self.conn_string


    def add(self,ip_address,hostname,*args,**kwargs):
	self.db_fields['param_ip_address']=ip_address
	self.db_fields['hostname']=hostname
	for k in kwargs.keys():
	    self.db_fields[k]=kwargs[k]
	logger.info("Created new hostcluster {0} ip address: {1}".format(ip_address,hostname))
	self.create()
	self.truncate()
	self._populate()


    def __set_self_db_conn(self):
	try:
	    self.__prod_conn=psycopg2.connect(self.get_conn_string())
	except Exception:
	    logger.warning("Cannot connect to postgres: {0}".format(self.get_conn_string()))
	    return False
	logger.debug('Connection to DB for host "{0}" obtained succsessfully'.format(self.db_fields['hostname']))
	return True


    def discover_cluster_params(self):
	if not self.__prod_conn:
	    if not self.__set_self_db_conn():
		logger.error("Did not obtain Prod database conection for cluster {0} in discover_cluster_params method ".format(self.db_fields['hostname']))
		return
	cur=self.__prod_conn.cursor()
	params={}
	try:
	    cur.execute("SELECT current_setting('server_version') AS ver")
	except Exception as e:
	    logger.error("Cannot get 'server_version' param for {0}. Details: {1}".format(self.db_fields['hostname'],e.pgerror))
	else:
	    params['pg_version']=cur.fetchone()[0]
	try:
	    cur.execute("SELECT current_setting('data_directory') AS pg_data_path")
	except Exception as e:
	    logger.error("Cannot get 'data_directory' param for {0}. Details: {1}".format(self.db_fields['hostname'],e.pgerror))
	else:
	    params['pg_data_path']=cur.fetchone()[0]
	try:
	    cur.execute("SELECT CASE WHEN current_setting('track_counts')='on' THEN 't'::boolean ELSE 'f'::boolean END AS track_counts")
	except Exception as e:
	    logger.error("Cannot get 'track_counts' param for {0}. Details: {1}".format(self.db_fields['hostname'],e.pgerror))
	else:
	    params['track_counts']=cur.fetchone()[0]
	try:
	    cur.execute("SELECT current_setting('track_functions') AS track_functions")
	except Exception as e:
	    logger.error("Cannot get 'track_functions' param for {0}. Details: {1}".format(self.db_fields['hostname'],e.pgerror))
	else:
	    track_function=cur.fetchone()[0]
	    tf=genericEnum('enum_track_functions')
	    tf_id=tf.get_id_by_name(track_function)
	    params['track_function_id']=tf_id
	cur.close()
	if len(params) > 0:
	    update_stat="UPDATE {0} SET ".format(self.table)
	    for k in params.keys():
		update_stat+="{0}='{1}',".format(k,params[k])
	    update_stat=update_stat[:-1]+" WHERE id={0}".format(self.id)
	    self.update_record(update_stat)
	    logger.info("Updated {0}\nDetails: {1}".format(self.db_fields['hostname'],update_stat))
	    self.truncate()
	    self._populate()
	else:
	    logger.debug("No data obtained during discover for hostcluster {0}".format(self.db_fields['hostname']))


    def discover_cluster_databases(self):
	if not self.__prod_conn:
	    if not self.__set_self_db_conn():
		logger.error("Did not obtain Prod database conection for cluster {0} in discover_cluster_databases method ".format(self.db_fields['hostname']))
		return
	cur=self.__prod_conn.cursor()
	try:
	    cur.execute("SELECT oid,datname FROM pg_database WHERE NOT datistemplate AND datname !='postgres'")
	except Exception as e:
	    logger.error("Cannot execute database discovery query: {0}".format(e))
	    cur.close()
	    return
	prod_dbs=cur.fetchall()
	cur.close()
	self.cursor.execute("SELECT obj_oid,db_name,id FROM database_name WHERE hc_id={0} AND alive".format(self.id))
	local_dbs=self.cursor.fetchall()
	for l_db in local_dbs:
	    for p_db in prod_dbs:
		if l_db[0]==p_db[0] and l_db[1]==p_db[1]:
		    break
	    else:
		old_db=DatabaseName(l_db[2],self.return_conn_string(dbname=l_db[1]))
		old_db.retire()
		logger.info("Retired database {0} in cluster {1}".format(l_db[1],self.db_fields['hostname']))
	for p_db in prod_dbs:
	    for l_db in local_dbs:
		if l_db[0]==p_db[0] and l_db[1]==p_db[1]:
		    break
	    else:
		new_db=DatabaseName()
		new_db.set_fields(hc_id=self.id,obj_oid=p_db[0],db_name=p_db[1])
		new_db.create()
		new_db.truncate()
		logger.info("Create new database {0} for cluster {1}".format(p_db[1],self.db_fields['hostname']))


    def get_track_function(self):
	if self.id:
	    tf=genericEnum('enum_track_functions')
	    return tf.get_name_by_id(self.db_fields['track_function_id'])
	return None


    def stat(self,time_id):
	if not self.__prod_conn:
	    if not self.__set_self_db_conn():
		logger.error("Did not obtain Prod database conection for cluster {0} in discover_cluster_databases method ".format(self.db_fields['hostname']))
		return
	cur=self.__prod_conn.cursor()
	sql_stat="""SELECT
pg_stat_get_bgwriter_timed_checkpoints() AS checkpoints_timed,
pg_stat_get_bgwriter_requested_checkpoints() AS checkpoints_req,
pg_stat_get_bgwriter_buf_written_checkpoints() AS buffers_checkpoint,
pg_stat_get_bgwriter_buf_written_clean() AS buffers_clean,
pg_stat_get_bgwriter_maxwritten_clean() AS maxwritten_clean,
pg_stat_get_buf_written_backend() AS buffers_backend,
pg_stat_get_buf_alloc() AS buffers_alloc"""
	self.create_stat(time_id,sql_stat,cur)
	cur.close()

    def __del__(self):
	if self.__prod_conn:
	    if not self.__prod_conn.closed:
		self.__prod_conn.close()


    def get_dependants(self,obs=None):
	select_stat="SELECT id,db_name FROM {0} WHERE {1}={2} AND alive".format(self.sub_table,self.sub_fk,self.id)
	if obs:
	    select_stat+=" AND observable"
	try:
	    self.cursor.execute(select_stat)
	except Exception as e:
	    logger.error(e.pgerror)
	    return
	ret=[]
	for db in self.cursor.fetchall():
	    ret.append(dict(id=db[0],db_name=db[1]))
	return ret
