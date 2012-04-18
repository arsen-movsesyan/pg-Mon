from django.db import models
from django.db import connection
from django import forms
import psycopg2


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
    track_functions = models.CharField(max_length=10,null=True)
    track_functions = TrackFunctionField(null=True)
    pg_version = models.CharField(max_length=30,null=True)
    pg_data_path = models.CharField(max_length=30,null=True)
    fqdn = models.CharField(max_length=255,null=True)
    spec_comments = models.TextField(max_length=2000,null=True)
    conn_param = VarcharArrayField(max_length=255)

    def set_content_data(self,in_data):
	self.model_data=in_data

    def set_non_alive(self):
	self.alive=False
	self.save()

    def toggle_observable(self):
	if self.observable:
	    self.observable=False
	else:
	    self.observable=True
	self.save()

    def discover_cluster(self):
	conn=psycopg2.connect(self.get_conn_string())
	cur=conn.cursor()
	cur.execute("SELECT current_setting('server_version') AS ver")
	self.pg_version=cur.fetchone()[0]
	cur.execute("SELECT current_setting('data_directory') AS pg_data_path")
	self.pg_data_path=cur.fetchone()[0]
	cur.execute("SELECT CASE WHEN current_setting('track_counts')='on' THEN 't'::boolean ELSE 'f'::boolean END AS track_counts")
	self.track_counts=cur.fetchone()[0]
	cur.execute("SELECT current_setting('track_functions') AS track_functions")
	self.track_functions=str(cur.fetchone()[0])
	self.save()

	exist_dbs=self.databasename_set.values('id','obj_oid','db_name').filter(alive=True)

	cur.execute("SELECT oid,datname FROM pg_database WHERE NOT datistemplate AND datname !='postgres'")
	new_dbs=cur.fetchall()
	for new_db in new_dbs:
	    for exist_db in exist_dbs:
		if new_db[0] == exist_db['obj_oid'] and new_db[1] == exist_db['db_name']:
		    break
	    else:
		db=self.databasename_set.create(obj_oid=new_db[0],db_name=new_db[1])
	for exist_db in exist_dbs:
	    for new_db in new_dbs:
		if new_db[0] == exist_db['obj_oid'] and new_db[1] == exist_db['db_name']:
		    break
	    else:
		drop_db=DatabaseName.objects.get(pk=exist_db['id'])
		drop_db.set_non_alive()

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
	return ret[:-1]

    def get_conn_param(self,name):
	for param in self.conn_param:
	    k_v=param.split("=")
	    if k_v[0]==name:
		return k_v[1]
	return False

    class Meta:
	db_table = 'host_cluster'

    def bg_stat(self,time):
	try:
	    conn=psycopg2.connect(self.get_conn_string())
	except Exception, e:
	    pass
	if e.pgerror != None:
	    print e.pgcode
	    print e.pgerror
	    return
	cursor = conn.cursor()
	try:
	    cursor.execute("""SELECT
pg_stat_get_bgwriter_timed_checkpoints() AS checkpoints_timed,
pg_stat_get_bgwriter_requested_checkpoints() AS checkpoints_req,
pg_stat_get_bgwriter_buf_written_checkpoints() AS buffers_checkpoint,
pg_stat_get_bgwriter_buf_written_clean() AS buffers_clean,
pg_stat_get_bgwriter_maxwritten_clean() AS maxwritten_clean,
pg_stat_get_buf_written_backend() AS buffers_backend,
pg_stat_get_buf_alloc() AS buffers_alloc""")
	except Exception, e:
	    pass
	if e.pgerror != None:
	    print e.pgcode
	    print e.pgerror
	    return
	stat=cursor.fetchone()
	self.bgwriterstat_set.create(time_id=time
	,checkpoints_timed=stat[0]
	,checkpoints_req=stat[1]
	,buffers_checkpoint=stat[2]
	,buffers_clean=stat[3]
	,maxwritten_clean=stat[4]
	,buffers_backend=stat[5]
	,buffers_alloc=stat[6])

    def cluster_queries(self):
	conn=psycopg2.connect(self.get_conn_string())
	cursor = conn.cursor()
	cursor.execute("""SELECT now()-query_start AS duration,datname,procpid,usename,client_addr,
	CASE WHEN char_length(current_query)>110 THEN substring(current_query from 0 for 110)||'...'
	ELSE current_query
	END AS cur_query FROM pg_stat_activity WHERE current_query!='<IDLE>' AND NOT procpid=pg_backend_pid() ORDER BY 1 DESC""")
	queries = cursor.fetchall()
	return queries


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

    def set_non_alive(self):
	self.alive=False
	self.save()

    def toggle_observable(self):
	if self.observable:
	    self.observable=False
	else:
	    self.observable=True
	self.save()

    def get_conn_string(self):
	from django.db import connection
	cursor=connection.cursor()
	cursor.execute("SELECT get_conn_string(%s,%s)",[self.hc_id,self.id])
	conn_string=cursor.fetchone()[0]
	return conn_string

    def discover_database(self):
	conn=psycopg2.connect(self.get_conn_string())
	cur=conn.cursor()
	exist_sch=self.schemaname_set.values('id','obj_oid','sch_name').filter(alive=True)
	cur.execute("SELECT oid,nspname FROM pg_namespace WHERE nspname NOT IN ('pg_catalog', 'information_schema') AND nspname !~ '^pg_toast' AND nspname !~ '^pg_temp'")
	new_sch=cur.fetchall()

	for new_s in new_sch:
	    for exist_s in exist_sch:
		if new_s[0] == exist_s['obj_oid'] and new_s[1] == exist_s['sch_name']:
		    break
	    else:
		self.schemaname_set.create(obj_oid=new_s[0],sch_name=new_s[1])
	for exist_s in exist_sch:
	    for new_s in new_sch:
		if new_s[0] == exist_s['obj_oid'] and new_s[1] == exist_s['sch_name']:
		    break
	    else:
		remove_sch=SchemaName.objects.get(pk=exist_s['id'])
		remove_sch.set_non_alive()
