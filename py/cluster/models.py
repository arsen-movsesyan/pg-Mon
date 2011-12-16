from django.db import models
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
	self.is_master=self.model_data['db_is_master']
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
	print "Con String = " + conn_string
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

    def discover_schema_tables(self,conn):
	exist_tbls=self.tablename_set.values('id','obj_oid','tbl_name').filter(alive=True)

#	parent_db=DatabaseName.objects.get(pk=self.dn)
#	conn=psycopg2.connect(parent_db.get_conn_string())
	cur=conn.cursor()

	cur.execute("""SELECT r.oid,r.relname,r.reltoastrelid,
    CASE WHEN h.inhrelid IS NULL THEN 'f'::boolean ELSE 't'::boolean END AS has_parent,
    CASE WHEN i.indexrelid IS NULL THEN 0::int ELSE (SELECT COUNT(1) FROM pg_index WHERE indrelid=r.oid)::int END AS indexes
    FROM pg_class r
    LEFT JOIN pg_inherits h ON r.oid=h.inhrelid
    LEFT JOIN pg_index i ON r.oid=i.indrelid
    WHERE r.relkind='r'
    AND r.relnamespace=%s GROUP BY 1,2,3,4,5
    ORDER BY 1,2,3,4,5""",self.obj_oid)
#".$self{database_fields}{obj_oid}.
	new_tbls=cur.fetchall()
	for new_t in new_tbls:
	    for exist_t in exist_tbls:
		if new_t[0]==exist_t['obj_oid'] and new_t[1]==exist_t['tbl_name']:
		    break
	    else:
		self.tablename_set.create(obj_oid=new_t[0],tbl_name=new_t[1],has_parent=new_t[3])
	for exist_t in exist_tbls:
	    for new_t in new_tbls:
		if new_t[0]==exist_t['obj_oid'] and new_t[1]==exist_t['tbl_name']:
		    break
	    else:
		remove_tbl=TableName.objects.get(pk=exist_t['id'])
		remove_tbl.set_non_alive()


    def discover_schema_functions(self,conn):
	exist_funcs=self.functionname_set.values('id','pro_oid','func_name').filter(alive=True)

#	parent_db=DatabaseName.objects.get(pk=self.dn)
#	conn=psycopg2.connect(parent_db.get_conn_string())
	cur=conn.cursor()

	cur.execute("""SELECT p.oid AS pro_oid,p.proname AS funcname,p.proretset,t.typname,l.lanname
    FROM pg_proc p
    LEFT JOIN pg_namespace n ON n.oid = p.pronamespace
    JOIN pg_type t ON p.prorettype=t.oid
    JOIN pg_language l ON p.prolang=l.oid
    WHERE (p.prolang <> (12)::oid)
    AND n.oid=%s""",self.obj_oid)

	new_funcs=cur.fetchall()
	for new_f in new_funcs:
	    for exist_f in exist_funcs:
		if new_f[0]==exist_f['pro_oid'] and new_f[1]==exist_f['func_name']:
		    break
	    else:
		self.functionname_set.create(obj_oid=new_f[0],func_name=new_f[1],proretset=new_f[2],prorettype=hew_f[3],prolang=new_f[4])
	for exist_f in exist_funcs:
	    for new_f in new_funcs:
		if new_f[0]==exist_f['pro_oid'] and new_f[1]==exist_f['func_name']:
		    break
	    else:
		remove_func=FunctionName.objects.get(pk=exist_f['id'])
		remove_func.set_non_alive()



###################################################################################################


class FunctionName(models.Model):
#    id = models.IntegerField(primary_key=True)
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

###################################################################################################


class TableName(models.Model):
#    id = models.IntegerField(primary_key=True)
    sn = models.ForeignKey(SchemaName)
    obj_oid = models.IntegerField()
    has_parent = models.BooleanField()
    alive = models.BooleanField()
    tbl_name = models.CharField(max_length=30)
    class Meta:
        db_table = 'table_name'

    def set_non_alive(self):
	self.alive=False
	self.save()

    def discover_table_indexes(self,conn):
	exist_idxs=self.indexname_set.values('id','obj_oid','idx_name').filter(alive=True)
	cur=conn.cursor()
	cur.execute("""SELECT i.indexrelid,c.relname,i.indisunique,i.indisprimary
    FROM pg_index i
    JOIN pg_class c ON i.indexrelid=c.oid
    WHERE i.indrelid=%s""",self.obj_oid)
	new_idxs=cur.fetchall()
	for new_i in new_idxs:
	    for exist_i in exist_idxs:
		if new_i[0]==exist_i['obj_id'] and new_i[1]==exist_i['idx_name']:
		    break
	    else:
		self.indexname_set.create(obj_oid=new_i[0],idx_name=new_i[1],is_unique=new_i[2],is_primary=new_i[3])
	for exist_i in exist_idxs:
	    for new_i in new_idxs:
		if new_i[0]==exist_i['obj_id'] and new_i[1]==exist_i['idx_name']:
		    break
	    else:
		remove_ind=IndexName.objects.get(pk=exist_i['id'])
		remove_ind.set_non_alive()

###################################################################################################


class IndexName(models.Model):
#    id = models.IntegerField(primary_key=True)
    tn = models.ForeignKey(TableName)
    obj_oid = models.IntegerField()
    is_unique = models.BooleanField()
    is_primary = models.BooleanField()
    alive = models.BooleanField()
    idx_name = models.CharField(max_length=30)
    class Meta:
	db_table = 'index_name'

    def set_non_alive(self):
	self.alive=False
	self.save()


###################################################################################################


class TableToastName(models.Model):
    tn = models.ForeignKey(TableName,primary_key=True)
    obj_oid = models.IntegerField()
    alive = models.BooleanField()
    tbl_name = models.CharField(max_length=-1)
    class Meta:
        db_table = 'table_toast_name'


###################################################################################################

#class IndexToastName(models.Model):
#    tn = models.ForeignKey(TableToastName)
#    obj_oid = models.IntegerField()
#    alive = models.BooleanField()
#    idx_name = models.CharField(max_length=-1)
#    class Meta:
#	db_table = u'index_toast_name'

