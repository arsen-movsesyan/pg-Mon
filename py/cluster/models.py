from django.db import models
from django.db import connection
from django import forms
from django.db import IntegrityError, DatabaseError
from sys import exit
import logging
import psycopg2
import telnetlib


logger = logging.getLogger('pg_mon_logger')

class TrackFunctionField(models.Field):

    def __init__(self, *args, **kwargs):
	super(TrackFunctionField, self).__init__(*args, **kwargs)

    def db_type(self,connection):
	return 'track_functions_state'


class VarcharArrayField(models.Field):

    def __init__(self, *args, **kwargs):
	super(VarcharArrayField,self).__init__(*args, **kwargs)

    def gb_type(self,connection):
	return 'varchar[]'


class Array():
    def __init__(self):
	self.container=[]

    def add(self,name,value):
	self.container.append(name+'='+value)

    def get_string(self):
        output=''
	for key_value in self.container:
	    output+=key_value+","
	return '{'+output[:-1]+'}'


class HostCluster(models.Model):
    ip_address = models.IPAddressField()
    hostname = models.CharField(max_length=30)
    is_master = models.BooleanField()
    observable = models.BooleanField(default=True)
    alive = models.BooleanField(default=True)
    track_counts = models.NullBooleanField(null=True)
#    track_functions = models.CharField(max_length=10,null=True)
    track_functions = TrackFunctionField(null=True)
    pg_version = models.CharField(max_length=30,null=True)
    pg_data_path = models.CharField(max_length=30,null=True)
    fqdn = models.CharField(max_length=255,null=True)
    spec_comments = models.TextField(max_length=2000,null=True)
    conn_param = VarcharArrayField(max_length=255)
    db_conn = None


    class Meta:
	db_table = 'host_cluster'



    def set_content_data(self,in_data):
	self.model_data=in_data


    def set_non_alive(self):
	self.alive=False
	logger.info('Hostcluster "{0}" disabled. Set "alive=False"'.format(self.hostcluster))
	self.save()


    def toggle_observable(self):
	obs='TRUE'
	if self.observable:
	    self.observable=False
	    obs='FALSE'
	else:
	    self.observable=True
	logger.info('Hostcluster "{0}" observable set to "{1}"'.format(self.hostcluster,obs))
	self.save()


    def add_edit(self):
	self.ip_address=self.model_data['db_ip_address']
	self.hostname=self.model_data['db_host']
	self.is_master=self.model_data.get('db_is_master', False)