#		exist_s.set_non_alive()


    def edit_description(self,new_description):
	self.description=new_description
	self.save()

    class Meta:
	db_table = 'database_name'

    def db_stat(self,time):
	conn=psycopg2.connect(self.get_conn_string())
	cursor=conn.cursor()
	cursor.execute("""SELECT
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
WHERE oid =%s""",(self.obj_oid,))
	stat=cursor.fetchone()
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
	self.save()

    def discover_schema_tables(self,conn_string):
	conn=psycopg2.connect(conn_string)
	exist_tbls=self.tablename_set.values('id','obj_oid','tbl_name').filter(alive=True)
	cur=conn.cursor()

	cur.execute("""SELECT r.oid,r.relname,r.reltoastrelid,
    CASE WHEN h.inhrelid IS NULL THEN 'f'::boolean ELSE 't'::boolean END AS has_parent
    FROM pg_class r
    LEFT JOIN pg_inherits h ON r.oid=h.inhrelid
    WHERE r.relkind='r'
    AND r.relnamespace=%s""",(self.obj_oid,))
	new_tbls=cur.fetchall()
	for new_t in new_tbls:
	    for exist_t in exist_tbls:
		if new_t[0]==exist_t['obj_oid'] and new_t[1]==exist_t['tbl_name']:
		    break
	    else:
		new_table_obj=self.tablename_set.create(obj_oid=new_t[0],tbl_name=new_t[1],has_parent=new_t[3])
		if new_t[2]:
		    new_toast_tbl_obj=new_table_obj.create_toast(conn_string,new_t[2])
		new_table_obj.discover_indexes(conn_string)

	for exist_t in exist_tbls:
	    for new_t in new_tbls:
		if new_t[0]==exist_t['obj_oid'] and new_t[1]==exist_t['tbl_name']:
		    break
	    else:
		remove_tbl=TableName.objects.get(pk=exist_t['id'])
		remove_tbl.set_non_alive()


    def discover_schema_functions(self,conn_string):
	conn=psycopg2.connect(conn_string)
	exist_funcs=self.functionname_set.values('id','pro_oid','func_name').filter(alive=True)
	cur=conn.cursor()

	cur.execute("""SELECT p.oid AS pro_oid,p.proname AS funcname,p.proretset,t.typname,l.lanname
    FROM pg_proc p
    LEFT JOIN pg_namespace n ON n.oid = p.pronamespace
    JOIN pg_type t ON p.prorettype=t.oid
    JOIN pg_language l ON p.prolang=l.oid
    WHERE (p.prolang <> (12)::oid)
    AND n.oid=%s""",(self.obj_oid,))

	new_funcs=cur.fetchall()
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
	self.save()

    def func_stat(self,time,conn_string):
	conn=psycopg2.connect(conn_string)
	cursor=conn.cursor()
	cursor.execute("""SELECT
COALESCE(pg_stat_get_function_calls(oid),0) AS func_calls,
COALESCE((pg_stat_get_function_time(oid)),0) AS total_time,
COALESCE((pg_stat_get_function_self_time(oid)),0) AS self_time
FROM pg_proc
WHERE oid=%s""",(self.pro_oid,))
	stat=cursor.fetchone()
	self.functionstat_set.create(time_id=time,
    func_calls = stat[0],
    total_time = stat[1],
    self_time = stat[2])


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
	self.save()

    def discover_indexes(self,conn_string):
	conn=psycopg2.connect(conn_string)
	exist_idxs=self.indexname_set.values('id','obj_oid','idx_name').filter(alive=True)
	cur=conn.cursor()
	cur.execute("""SELECT i.indexrelid,c.relname,i.indisunique,i.indisprimary
    FROM pg_index i
    JOIN pg_class c ON i.indexrelid=c.oid
    WHERE i.indrelid=%s""",(self.obj_oid,))
	new_idxs=cur.fetchall()
	for new_i in new_idxs:
	    for exist_i in exist_idxs:
		if new_i[0]==exist_i['obj_oid'] and new_i[1]==exist_i['idx_name']:
		    break
	    else:
		self.indexname_set.create(obj_oid=new_i[0],idx_name=new_i[1],is_unique=new_i[2],is_primary=new_i[3])
	for exist_i in exist_idxs:
	    for new_i in new_idxs:
		if new_i[0]==exist_i['obj_oid'] and new_i[1]==exist_i['idx_name']:
		    break
	    else:
		remove_ind=IndexName.objects.get(pk=exist_i['id'])
		remove_ind.set_non_alive()

    def create_toast(self,conn_string,toast_relid):
	conn=psycopg2.connect(conn_string)
	cur=conn.cursor()
	cur.execute("""SELECT t.relname,t.reltoastidxid,i.relname
    FROM pg_class t
    INNER JOIN pg_class r ON r.reltoastrelid=t.oid
    INNER JOIN pg_class i ON t.reltoastidxid=i.oid
    WHERE t.oid=%s""",(toast_relid,))
	toast_res=cur.fetchone()
	tt=self.tabletoastname_set.create(obj_oid=toast_relid,tbl_name=toast_res[0])
	tt.indextoastname_set.create(obj_oid=toast_res[1],idx_name=toast_res[2])


    def tbl_stat(self,time,conn_string):
	conn=psycopg2.connect(conn_string)
	cursor=conn.cursor()
	cursor.execute("""SELECT
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
WHERE oid=%s""",(self.obj_oid,))
	stat=cursor.fetchone()
	self.tablestat_set.create(time_id=time,
    tbl_size = stat[0],
    tbl_total_size = stat[1],
    tbl_tuples = stat[2],
    seq_scan = stat[3],
    seq_tup_read = stat[4],
    seq_tup_fetch = stat[5],
    n_tup_ins = stat[6],
    n_tup_upd = stat[7],
    n_tup_del = stat[8],
    n_tup_hot_upd = stat[9],
    n_live_tup = stat[10],
    n_dead_tup = stat[11],
    heap_blks_fetch = stat[12],
    heap_blks_hit = stat[13])

    def tbl_va_stat(self,time,conn_string):
	conn=psycopg2.connect(conn_string)
	cursor=conn.cursor()
	cursor.execute("""SELECT
pg_stat_get_last_vacuum_time(oid) AS last_vacuum,
pg_stat_get_last_autovacuum_time(oid) AS last_autovacuum,
pg_stat_get_last_analyze_time(oid) AS last_analyze,
pg_stat_get_last_autoanalyze_time(oid) AS last_autoanalyze
FROM pg_class WHERE oid=%s""",(self.obj_oid,))
	stat=cursor.fetchone()
	self.tablevastat_set.create(time_id=time,
    last_vacuum = stat[0],
    last_autovacuum = stat[1],
    last_analyze = stat[2],
    last_autoanalyze = stat[3])


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

    def idx_stat(self,time,conn_string):
	conn=psycopg2.connect(conn_string)
	cursor=conn.cursor()
	cursor.execute("""SELECT
pg_relation_size(oid) AS relsize,
pg_stat_get_numscans(oid) AS idx_scan,
pg_stat_get_tuples_returned(oid) AS idx_tup_read,
pg_stat_get_tuples_fetched(oid) AS idx_tup_fetch,
pg_stat_get_blocks_fetched(oid) AS idx_blks_fetch,
pg_stat_get_blocks_hit(oid) AS idx_blks_hit
FROM pg_class WHERE oid=%s""",(self.obj_oid,))
	stat=cursor.fetchone()
	self.indexstat_set.create(time_id=time,
    idx_scan = stat[0],
    idx_tup_read = stat[1],
    idx_tup_fetch = stat[2],
    idx_blks_fetch = stat[3],
    idx_blks_hit = stat[4])

    def set_non_alive(self):
	self.alive=False
	self.save()


