
import settings
import psycopg2

logger=settings.logger

###################################################################################################
###################################################################################################

def zip_field_names(res_list,res_desc):
    f_names=[]
    for fields in res_desc:
	f_names.append(fields.name)
    return dict(zip(f_names,res_list))


class generic(object):

    def __init__(self,in_db_conn):
	self.id=None
	self.table=None
	self.db_fields={}
#	self.updated=True
	self.db_conn=in_db_conn
	self.prod_conn=None

#    def set_db_conn(self,in_db_conn):
#	self.db_conn=in_db_conn

    def set_field(self,k,v):
	self.db_fields[k]=v
#	self.updated=False

    def set_fields(self,*args,**kwargs):
	for k in kwargs.keys():
	    self.db_fields[k]=kwargs[k]
#	self.updated=False

    def set_field_dict(self,dictionary):
	self.db_fields.update(dictionary)
#	self.updated=False

    def get_field(self,field):
	for k in self.db_fields.keys():
	    if k==field:
		return self.db_fields[k]
	return None

    def get_id(self):
	return self.id

    def _create(self,in_cur=None):
	ins_stat="INSERT INTO {0} (".format(self.table)
	for column in self.db_fields.keys():
	    ins_stat+=column+','
	ins_stat=ins_stat[:-1]+") VALUES ("
	for column in self.db_fields.keys():
	    ins_stat+="%s,"
	ins_stat=ins_stat[:-1]+") RETURNING id";
	if not in_cur:
	    in_cur=self.db_conn.cursor()
#	else:
#	    cur=in_cur
	stat=in_cur.mogrify(ins_stat,(self.db_fields.values()))
	try:
	    in_cur.execute(stat)
	except Exception as e:
	    logger.error("Cannot create stat record: {0}".format(e.pgerror))
	    in_cur.close()
	    return False
	self.id=in_cur.fetchone()[0]
	in_cur.close()
	return True



    def __del__(self):
	if self.prod_conn:
	    if not self.prod_conn.closed:
		self.prod_conn.close()



class genericStat(generic):

    def __init__(self,in_table,in_fk_field,in_id):
	super(genericStat,self).__init__(None)
	self.table=in_table
	self.db_fields[in_fk_field]=in_id



class genericName(generic):

    def __init__(self,in_db_conn,in_id=None):
	super(genericName,self).__init__(in_db_conn)
	self.stat_obj=None
	self.sub_table=None
	self.sub_fk=None
	if in_id:
	    self.id=in_id
	self.stat_query=None



    def _populate(self):
	cur=self.db_conn.cursor()
	try:
	    cur.execute("SELECT * FROM {0} WHERE id=%s".format(self.table),(self.id,))
	except Exception as e:
	    logger.error("Cannot populate host cluster with id {0}. {1}".format(self.id,e.pgerror))
	    cur.close()
	    return
	res=cur.fetchone()
	self.db_fields=zip_field_names(res,cur.description)
	cur.close()



    def get_dependants(self,obs=False):
	ids=[]
	dependant_q="SELECT id FROM {0} WHERE {1}={2} AND alive".format(self.sub_table,self.sub_fk,self.id)
	if obs:
	    dependant_q+=" AND observable"
	cur=self.db_conn.cursor()
	try:
	    cur.execute(dependant_q)
	except Exception as e:
	    logger.error(e.pgerror)
	else:
	    for ref in cur.fetchall():
		ids.append(ref[0])
	    cur.close()
	return ids



    def set_prod_conn(self):
	try:
	    self.prod_conn=psycopg2.connect(self.prod_dsn)
	except Exception as e:
	    logger.warning("Cannot connect to production DB: {0}".format(self.prod_dsn))
	    logger.warning("Error: {0}".format(e))
	    return False
	return True



    def stat(self,in_time_id):
	if not self.prod_conn or self.prod_conn.closed:
	    if not self.set_prod_conn():
		return False
	cur=self.prod_conn.cursor()
#	print self.stat_query
	try:
	    cur.execute(self.stat_query)
	except Exception as e:
	    logger.error("Canot get statistic info: {0}".format(e.pgerror))
	    return
	self.stat_obj.set_field_dict(zip_field_names(cur.fetchone(),cur.description))
	self.stat_obj.set_field('time_id',in_time_id)
	cur.close()
	if self.stat_obj._create(self.db_conn.cursor()):
#	if self.stat_obj._create():
	    self.db_conn.commit()



    def retire(self):
	if self.id:
	    cur=self.db_conn.cursor()
	    upd_stat=cur.mogrify("UPDATE {0} SET alive=FALSE WHERE id=%s".format(self.table),(self.id,))
	    try:
		cur.execute(upd_stat)
	    except Exception as e:
		logger.error("Cannot retire object from table {0}. {1}".format(self.table,e.pgerror))
	    cur.close()




class genericEnum(object):

    def __init__(self,in_table,in_cursor):
	self.table=in_table
	try:
	    in_cursor.execute("SELECT * FROM {0}".format(in_table))
	except Exception as e:
	    logger.error("Canot get ENUM info for table {0}: {1}".format(in_table,e))
	    self.data_array=None
	else:
	    self.data_array=in_cursor.fetchall()
	in_cursor.close()


    def get_id_by_name(self,seek_name):
	if self.data_array:
	    for row in self.data_array:
		if row[1] == seek_name:
		    return row[0]
	return None

    def get_name_by_id(self,seek_id):
	if self.data_array:
	    for row in self.data_array:
		if row[0] == seek_id:
		    return row[1]
	return None