#	self.is_master=self.model_data['db_is_master']
	self.spec_comments=self.model_data['db_comments']
	self.fqdn=self.model_data['db_fqdn']
	conn_array=Array()
	conn_array.add('host',self.model_data['db_ip_address'])
	conn_array.add('dbname',self.model_data['db_name'])
	conn_array.add('user',self.model_data['db_user'])
	conn_array.add('port',self.model_data['db_port'])
	conn_array.add('sslmode',self.model_data['db_sslmode'])
	conn_array.add('password',self.model_data['db_password'])
	self.conn_param=conn_array.get_string()
	self.save()


    def get_conn_string(self):
	ret=''
	for param in self.conn_param:
	    ret+=param+" "
	logger.debug('Connection string: "{0}" found'.format(ret[:-1]))
	return ret[:-1]


    def get_conn_param(self,name):
	for param in self.conn_param:
	    k_v=param.split("=")
	    if k_v[0]==name:
		logger.debug("Found VALUE for param {0}: {1}".format(name,k_v[1]))
		return k_v[1]
	logger.warning('No connection value found for param: "{0}" or param is incorrect'.format(name))
	return False


    def conn_test(self):
	tn=telnetlib.Telnet()
	try:
	    tn.open(self.ip_address,self.get_conn_param("port"),1)
	except IOError:
	    logger.warning('No connection to host: {0} port: {1}'.format(self.ip_address,self.get_conn_param("port")))
	    return False
	logger.debug('Host: {0} is up and listening on port: {1}'.format(self.ip_address,self.get_conn_param("port")))
	tn.close()
	return True


    def get_self_db_conn(self):
	if self.conn_test():
	    try:
		conn=psycopg2.connect(self.get_conn_string())
	    except Exception, e:
		logger.warning("Cannot connect to postgres: {0}".format(self.get_conn_string()))
		logger.warning("Details: {0}{1}".format(e.pgcode,e.pgerror))
		return False
	    self.db_conn=conn
	    logger.debug('Connection to DB for host "{0}" obtained succsessfully'.format(self.hostname))
	    return True
	else:
	    return False


    def discover_cluster(self):
	if self.db_conn is None:
	    if self.get_self_db_conn():
		l_cursor = self.db_conn.cursor()
	    else:
		return
	else:
	    l_cursor = self.db_conn.cursor()
	l_cursor.execute("SELECT current_setting('server_version') AS ver")
	self.pg_version=l_cursor.fetchone()[0]
	l_cursor.execute("SELECT current_setting('data_directory') AS pg_data_path")
	self.pg_data_path=l_cursor.fetchone()[0]
	l_cursor.execute("SELECT CASE WHEN current_setting('track_counts')='on' THEN 't'::boolean ELSE 'f'::boolean END AS track_counts")
	self.track_counts=l_cursor.fetchone()[0]
	l_cursor.execute("SELECT current_setting('track_functions') AS track_functions")
	self.track_functions=str(l_cursor.fetchone()[0])
	self.save()
	exist_dbs=self.databasename_set.values('id','obj_oid','db_name').filter(alive=True)
	l_cursor.execute("SELECT oid,datname FROM pg_database WHERE NOT datistemplate AND datname !='postgres'")
	new_dbs=l_cursor.fetchall()
	for new_db in new_dbs:
	    for exist_db in exist_dbs:
		if new_db[0] == exist_db['obj_oid'] and new_db[1] == exist_db['db_name']:
		    break
	    else:
		try:
		    db=self.databasename_set.create(obj_oid=new_db[0],db_name=new_db[1])
		except (IntegrityError,DatabaseError) as msg:
		    logger.error('Cannot create new database record for cluster {0}'.format(self.hostname))
		    logger.error('DETAILS: {0}'.format(msg))
		    return
		logger.info("Created new database {0} for cluster {1}".format(new_db[1],self.hostname))
	for exist_db in exist_dbs:
	    for new_db in new_dbs:
		if new_db[0] == exist_db['obj_oid'] and new_db[1] == exist_db['db_name']:
		    break
	    else:
		drop_db=DatabaseName.objects.get(pk=exist_db['id'])
		drop_db.set_non_alive()
	l_cursor.close()
	return True


    def bg_stat(self,time):
	if self.db_conn is None:
	    if self.get_self_db_conn():
		l_cursor = self.db_conn.cursor()
	    else:
		return
	else:
	    l_cursor = self.db_conn.cursor()
	try:
	    l_cursor.execute("""SELECT
pg_stat_get_bgwriter_timed_checkpoints() AS checkpoints_timed,
pg_stat_get_bgwriter_requested_checkpoints() AS checkpoints_req,
pg_stat_get_bgwriter_buf_written_checkpoints() AS buffers_checkpoint,
pg_stat_get_bgwriter_buf_written_clean() AS buffers_clean,
pg_stat_get_bgwriter_maxwritten_clean() AS maxwritten_clean,
pg_stat_get_buf_written_backend() AS buffers_backend,
pg_stat_get_buf_alloc() AS buffers_alloc""")
	except Exception, e:
	    logger.error("Cannot execute hostcluster stat query for host: {0}".format(self.hostname))
	    logger.error("Details: {0}{1}".format(e.pgcode,e.pgerror))
	    return
	stat=l_cursor.fetchone()
	logger.debug('Hostcluster stat results:\n\t{}'.format(stat))
	try:
	    self.bgwriterstat_set.create(time_id=time
	,checkpoints_timed=stat[0]
	,checkpoints_req=stat[1]
	,buffers_checkpoint=stat[2]
	,buffers_clean=stat[3]
	,maxwritten_clean=stat[4]
	,buffers_backend=stat[5]
	,buffers_alloc=stat[6])
	except (IntegrityError,DatabaseError) as msg:
	    logger.error('Cannot create bgwriter record for hostcluster {0}'.format(self.hostname))
	    logger.error('DETAILS: {0}'.format(msg))
	    pass
	logger.debug('Hostcluster stat results saved')
	l_cursor.close()

    def cluster_queries(self):
	if self.db_conn is None:
	    if self.get_self_db_conn():
		l_cursor = self.db_conn.cursor()
	    else:
		return
	else:
	    l_cursor = self.db_conn.cursor()
	try:
	    l_cursor.execute("""SELECT now()-query_start AS duration,datname,procpid,usename,client_addr,
	CASE WHEN char_length(current_query)>110 THEN substring(current_query from 0 for 110)||'...'
	ELSE current_query
	END AS cur_query FROM pg_stat_activity WHERE current_query!='<IDLE>' AND NOT procpid=pg_backend_pid() ORDER BY 1 DESC""")
	except Exception, e:
	    logger.error("Cannot execute hostcluster running queries request for host: {0}".format(self.hostname))
	    logger.error('Details: {0}{1}'.format(e.pgcode,e.pgerror))
	    return
	queries = l_cursor.fetchall()
	logger.debug('Queries running:\n\t{}'.format(queries))
	l_cursor.close()
	return queries

    def __del__(self):
	if self.db_conn is not None:
	    self.db_conn.close()


class ClusterForm(forms.Form):
    db_host = forms.CharField(max_length=30)
    db_ip_address = forms.CharField(max_length=30)
    db_fqdn = forms.CharField(max_length=30,required=False)
    db_is_master = forms.BooleanField(widget=forms.CheckboxInput(attrs={'checked':True}))
    db_comments = forms.CharField(max_length=2000,required=False)



class ClusterConnParamForm(forms.Form):
    SSLMODE_CHOICE = (
	('prefer','Prefer'),
	('allow','Allow'),
	('disable','Disable'),
	('require','Require'),
	('verify-ca','Verify-CA'),
	('verify-full','Verify-Full'),
    )
    db_name = forms.CharField(max_length=30,initial='postgres')
    db_user = forms.CharField(max_length=30,initial='postgres')
    db_password = forms.CharField(required=False)
    db_port = forms.IntegerField(initial=5432)
    db_sslmode = forms.ChoiceField(choices=SSLMODE_CHOICE)


###################################################################################################