###################################################################################################

class TableToastName(models.Model):
    tn = models.ForeignKey(TableName,primary_key=True)
    obj_oid = models.IntegerField()
    alive = models.BooleanField(default=True)
    tbl_name = models.CharField(max_length=30)
    class Meta:
        db_table = 'table_toast_name'

    def tbl_toast_stat(self,time,conn_string):
	conn=psycopg2.connect(conn_string)
	cursor=conn.cursor()
	cursor.execute("""SELECT
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
	stat=cursor.fetchone()
	self.tabletoaststat_set.create(time_id=time,
    seq_scan = stat[0],
    seq_tup_read = stat[1],
    seq_tup_fetch = stat[2],
    n_tup_ins = stat[3],
    n_tup_upd = stat[4],
    n_tup_del = stat[5],
    n_tup_hot_upd = stat[6],
    n_live_tup = stat[7],
    n_dead_tup = stat[8],
    heap_blks_fetch = stat[9],
    heap_blks_hit = stat[10])


###################################################################################################

class IndexToastName(models.Model):
    tn = models.ForeignKey(TableToastName,primary_key=True)
    obj_oid = models.IntegerField()
    alive = models.BooleanField(default=True)
    idx_name = models.CharField(max_length=30)
    class Meta:
	db_table = 'index_toast_name'

    def idx_toast_stat(self,time,conn_string):
	conn=psycopg2.connect(conn_string)
	cursor=conn.cursor()
	cursor.execute("""SELECT
pg_relation_size(oid) AS relsize,
pg_stat_get_numscans(oid) AS idx_scan,
pg_stat_get_tuples_returned(oid) AS idx_tup_read,
pg_stat_get_tuples_fetched(oid) AS idx_tup_fetch,
pg_stat_get_blocks_fetched(oid) AS idx_blks_fetch,
pg_stat_get_blocks_hit(oid) AS idx_blks_hit
FROM pg_class WHERE oid=%s""",(self.obj_oid,))
	stat=cursor.fetchone()
	self.indextoaststat_set.create(time_id=time,
    tidx_scan = stat[0],
    tidx_tup_read = stat[1],
    tidx_tup_fetch = stat[2],
    tidx_blks_fetch = stat[3],
    tidx_blks_hit = stat[4])


###################################################################################################
###################################################################################################

class LogTime(models.Model):
    actual_time = models.DateTimeField(null=True)
    hour_truncate = models.DateTimeField(null=True,unique=True)
    class Meta:
	db_table = 'log_time'

    def __init__(self,*args,**kwargs):
	cursor = connection.cursor()
	cursor.execute("SELECT LOCALTIMESTAMP,date_trunc('hour',LOCALTIMESTAMP)")
	time_data=cursor.fetchone()
	kwargs['actual_time']=time_data[0]
	kwargs['hour_truncate']=time_data[1]
	super(LogTime,self).__init__(*args,**kwargs)


###################################################################################################

class BgwriterStat(models.Model):
    hc = models.ForeignKey(HostCluster)
    time = models.ForeignKey(LogTime)
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
    func_calls = models.BigIntegerField()
    total_time = models.BigIntegerField()
    self_time = models.BigIntegerField()
    class Meta:
	db_table = 'function_stat'


###################################################################################################

class IndexStat(models.Model):
    in_id = models.ForeignKey(IndexName,db_column='in_id')
    time = models.ForeignKey(LogTime)
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
    tbl_size = models.BigIntegerField()
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
    tidx_size = models.BigIntegerField()
    tidx_scan = models.BigIntegerField()
    tidx_tup_read = models.BigIntegerField()
    tidx_tup_fetch = models.BigIntegerField()
    tidx_blks_fetch = models.BigIntegerField()
    tidx_blks_hit = models.BigIntegerField()
    class Meta:
	db_table = u'index_toast_stat'

