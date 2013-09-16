import table
import settings
from dbname import DatabaseName

logger=settings.logger

class HostCluster(table.genericName):

    def __init__(self,in_db_conn,in_id=None):
	super(HostCluster,self).__init__(in_db_conn,in_id)
	self.table='host_cluster'
	if in_id:
	    self._initialyze(in_id)


    def _initialyze(self,in_id):
	self._populate()
	self.prod_dsn=self.get_conn_string()
	self.stat_obj=table.genericStat('bgwriter_stat','hc_id',in_id)
	self.runtime_stat_obj=table.genericStat('cluster_runtime_stat','hc_id',in_id)
	self.sub_table='database_name'
	self.sub_fk='hc_id'
	self.stat_query="""SELECT
pg_stat_get_bgwriter_timed_checkpoints() AS checkpoints_timed,
pg_stat_get_bgwriter_requested_checkpoints() AS checkpoints_req,
pg_stat_get_bgwriter_buf_written_checkpoints() AS buffers_checkpoint,
pg_stat_get_bgwriter_buf_written_clean() AS buffers_clean,
pg_stat_get_bgwriter_maxwritten_clean() AS maxwritten_clean,
pg_stat_get_buf_written_backend() AS buffers_backend,
pg_stat_get_buf_alloc() AS buffers_alloc"""
	self.runtime_stat_query="""SELECT current_setting('max_connections') AS conn_total,COUNT(*) AS conn_used 
	FROM pg_stat_activity GROUP BY 1"""


    def get_conn_string(self,in_db_name=None):
	if not in_db_name:
	    dbname=self.db_fields['param_maintenance_dbname']
	else:
	    dbname=in_db_name
	ret="host={0} dbname={1} port={2} user={3}".format(self.db_fields['param_ip_address'],dbname,self.db_fields['param_port'],self.db_fields['param_user'])
	if self.db_fields['param_password']:
	    ret+=" password={0}".format(self.db_fields['param_password'])
	sslmode=table.genericEnum('enum_sslmode',self.db_conn.cursor())
	ssl=sslmode.get_name_by_id(self.db_fields['param_sslmode_id'])
	ret+=" sslmode={0}".format(ssl)
	return ret


#    def get_conn_string(self,dbname=None):
#	return self.conn_string


    def add(self,ip_address,hostname,*args,**kwargs):
	self.db_fields['param_ip_address']=ip_address
	self.db_fields['hostname']=hostname
	for k in kwargs.keys():
	    self.db_fields[k]=kwargs[k]
	if self._create():
	    self.db_conn.commit()
	    logger.info("Created new hostcluster {0} ip address: {1}".format(ip_address,hostname))
	    self._initialyze(self.id)
	else:
	    logger.critical("Cannot create new hostcluster {0} with ip address: {1}".format(ip_address,hostname))



    def discover_cluster_params(self):
	if not self.prod_conn or self.prod_conn.closed:
	    if not self.set_prod_conn():
		return False
	cur=self.prod_conn.cursor()
	params={}
	try:
	    cur.execute("SELECT current_setting('server_version') AS ver")
	except Exception as e:
	    logger.error("Cannot get 'server_version' param for {0}. Details: {1}".format(self.db_fields['hostname'],e.pgerror))
	else:
	    pg_ver=cur.fetchone()[0]
	    if self.db_fields['pg_version'] != pg_ver:
		logger.info("Updated parameter 'pg_version' set to '{0}' for hostcluster {1}".format(pg_ver,self.db_fields['hostname']))
		params['pg_version']=pg_ver
	try:
	    cur.execute("SELECT current_setting('data_directory') AS pg_data_path")
	except Exception as e:
	    logger.error("Cannot get 'data_directory' param for {0}. Details: {1}".format(self.db_fields['hostname'],e.pgerror))
	else:
	    data_path=cur.fetchone()[0]
	    if self.db_fields['pg_data_path'] != data_path:
		logger.info("Updated parameter 'pg_data_path' set to '{0}' for hostcluster {1}".format(data_path,self.db_fields['hostname']))
		params['pg_data_path']=data_path
	try:
	    cur.execute("SELECT CASE WHEN current_setting('track_counts')='on' THEN 't'::boolean ELSE 'f'::boolean END AS track_counts")
	except Exception as e:
	    logger.error("Cannot get 'track_counts' param for {0}. Details: {1}".format(self.db_fields['hostname'],e.pgerror))
	else:
	    t_c=cur.fetchone()[0]
	    if self.db_fields['track_counts'] != t_c:
		logger.info("Updated parameter 'track_counts' set to '{0}' for hostcluster {1}".format(t_c,self.db_fields['hostname']))
		params['track_counts']=t_c
	try:
	    cur.execute("SELECT current_setting('track_functions') AS track_functions")
	except Exception as e:
	    logger.error("Cannot get 'track_functions' param for {0}. Details: {1}".format(self.db_fields['hostname'],e.pgerror))
	else:
	    t_f=cur.fetchone()[0]
	    tf=table.genericEnum('enum_track_functions',self.db_conn.cursor())
	    tf_id=tf.get_id_by_name(t_f)

	    if self.db_fields['track_function_id'] != tf_id:
		logger.info("Updated parameter 'track_functions' set to '{0}' for hostcluster {1}".format(t_f,self.db_fields['hostname']))
		params['track_function_id']=tf_id
	cur.close()
	if len(params) > 0:
	    update_stat="UPDATE {0} SET ".format(self.table)
	    for k in params.keys():
		update_stat+="{0}='{1}',".format(k,params[k])
	    update_stat=update_stat[:-1]+" WHERE id={0}".format(self.id)
	    cur=self.db_conn.cursor()
	    try:
		cur.execute(update_stat)
	    except Exception as e:
		logger.error("Cannot update hostcluster new discovered data: {0}".format(e.pgerror))
		return False
	    self.db_fields={}
	    self._populate()
	    self.db_conn.commit()