class DatabaseName(models.Model):
    hc = models.ForeignKey(HostCluster)
    obj_oid = models.IntegerField()
    observable = models.BooleanField(default=True)
    alive = models.BooleanField(default=True)
    db_name = models.CharField(max_length=30)
    description = models.TextField(null=True)

    class Meta:
	db_table = 'database_name'

    db_conn = None

    def set_non_alive(self):
	self.alive=False
	self.save()
	logger.info('Database "{0}" disabled. Set "alive=False"'.format(self.db_name))
	logger.debug('Details: id={0} hc_id={1}'.format(self.id,self.hc_id))

    def toggle_observable(self):
	obs='TRUE'
	if self.observable:
	    self.observable=False
	    obs='FALSE'
	else:
	    self.observable=True
	self.save()
	logger.info('Database "{0}" set observable to "{1}"'.format(self.hostcluster,obs))

    def get_conn_string(self):
	l_cursor=connection.cursor()
	l_cursor.execute("SELECT get_conn_string({0},{1})".format(self.hc_id,self.id))
	conn_string=l_cursor.fetchone()[0]
	l_cursor.close()
	return conn_string


    def get_self_db_conn(self):
	try:
	    conn=psycopg2.connect(self.get_conn_string())
	except Exception, e:
	    logger.warning("Cannot connect to postgres: {0}".format(self.get_conn_string()))
	    logger.warning("Details: {0}{1}".format(e.pgcode,e.pgerror))
	    return False
	self.db_conn=conn
	logger.debug('Connection to DB for host "{0}" obtained succsessfully'.format(self.db_name))
	return True


    def obtain_database_connection(self):
	if self.db_conn is None:
#	    logger.debug("Requested PROD connection does not exists. Trying to create...")
	    if self.get_self_db_conn():
#		logger.debug("Created new PROD connection handler for database {0}".format(self.db_name))
		return self.db_conn
#	logger.debug("Returning PROD connection handler object: {0}".format(self.db_conn))
	return self.db_conn


    def discover_database(self):
	if self.db_conn is None:
	    if self.get_self_db_conn():
		l_cursor = self.db_conn.cursor()
	    else:
		return
	else:
	    l_cursor = self.db_conn.cursor()
	try:
	    l_cursor.execute("SELECT oid,nspname FROM pg_namespace WHERE nspname NOT IN ('pg_catalog', 'information_schema') AND nspname !~ '^pg_toast' AND nspname !~ '^pg_temp'")
	except Exception, e:
	    logger.error("Cannot execute database discover queries for db: {0}".format(self.db_name))
	    logger.error('Details: {0}{1}'.format(e.pgcode,e.pgerror))
	    return
	exist_sch=self.schemaname_set.values('id','obj_oid','sch_name').filter(alive=True)
	new_sch=l_cursor.fetchall()
	for new_s in new_sch:
	    for exist_s in exist_sch:
		if new_s[0] == exist_s['obj_oid'] and new_s[1] == exist_s['sch_name']:
		    break
	    else:
		try:
		    self.schemaname_set.create(obj_oid=new_s[0],sch_name=new_s[1])
		except (IntegrityError,DatabaseError) as msg:
		    logger.error('Cannot create new schema record for database {0}'.format(self.db_name))
		    logger.error('DETAILS: {0}'.format(msg))
		logger.info("Created new schema {0} for database {1}".format(new_s[1],self.db_name))
	for exist_s in exist_sch:
	    for new_s in new_sch:
		if new_s[0] == exist_s['obj_oid'] and new_s[1] == exist_s['sch_name']:
		    break
	    else:
		remove_sch=SchemaName.objects.get(pk=exist_s['id'])
		remove_sch.set_non_alive()
	l_cursor.close()


    def edit_description(self,new_description):
	old_desc=self.description
	self.description=new_description
	self.save()
	logger.info('Database description changed from "{0}" to "{1}"'.format(old_desc,self.description))

    def db_stat(self,time):
	if self.db_conn is None:
	    if self.get_self_db_conn():
		l_cursor = self.db_conn.cursor()
	    else:
		return
	else:
	    l_cursor = self.db_conn.cursor()
	try:
	    l_cursor.execute("""SELECT
pg_database_size(oid) AS db_size,
pg_stat_get_db_xact_commit(oid) AS xact_commit,
pg_stat_get_db_xact_rollback(oid) AS xact_rollback,
pg_stat_get_db_blocks_fetched(oid) AS blks_fetch,
pg_stat_get_db_blocks_hit(oid) AS blks_hit,
pg_stat_get_db_tuples_returned(oid) AS tup_returned,
pg_stat_get_db_tuples_fetched(oid) AS tup_fetched,
pg_stat_get_db_tuples_inserted(oid) AS tup_inserted,
pg_stat_get_db_tuples_updated(oid) AS tup_updated,
pg_stat_get_db_tuples_deleted(oid) AS tup_deleted
FROM pg_database
WHERE oid ={0}""".format(self.obj_oid))
	except Exception, e:
	    logger.error("Cannot execute database stat queries for db: {0}".format(self.db_name))
	    logger.error('Details: {0}{1}'.format(e.pgcode,e.pgerror))
	    return
	stat=l_cursor.fetchone()
	logger.debug('Database stat results for DB {0}:\n\t{1}'.format(self.db_name,stat))
	try:
	    self.databasestat_set.create(time_id=time,
    db_size = stat[0],
    xact_commit = stat[1],
    xact_rollback = stat[2],
    blks_fetch = stat[3],
    blks_hit = stat[4],
    tup_returned = stat[5],
    tup_fetched = stat[6],
    tup_inserted = stat[7],
    tup_updated = stat[8],
    tup_deleted = stat[9])
	except (IntegrityError,DatabaseError) as msg:
	    logger.error('Cannot create database stat record for database {0}'.format(self.db_name))
	    logger.error('DETAILS: {0}'.format(msg))
	    pass
	logger.debug('Database stat results saved')
	l_cursor.close()


    def __del__(self):
	if self.db_conn is not None:
	    self.db_conn.close()



###################################################################################################

