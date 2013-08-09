
from settings import logger,db_handler

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
	self.iden_field=None
	self.db_fields={}
	self.self_cursor=db_handler.cursor()

    def set_table_name(self,table_name):
	self.table=table_name


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


    def populate(self,iden=None):
	if not iden:
	    init_stmt="SELECT * FROM {0} WHERE id={1}".format(self.table,self.id)
	else:
	    init_stmt="SELECT * FROM {0} WHERE {1}='{2}'".format(self.table,self.iden_field,iden)
	try:
	    self.self_cursor.execute(init_stmt)
	except Exception as e:
	    logger.error("Cannot execute populate query. Details: {0}".format(e))
	    return
	self.db_fields.clear()
	res=self.self_cursor.fetchone()
	desc=self.self_cursor.description
	if res:
	    self.db_fields=zip_field_names(res,desc)
	    self.id=self.db_fields['id']



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

