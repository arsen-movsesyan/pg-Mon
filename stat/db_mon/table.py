
from settings import logger,db_handler,prod_handler


###################################################################################################
###################################################################################################

def zip_field_names(res_list,res_desc):
    f_names=[]
    for fields in res_desc:
	f_names.append(fields.name)
    return dict(zip(f_names,res_list))


class generic(object):

    def __init__(self):
	self.table=None
	self.id=None
	self.fk_field=None
	self.fk_value=None
	self.db_fields={}
	self.self_cursor=db_handler.cursor()

    def set_table_name(self,table_name):
	self.table=table_name

    def set_fk_field(self,fk_field):
	self.fk_field=fk_field


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


    def __del__(self):
	if not self.self_cursor.closed:
	    self.self_cursor.close()


    def get_id(self):
	return self.id

    def populate(self):
	init_stmt="SELECT * FROM {0} WHERE id={1}".format(self.table,self.id)
	try:
	    self.self_cursor.execute(init_stmt)
	except Exception as e:
	    logger.error("Cannot execute populate query. Details: {0}".format(e))
	    return
	self.truncate()
	res=self.self_cursor.fetchone()
	desc=self.self_cursor.description
	self.db_fields=zip_field_names(res,desc)


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
	    stmt=self.self_cursor.mogrify(ins_stat,(self.db_fields.values()))
	    try:
		self.self_cursor.execute(stmt)
	    except Exception as e:
		logger.error("Cannot create record: {0}".format(e.pgerror))
		return
	    logger.debug("Created new object with statement: {0}".format(stmt))
	    self.id=self.self_cursor.fetchone()[0]

    def db_dump(self):
	return self.db_fields


    def truncate(self):
	self.db_fields.clear()




class genericStat(generic):

    def set_time_id(self,time_id):
	self.db_fields['time_id']=time_id

    def set_fk_value(self,fk_id):
	self.db_fields[self.fk_field]=fk_id



class genericName(generic):

    def __init__(self,id=None):
	super(genericName,self).__init__()
	self.sub_table=None
	self.prod_cursor=prod_handler.cursor()
	self.stat_stmt=None
	self.stat_obj=genericStat()
	if id:
	    self.id=id
#	    self._populate()



    def create(self):
	super(genericName,self).create()
	self.populate()


    def create_stat(self,time_id):
	try:
	    self.prod_cursor.execute(self.stat_stmt)
	except Exception, e:
	    logger.warning("Details: {0},{1}".format(e.pgcode,e.pgerror))
	    return
	result=self.prod_cursor.fetchone()
	desc=self.prod_cursor.description
	self.stat_obj.set_fk_value(self.id)
	self.stat_obj.set_time_id(time_id)
	self.stat_obj.set_field_dict(zip_field_names(result,desc))
	self.stat_obj.create()
	self.stat_obj.truncate()


    def get_dependants(self,alive=True):
	select_stmt="SELECT id FROM {0} WHERE {1}={2} AND alive".format(self.sub_table,self.sub_fk,self.id)
	if alive:
	    select_stmt+=" AND alive"
	try:
	    self.self_cursor.execute(select_stmt)
	except Exception as e:
	    logger.error(e.pgerror)
	    return
	ids=[]
	for ref in self.self_cursor.fetchall():
	    ids.append(ref[0])
	return ids


    def retire(self):
	if self.id:
	    upd_stat="UPDATE {0} SET alive=FALSE WHERE id={1}".format(self.table,self.id)
#	    print upd_stat
	    try:
		self.self_cursor.execute(upd_stat)
	    except Exception as e:
		logger.error("Cannot retire table {0}. {1}".format(self.table,e.pgerror))
		return



    def __del__(self):
	if self.prod_cursor:
	    if not self.prod_cursor.closed:
		self.prod_cursor.close()
	super(genericName,self).__del__()