class SchemaName(models.Model):
    dn = models.ForeignKey(DatabaseName)
    obj_oid = models.IntegerField()
    observable = models.BooleanField(default=True)
    alive = models.BooleanField(default=True)
    sch_name = models.CharField(max_length=30)
    description = models.TextField(null=True)
    class Meta:
	db_table = 'schema_name'

    def set_non_alive(self):
	self.alive=False
	logger.info('Schema "{0}" disabled. Set "alive=False"'.format(self.sch_name))
	self.save()

    def discover_schema_tables(self,db_conn):
	exist_tbls=self.tablename_set.values('id','obj_oid','tbl_name').filter(alive=True)
	r_cursor=db_conn.cursor()
	try:
	    r_cursor.execute("""SELECT r.oid,r.relname,r.reltoastrelid,
    CASE WHEN h.inhrelid IS NULL THEN 'f'::boolean ELSE 't'::boolean END AS has_parent
    FROM pg_class r
    LEFT JOIN pg_inherits h ON r.oid=h.inhrelid
    WHERE r.relkind='r'
    AND r.relnamespace={0}""".format(self.obj_oid))
	except Exception, e:
	    logger.error("Cannot execute table discovery query for schema: {0}".format(self.sch_name))
	    logger.error("Details: {0}{1}".format(e.pgcode,e.pgerror))
	    return
	new_tbls=r_cursor.fetchall()
	for new_t in new_tbls:
	    for exist_t in exist_tbls:
		if new_t[0]==exist_t['obj_oid'] and new_t[1]==exist_t['tbl_name']:
		    break
	    else:
		try:
		    new_table_obj=self.tablename_set.create(obj_oid=new_t[0],tbl_name=new_t[1],has_parent=new_t[3])
		except (IntegrityError,DatabaseError) as msg:
		    logger.error('Cannot create new table record for schema {0}'.format(self.sch_name))
		    logger.error('DETAILS: {0}'.format(msg))
		logger.info("New table created {0} for schema {1}".format(new_t[1],self.sch_name))
	for exist_t in exist_tbls:
	    for new_t in new_tbls:
		if new_t[0]==exist_t['obj_oid'] and new_t[1]==exist_t['tbl_name']:
		    break
	    else:
		remove_tbl=TableName.objects.get(pk=exist_t['id'])
		remove_tbl.set_non_alive()
	r_cursor.close()
	for exist_t in self.tablename_set.filter(alive=True):
	    exist_t.discover_indexes(db_conn)
	    exist_t.discover_toast_table(db_conn)


    def discover_schema_functions(self,prod_conn):
	r_cursor=prod_conn.cursor()
	exist_funcs=self.functionname_set.values('id','pro_oid','func_name').filter(alive=True)
	try:
	    r_cursor.execute("""SELECT p.oid AS pro_oid,p.proname AS funcname,p.proretset,t.typname,l.lanname
    FROM pg_proc p
    LEFT JOIN pg_namespace n ON n.oid = p.pronamespace
    JOIN pg_type t ON p.prorettype=t.oid
    JOIN pg_language l ON p.prolang=l.oid
    WHERE (p.prolang <> (12)::oid)
    AND n.oid=%s""",(self.obj_oid,))
	except Exception, e:
	    logger.error("Cannot execute function discovery query for schema: {0}".format(self.hostname))
	    logger.error("Details: {0}{1}".format(e.pgcode,e.pgerror))
	    return
	new_funcs=r_cursor.fetchall()
	for new_f in new_funcs:
	    for exist_f in exist_funcs:
		if new_f[0]==exist_f['pro_oid'] and new_f[1]==exist_f['func_name']:
		    break
	    else:
		self.functionname_set.create(pro_oid=new_f[0],func_name=new_f[1],proretset=new_f[2],prorettype=new_f[3],prolang=new_f[4])
	for exist_f in exist_funcs:
	    for new_f in new_funcs:
		if new_f[0]==exist_f['pro_oid'] and new_f[1]==exist_f['func_name']:
		    break
	    else:
		remove_func=FunctionName.objects.get(pk=exist_f['id'])
		remove_func.set_non_alive()
	r_cursor.close()

###################################################################################################

class FunctionName(models.Model):
    sn = models.ForeignKey(SchemaName)
    pro_oid = models.IntegerField()
    proretset = models.BooleanField()
    alive = models.BooleanField(default=True)
    func_name = models.CharField(max_length=30)
    prorettype = models.CharField(max_length=30)
    prolang = models.CharField(max_length=30)
    description = models.TextField()

    class Meta:
        db_table = 'function_name'

    def set_non_alive(self):
	self.alive=False
	logger.info('Function "{0}" disabled. Set "alive=False"'.format(self.func_name))
	self.save()

    def func_stat(self,time,prod_conn):
	r_cursor=prod_conn.cursor()
	try:
	    r_cursor.execute("""SELECT
COALESCE(pg_stat_get_function_calls(oid),0) AS func_calls,
COALESCE((pg_stat_get_function_time(oid)),0) AS total_time,
COALESCE((pg_stat_get_function_self_time(oid)),0) AS self_time
FROM pg_proc
WHERE oid={0}""".format(self.pro_oid))
	except Exception,e:
	    logger.error("Cannot execute stat queries for function: {0}".format(self.func_name))
	    logger.error('Details: {0}{1}'.format(e.pgcode,e.pgerror))
	    return
	stat=r_cursor.fetchone()
	try:
	    self.functionstat_set.create(time_id=time,
    func_calls = stat[0],
    total_time = stat[1],
    self_time = stat[2])
	except (IntegrityError,DatabaseError) as msg:
	    logger.error('Cannot create stat record for function {0}'.format(self.func_name))
	    logger.error('DETAILS: {0}'.format(msg))
	    pass
#	logger.debug('Function stat results saved. Function: {0}'.format(self.func_name))
	r_cursor.close()


