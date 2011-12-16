from django.db import models
from django import forms


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
	import psycopg2
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
	import psycopg2
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


###################################################################################################


#class TableToastName(models.Model):
#    tn = models.ForeignKey(TableName)
#    obj_oid = models.IntegerField()
#    alive = models.BooleanField()
#    tbl_name = models.CharField(max_length=-1)
#    class Meta:
#        db_table = u'table_toast_name'


###################################################################################################

#class IndexToastName(models.Model):
#    tn = models.ForeignKey(TableToastName)
#    obj_oid = models.IntegerField()
#    alive = models.BooleanField()
#    idx_name = models.CharField(max_length=-1)
#    class Meta:
#	db_table = u'index_toast_name'