#	else:
#	    logger.debug("No new data obtained during discover for hostcluster {0}".format(self.db_fields['hostname']))
	return True

    def discover_cluster_databases(self):
	if not self.prod_conn or self.prod_conn.closed:
	    if not self.set_prod_conn():
		return False
	cur=self.prod_conn.cursor()
	try:
	    cur.execute("SELECT oid,datname FROM pg_database WHERE NOT datistemplate AND datname !='postgres'")
	except Exception as e:
	    logger.error("Cannot execute database discovery query on Prod: {0}".format(e.pgerror))
	    cur.close()
	    return
	prod_dbs=cur.fetchall()
	cur.close()
	cur=self.db_conn.cursor()
	try:
	    cur.execute("SELECT obj_oid,db_name,id FROM database_name WHERE hc_id={0} AND alive".format(self.id))
	except Exception as e:
	    logger.error("Cannot execute database discovery query on Local: {0}".format(e.pgerror))
	    cur.close()
	    return
	local_dbs=cur.fetchall()
	cur.close()
	for l_db in local_dbs:
	    for p_db in prod_dbs:
		if l_db[0]==p_db[0] and l_db[1]==p_db[1]:
		    break
	    else:
		old_db=DatabaseName(self.db_conn,self.prod_dsn,l_db[2])
		old_db.retire()
		logger.info("Retired database {0} in cluster {1}".format(l_db[1],self.db_fields['hostname']))
	for p_db in prod_dbs:
	    for l_db in local_dbs:
		if l_db[0]==p_db[0] and l_db[1]==p_db[1]:
		    break
	    else:
		new_db=DatabaseName(self.db_conn,self.prod_dsn)
		new_db.set_fields(hc_id=self.id,obj_oid=p_db[0],db_name=p_db[1])
		new_db._create()
		logger.info("Create new database {0} for cluster {1}".format(p_db[1],self.db_fields['hostname']))
	self.db_conn.commit()

    def get_track_function(self):
	if self.id:
	    tf=table.genericEnum('enum_track_functions',self.db_conn.cursor())
	    return tf.get_name_by_id(self.db_fields['track_function_id'])
	return None



    def get_dependants(self,obs=True):
	select_stat="SELECT id,db_name FROM {0} WHERE {1}={2} AND alive".format(self.sub_table,self.sub_fk,self.id)
	if obs:
	    select_stat+=" AND observable"
	cur=self.db_conn.cursor()
	try:
	    cur.execute(select_stat)
	except Exception as e:
	    logger.error(e.pgerror)
	    return
	ret=[]
	for db in cur.fetchall():
	    ret.append(dict(id=db[0],db_dsn=self.get_conn_string(db[1])))
	cur.close()
	return ret