###################################################################################################


class TableName(models.Model):
    sn = models.ForeignKey(SchemaName)
    obj_oid = models.IntegerField()
    has_parent = models.BooleanField()
    alive = models.BooleanField(default=True)
    tbl_name = models.CharField(max_length=30)
    class Meta:
        db_table = 'table_name'

    def set_non_alive(self):
	self.alive=False
	logger.info('Table "{0}" disabled. Set "alive=False"'.format(self.tbl_name))
	self.save()

    def discover_indexes(self,prod_conn):
	exist_idxs=self.indexname_set.values('id','obj_oid','idx_name').filter(alive=True)
	r_cursor=prod_conn.cursor()
	try:
	    r_cursor.execute("""SELECT i.indexrelid,c.relname,i.indisunique,i.indisprimary
    FROM pg_index i
    JOIN pg_class c ON i.indexrelid=c.oid
    WHERE i.indrelid={0}""".format(self.obj_oid))
	except Exception,e:
	    logger.error("Cannot execute index discovery query for table: {0}".format(self.tbl_name))
	    logger.error("Details: {0}{1}".format(e.pgcode,e.pgerror))
	    return
	new_idxs=r_cursor.fetchall()
	for new_i in new_idxs:
	    for exist_i in exist_idxs:
		if new_i[0]==exist_i['obj_oid'] and new_i[1]==exist_i['idx_name']:
		    break
	    else:
		try:
		    self.indexname_set.create(obj_oid=new_i[0],idx_name=new_i[1],is_unique=new_i[2],is_primary=new_i[3])
		except (IntegrityError,DatabaseError) as msg:
		    logger.error('Cannot create stat record for table {0}'.format(self.tbl_name))
		    logger.error('DETAILS: {0}'.format(msg))
		    return
		logger.info("Added new index: {0} for table: {1}".format(new_i[1],self.tbl_name))
	for exist_i in exist_idxs:
	    for new_i in new_idxs:
		if new_i[0]==exist_i['obj_oid'] and new_i[1]==exist_i['idx_name']:
		    break
	    else:
		remove_ind=IndexName.objects.get(pk=exist_i['id'])
		remove_ind.set_non_alive()
	r_cursor.close()


    def discover_toast_table(self,prod_conn):
	exist_tt=self.tabletoastname_set.filter(alive=True)
	r_cursor=prod_conn.cursor()
	try:
	    r_cursor.execute("""SELECT r.reltoastrelid,t.relname
    FROM pg_class r
    INNER JOIN pg_class t ON r.reltoastrelid=t.oid
    WHERE r.relkind='r'
    AND t.relkind='t'
    AND r.oid={0}""".format(self.obj_oid))
	except Exception, e:
	    logger.error("Cannot execute toast discovery query for table: {0}".format(self.tbl_name))
	    logger.error('Details: {0}{1}'.format(e.pgcode,e.pgerror))
	    return
	new_tt=r_cursor.fetchone()
	if new_tt and exist_tt:
	    if new_tt[0] != exist_tt[0].obj_oid and new_tt[1] != exist_tt[0].tbl_name:
		exist_tt[0].set_non_alive()
		try:
		    self.tabletoastname_set.create(obj_oid=new_tt[0],tbl_name=new_tt[1])
		except (IntegrityError,DatabaseError) as msg:
		    logger.error('Cannot create toast table record for table {0}'.format(self.tbl_name))
		    logger.error('DETAILS: {0}'.format(msg))
		    pass
		logger.info("Created TOAST table {0} for relation {1}".format(new_tt[1],self.tbl_name))
	elif new_tt and not exist_tt:
	    try:
		self.tabletoastname_set.create(obj_oid=new_tt[0],tbl_name=new_tt[1])
	    except (IntegrityError,DatabaseError) as msg:
		logger.error('Cannot create toast table record for table {0}'.format(self.tbl_name))
		logger.error('DETAILS: {0}'.format(msg))
		pass
	    logger.info("Created TOAST table {0} for relation {1}".format(new_tt[1],self.tbl_name))
	elif not new_tt and exist_tt:
	    exist_tt[0].set_non_alive()
	r_cursor.close()
	for tt in self.tabletoastname_set.filter(alive=True):
	    tt.discover_toast_index(prod_conn)


    def tbl_stat(self,time,prod_conn):
	r_cursor=prod_conn.cursor()
	try:
	    r_cursor.execute("""SELECT
pg_relation_size(oid) AS relsize,
reltuples::bigint,
pg_stat_get_numscans(oid) AS seq_scan,
pg_stat_get_tuples_returned(oid) AS seq_tup_read,
pg_stat_get_tuples_fetched(oid) AS seq_tup_fetch,
pg_stat_get_tuples_inserted(oid) AS n_tup_ins,
pg_stat_get_tuples_updated(oid) AS n_tup_upd,
pg_stat_get_tuples_deleted(oid) AS n_tup_del,
pg_stat_get_tuples_hot_updated(oid) AS n_tup_hot_upd,
pg_stat_get_live_tuples(oid) AS n_live_tup,
pg_stat_get_dead_tuples(oid) AS n_dead_tup,
pg_stat_get_blocks_fetched(oid) AS heap_blks_fetch,
pg_stat_get_blocks_hit(oid) AS heap_blks_hit
FROM pg_class
WHERE oid={0}""".format(self.obj_oid))
	except Exception,e:
	    logger.error("Cannot execute stat queries for table: {0}".format(self.tbl_name))
	    logger.error('Details: {0}{1}'.format(e.pgcode,e.pgerror))
	    return
	stat=r_cursor.fetchone()
	try:
	    self.tablestat_set.create(time_id=time,
    tbl_size = stat[0],
    tbl_tuples = stat[1],
    seq_scan = stat[2],
    seq_tup_read = stat[3],
    seq_tup_fetch = stat[4],
    n_tup_ins = stat[5],
    n_tup_upd = stat[6],
    n_tup_del = stat[7],
    n_tup_hot_upd = stat[8],
    n_live_tup = stat[9],
    n_dead_tup = stat[10],
    heap_blks_fetch = stat[11],
    heap_blks_hit = stat[12])
	except (IntegrityError,DatabaseError) as msg:
	    logger.error('Cannot create stat record for table {0}'.format(self.tbl_name))
	    logger.error('DETAILS: {0}'.format(msg))
	    pass
