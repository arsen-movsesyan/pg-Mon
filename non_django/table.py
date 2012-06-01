import database
from Logger import logger

###################################################################################################
###################################################################################################

def zip_field_names(res_list,res_desc):
    f_names=[]
    for fields in res_desc:
	f_names.append(fields.name)
    return dict(zip(f_names,res_list))


class generic(object):
    table=None
    id=None
    fk_field=None
    fk_value=None
    db_fields={}
    cursor=database.db_conn.cursor()

    def set_fields(self,*args,**kwargs):
	for k in kwargs.keys():
	    self.db_fields[k]=kwargs[k]

    def set_field_dict(self,dictionary):
	self.db_fields.update(dictionary)

    def get_field(self,field):
	for k in self.db_fields.keys():
	    if k==field:
		return self.db_fields[k]
	return None


    def get_id(self):
	return self.id


    def set_table_name(self,table_name):
	self.table=table_name


    def create(self):
	if not self.id:
	    ins_stat="INSERT INTO {0} (".format(self.table)
	    fields=self.db_fields.keys()
	    for column in fields:
		ins_stat+=column+','
	    ins_stat=ins_stat[:-1]+") VALUES ("
	    for column in fields:
		ins_stat+="%s,"
	    ins_stat=ins_stat[:-1]+") RETURNING id";
	    stat=self.cursor.mogrify(ins_stat,(self.db_fields.values()))
	    try:
		self.cursor.execute(stat)
	    except Exception as e:
		logger.error("Cannot create record: {0}".format(e.pgerror))
		return
	    logger.debug("Created new object with statement: {0}".format(stat))
	    self.id=self.cursor.fetchone()[0]


    def truncate(self):
	self.db_fields.clear()


    def set_fk_field(self,fk_field):
	self.fk_field=fk_field


class genericStat(generic):

    def set_time_id(self,time_id):
	self.db_fields['time_id']=time_id

    def set_fk_value(self,fk_id):
	self.db_fields[self.fk_field]=fk_id


class genericName(generic):
    sub_table=None
    sub_fk=None
    prod_cursor=None
#    stat_obj=genericStat()

    def __init__(self,id=None):
	self.stat_obj=genericStat()
	if id:
	    self.id=id
	    self._populate()
	super(genericName,self).__init__()

    def _populate(self):
	init_stat="SELECT * FROM {0} WHERE id={1}".format(self.table,self.id)
#	print init_stat
	try:
	    self.cursor.execute(init_stat)
	except Exception as e:
	    logger.error(e)
	    return
	res=self.cursor.fetchone()
	self.db_fields=zip_field_names(res,self.cursor.description)


    def create_stat(self,time_id,stat_sql,cur):
	try:
	    cur.execute(stat_sql)
	except Exception, e:
	    logger.warning("Details: {0},{1}".format(e.pgcode,e.pgerror))
	    return
	result=cur.fetchone()
	desc=cur.description
	self.stat_obj.set_fk_value(self.id)
	self.stat_obj.set_time_id(time_id)
	self.stat_obj.set_field_dict(zip_field_names(result,desc))
	self.stat_obj.create()
	self.stat_obj.truncate()


    def get_dependants(self,obs=None):
	select_stat="SELECT id FROM {0} WHERE {1}={2} AND alive".format(self.sub_table,self.sub_fk,self.id)
	if obs:
	    select_stat+=" AND observable"
	try:
	    self.cursor.execute(select_stat)
	except Exception as e:
	    logger.error(e.pgerror)
	    return
	ids=[]
	for ref in self.cursor.fetchall():
	    ids.append(ref[0])
	return ids


    def update_record(self,upd_stat):
	try:
	    self.cursor.execute(upd_stat)
	except Exception as e:
	    logger.error("Cannot update {0}\nDetails: {1}\nQuery: {2}".format(self.table,e.pgerror,upd_stat))
	    return

    def retire(self):
	if self.id:
	    upd_stat="UPDATE {0} SET alive=FALSE WHERE id={1}".format(self.table,self.id)
#	    print upd_stat
	    try:
		self.cursor.execute(upd_stat)
	    except Exception as e:
		logger.error("Cannot retire table {0}. {1}".format(self.table,e.pgerror))
		return

    def toggle_observable(self,obs=True):
	if self.id:
	    upd_stat="UPDATE {0} SET observable={1} WHERE id={2}".format(self.table,obs,self.id)
	    try:
		self.cursor.execute(upd_stat)
	    except Exception as e:
		logger.error("Cannot update table {0}. {1}".format(self.table,e.pgerror))
		return


class genericEnum(generic):
#    id_field=None
#    name_field=None
#    desc_field=None

    def __init__(self,en_table):
	self.set_table_name(en_table)
	self.cursor.execute("SELECT * FROM {0}".format(en_table))
	self.data_array=self.cursor.fetchall()
	names=self.cursor.description
#	self.id_field=names[0]['name']
#	self.name_field=names[1]['name']
#	self.desc_field=names[2]['name']


    def set_fields(self,*args,**kwargs):
	pass

    def set_field_dict(self,dictionary):
	pass

    def create(self):
	pass

    def truncate(self):
	pass


    def get_id_by_name(self,seek_name):
	for row in self.data_array:
	    if row[1] == seek_name:
		return row[0]
	return None

    def get_name_by_id(self,seek_id):
	for row in self.data_array:
	    if row[0] == seek_id:
		return row[1]
	return None