#	logger.debug('Table stat results saved. Table: {0}'.format(self.tbl_name))
	r_cursor.close()


    def tbl_va_stat(self,time,prod_conn):
	r_cursor=prod_conn.cursor()
	try:
	    r_cursor.execute("""SELECT
pg_stat_get_last_vacuum_time(oid) AS last_vacuum,
pg_stat_get_last_autovacuum_time(oid) AS last_autovacuum,
pg_stat_get_last_analyze_time(oid) AS last_analyze,
pg_stat_get_last_autoanalyze_time(oid) AS last_autoanalyze
FROM pg_class WHERE oid=%s""",(self.obj_oid,))
	except Exception,e:
	    logger.error("Cannot execute VA stat queries for table: {0}".format(self.tbl_name))
	    logger.error('Details: {0}{1}'.format(e.pgcode,e.pgerror))
	    return
	stat=r_cursor.fetchone()
	try:
	    self.tablevastat_set.create(time_id=time,
    last_vacuum = stat[0],
    last_autovacuum = stat[1],
    last_analyze = stat[2],
    last_autoanalyze = stat[3])
	except (IntegrityError,DatabaseError) as msg:
	    logger.error('Cannot create VA stat record for table {0}'.format(self.tbl_name))
	    logger.error('DETAILS: {0}'.format(msg))
	    pass
#	logger.debug('Table VA stat results saved. Table: {0}'.format(self.tbl_name))
	r_cursor.close()


###################################################################################################

class IndexName(models.Model):
    tn = models.ForeignKey(TableName)
    obj_oid = models.IntegerField()
    is_unique = models.BooleanField()
    is_primary = models.BooleanField()
    alive = models.BooleanField(default=True)
    idx_name = models.CharField(max_length=30)
    class Meta:
	db_table = 'index_name'

    def idx_stat(self,time,prod_conn):
	r_cursor=prod_conn.cursor()
	try:
	    r_cursor.execute("""SELECT
pg_relation_size(oid) AS relsize,
pg_stat_get_numscans(oid) AS idx_scan,
pg_stat_get_tuples_returned(oid) AS idx_tup_read,
pg_stat_get_tuples_fetched(oid) AS idx_tup_fetch,
pg_stat_get_blocks_fetched(oid) AS idx_blks_fetch,
pg_stat_get_blocks_hit(oid) AS idx_blks_hit
FROM pg_class WHERE oid=%s""",(self.obj_oid,))
	except Exception,e:
	    logger.error("Cannot execute stat queries for index: {0}".format(self.idx_name))
	    logger.error('Details: {0}{1}'.format(e.pgcode,e.pgerror))
	    return
	stat=r_cursor.fetchone()
	try:
	    self.indexstat_set.create(time_id=time,
    idx_size = stat[0],
    idx_scan = stat[1],
    idx_tup_read = stat[2],
    idx_tup_fetch = stat[3],
    idx_blks_fetch = stat[4],
    idx_blks_hit = stat[5])
	except (IntegrityError,DatabaseError) as msg:
	    logger.error('Cannot create index stat record for index {0}'.format(self.idx_name))
	    logger.error('DETAILS: {0}'.format(msg))
	    pass
#	logger.debug('Table VA stat results saved. Table: {0}'.format(self.tbl_name))
	r_cursor.close()


    def set_non_alive(self):
	self.alive=False
	logger.info('Index "{0}" disabled. Set "alive=False"'.format(self.idx_name))
	self.save()


###################################################################################################

class TableToastName(models.Model):
    tn = models.ForeignKey(TableName)
    obj_oid = models.IntegerField()
    alive = models.BooleanField(default=True)
    tbl_name = models.CharField(max_length=30)
    class Meta:
        db_table = 'table_toast_name'

    def tbl_toast_stat(self,time,prod_conn):
	r_cursor=prod_conn.cursor()
	try:
	    r_cursor.execute("""SELECT
pg_relation_size(oid) AS relsize,
pg_stat_get_numscans(oid) AS seq_scan,
pg_stat_get_tuples_returned(oid) AS seq_tup_read,
pg_stat_get_tuples_fetched(oid) AS seq_tup_fetch,
pg_stat_get_tuples_inserted(oid) AS n_tup_ins,
pg_stat_get_tuples_updated(oid) AS n_tup_upd,
pg_stat_get_tuples_deleted(oid) AS n_tup_del,
pg_stat_get_tuples_hot_updated(oid) AS n_tup_hot_upd,
pg_stat_get_live_tuples(oid) AS n_live_tup,
pg_stat_get_dead_tuples(oid) AS n_dead_tup,
pg_stat_get_blocks_fetched(oid) AS heap_blks_fetch,
pg_stat_get_blocks_hit(oid) AS heap_blks_hit
FROM pg_class WHERE oid=%s""",(self.obj_oid,))
	except Exception,e:
	    logger.error("Cannot execute stat queries for TOAST table: {0}".format(self.tbl_name))
	    logger.error('Details: {0}{1}'.format(e.pgcode,e.pgerror))
	    return
	stat=r_cursor.fetchone()
	try:
	    self.tabletoaststat_set.create(time_id=time,
    ttbl_size = stat[0],
    seq_scan = stat[1],
    seq_tup_read = stat[2],
    seq_tup_fetch = stat[3],
    n_tup_ins = stat[4],
    n_tup_upd = stat[5],
    n_tup_del = stat[6],
    n_tup_hot_upd = stat[7],
    n_live_tup = stat[8],
    n_dead_tup = stat[9],
    heap_blks_fetch = stat[10],
    heap_blks_hit = stat[11])
	except (IntegrityError,DatabaseError) as msg:
	    logger.error('Cannot create TOAST table stat record for table {0}'.format(self.tbl_name))
	    logger.error('DETAILS: {0}'.format(msg))
	    pass
#	logger.debug('Table VA stat results saved. Table: {0}'.format(self.tbl_name))
	r_cursor.close()



    def set_non_alive(self):
	self.alive=False
	logger.info('TOAST Table "{0}" disabled. Set "alive=False"'.format(self.tbl_name))
	self.save()

    def discover_toast_index(self,prod_conn):
	exist_it=self.indextoastname_set.filter(alive=True)
	r_cursor=prod_conn.cursor()
	try:
	    r_cursor.execute("""SELECT i.oid,i.relname
    FROM pg_class t
    INNER JOIN pg_class i ON t.reltoastidxid=i.oid
    WHERE t.relkind='t'
    AND t.oid={0}""".format(self.obj_oid))
	except Exception, e:
	    logger.error("Cannot execute toast index discovery query for table: {0}".format(self.tbl_name))
	    logger.error('Details: {0}{1}'.format(e.pgcode,e.pgerror))
	    return
	new_it=r_cursor.fetchone()
	if new_it and exist_it:
	    if new_it[0] != exist_it[0].obj_oid and new_it[1] != exist_it[0].idx_name:
		exist_it[0].set_non_alive()
		try:
		    self.indextoastname_set.create(obj_oid=new_it[0],idx_name=new_it[1])
		except (IntegrityError,DatabaseError) as msg:
		    logger.error('Cannot create toast index record for table {0}'.format(self.tbl_name))
		    logger.error('DETAILS: {0}'.format(msg))
		    pass
		logger.info("Created TOAST index {0} for relation {1}".format(new_it[1],self.tbl_name))
	elif new_it and not exist_it:
	    try:
		self.indextoastname_set.create(obj_oid=new_it[0],idx_name=new_it[1])
	    except (IntegrityError,DatabaseError) as msg:
		logger.error('Cannot create toast index record for table {0}'.format(self.tbl_name))
		logger.error('DETAILS: {0}'.format(msg))
		pass
	    logger.info("Created TOAST index {0} for relation {1}".format(new_it[1],self.tbl_name))
	elif not new_it and exist_it:
	    exist_tt[0].set_non_alive()
	r_cursor.close()

###################################################################################################

class IndexToastName(models.Model):
    tn = models.ForeignKey(TableToastName)
    obj_oid = models.IntegerField()
    alive = models.BooleanField(default=True)
    idx_name = models.CharField(max_length=30)
    class Meta:
	db_table = 'index_toast_name'

    def idx_toast_stat(self,time,prod_conn):
	r_cursor=prod_conn.cursor()
	try:
	    r_cursor.execute("""SELECT
pg_relation_size(oid) AS relsize,
pg_stat_get_numscans(oid) AS idx_scan,
pg_stat_get_tuples_returned(oid) AS idx_tup_read,
pg_stat_get_tuples_fetched(oid) AS idx_tup_fetch,
pg_stat_get_blocks_fetched(oid) AS idx_blks_fetch,
pg_stat_get_blocks_hit(oid) AS idx_blks_hit
FROM pg_class WHERE oid={0}""".format(self.obj_oid))
	except Exception,e:
	    logger.error("Cannot execute stat queries for TOAST index: {0}".format(self.idx_name))
	    logger.error('Details: {0}{1}'.format(e.pgcode,e.pgerror))
	    return
	stat=r_cursor.fetchone()
	try:
	    self.indextoaststat_set.create(time_id=time,
    tidx_size = stat[0],
    tidx_scan = stat[1],
    tidx_tup_read = stat[2],
    tidx_tup_fetch = stat[3],
    tidx_blks_fetch = stat[4],
    tidx_blks_hit = stat[5])
	except (IntegrityError,DatabaseError) as msg:
	    logger.error('Cannot create TOAST index stat record for index {0}'.format(self.idx_name))
	    logger.error('DETAILS: {0}'.format(msg))
	    pass
#	logger.debug('Table VA stat results saved. Table: {0}'.format(self.tbl_name))
	r_cursor.close()


###################################################################################################
###################################################################################################

class LogTime(models.Model):
    actual_time = models.DateTimeField(null=True)
    hour_truncate = models.DateTimeField(null=True,unique=True)
    class Meta:
	db_table = 'log_time'

    def __init__(self,*args,**kwargs):
	logger.debug('Log time requested')
	cursor = connection.cursor()
	time_check_query="""SELECT CASE
    WHEN (SELECT COUNT(1) FROM log_time WHERE hour_truncate=(SELECT date_trunc('hour',now())::timestamp without time zone)) > 0 
	THEN NULl
    ELSE 
	LOCALTIMESTAMP END AS actual_time,
    date_trunc('hour',LOCALTIMESTAMP) as hour_truncate"""
	cursor.execute(time_check_query)
	time_data=cursor.fetchone()
	if time_data[0] is None:
	    logger.critical('Appropriate record for "{0}" already exists'.format(time_data[1]))
#	    print 'Appropriate record for "{0}" already exists'.format(time_data[1])

	    exit()
	logger.debug('Log time obtained. Actual Time: {0}\tHour Truncate: {1}'.format(time_data[0],time_data[1]))
	kwargs['actual_time']=time_data[0]
	kwargs['hour_truncate']=time_data[1]
	super(LogTime,self).__init__(*args,**kwargs)
	self.save()

###################################################################################################

class BgwriterStat(models.Model):
    hc = models.ForeignKey(HostCluster)
    time = models.ForeignKey(LogTime)
#    time = models.IntegerField()
    checkpoints_timed = models.BigIntegerField()
    checkpoints_req = models.BigIntegerField()
    buffers_checkpoint = models.BigIntegerField()
    buffers_clean = models.BigIntegerField()
    maxwritten_clean = models.BigIntegerField()
    buffers_backend = models.BigIntegerField()
    buffers_alloc = models.BigIntegerField()
    conn_string = ''
    class Meta:
	db_table = 'bgwriter_stat'


###################################################################################################

class DatabaseStat(models.Model):
    dn = models.ForeignKey(DatabaseName)
    time = models.ForeignKey(LogTime)
#    time = models.IntegerField()
    db_size = models.BigIntegerField()
    xact_commit = models.BigIntegerField()
    xact_rollback = models.BigIntegerField()
    blks_fetch = models.BigIntegerField()
    blks_hit = models.BigIntegerField()
    tup_returned = models.BigIntegerField()
    tup_fetched = models.BigIntegerField()
    tup_inserted = models.BigIntegerField()
    tup_updated = models.BigIntegerField()
    tup_deleted = models.BigIntegerField()
    class Meta:
	db_table = 'database_stat'

###################################################################################################

class TableStat(models.Model):
    tn = models.ForeignKey(TableName)
    time = models.ForeignKey(LogTime)
#    time = models.IntegerField()
    tbl_size = models.BigIntegerField()
#    tbl_total_size = models.BigIntegerField()
    tbl_tuples = models.BigIntegerField()
    seq_scan = models.BigIntegerField()
    seq_tup_read = models.BigIntegerField()
    seq_tup_fetch = models.BigIntegerField()
    n_tup_ins = models.BigIntegerField()
    n_tup_upd = models.BigIntegerField()
    n_tup_del = models.BigIntegerField()
    n_tup_hot_upd = models.BigIntegerField()
    n_live_tup = models.BigIntegerField()
    n_dead_tup = models.BigIntegerField()
    heap_blks_fetch = models.BigIntegerField()
    heap_blks_hit = models.BigIntegerField()
    class Meta:
	db_table = 'table_stat'

###################################################################################################

class TableVaStat(models.Model):
    tn = models.ForeignKey(TableName)
    time = models.ForeignKey(LogTime)
#    time = models.IntegerField()
    last_vacuum = models.DateTimeField()
    last_autovacuum = models.DateTimeField()
    last_analyze = models.DateTimeField()
    last_autoanalyze = models.DateTimeField()
    class Meta:
	db_table = 'table_va_stat'


###################################################################################################

class FunctionStat(models.Model):
    fn = models.ForeignKey(FunctionName)
    time = models.ForeignKey(LogTime)
#    time = models.IntegerField()
    func_calls = models.BigIntegerField()
    total_time = models.BigIntegerField()
    self_time = models.BigIntegerField()
    class Meta:
	db_table = 'function_stat'


###################################################################################################

class IndexStat(models.Model):
    in_id = models.ForeignKey(IndexName,db_column='in_id')
    time = models.ForeignKey(LogTime)
#    time = models.IntegerField()
    idx_size = models.BigIntegerField()
    idx_scan = models.BigIntegerField()
    idx_tup_read = models.BigIntegerField()
    idx_tup_fetch = models.BigIntegerField()
    idx_blks_fetch = models.BigIntegerField()
    idx_blks_hit = models.BigIntegerField()
    class Meta:
	db_table = 'index_stat'


###################################################################################################


class TableToastStat(models.Model):
    tn = models.ForeignKey(TableToastName)
    time = models.ForeignKey(LogTime)
#    time = models.IntegerField()
    ttbl_size = models.BigIntegerField()
    seq_scan = models.BigIntegerField()
    seq_tup_read = models.BigIntegerField()
    seq_tup_fetch = models.BigIntegerField()
    n_tup_ins = models.BigIntegerField()
    n_tup_upd = models.BigIntegerField()
    n_tup_del = models.BigIntegerField()
    n_tup_hot_upd = models.BigIntegerField()
    n_live_tup = models.BigIntegerField()
    n_dead_tup = models.BigIntegerField()
    heap_blks_fetch = models.BigIntegerField()
    heap_blks_hit = models.BigIntegerField()
    class Meta:
	db_table = 'table_toast_stat'

###################################################################################################


class IndexToastStat(models.Model):
    tn = models.ForeignKey(IndexToastName)
    time = models.ForeignKey(LogTime)
#    time = models.IntegerField()
    tidx_size = models.BigIntegerField()
    tidx_scan = models.BigIntegerField()
    tidx_tup_read = models.BigIntegerField()
    tidx_tup_fetch = models.BigIntegerField()
    tidx_blks_fetch = models.BigIntegerField()
    tidx_blks_hit = models.BigIntegerField()
    class Meta:
	db_table = u'index_toast_stat'

