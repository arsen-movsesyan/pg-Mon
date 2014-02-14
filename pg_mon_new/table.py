
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
	self.db_conn=in_db_conn
	self.prod_dsn=None
	self.prod_conn=None


    def set_field(self,k,v):
	self.db_fields[k]=v


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


    def set_prod_dsn(self,in_prod_dsn):
	self.prod_dsn=in_prod_dsn

    def get_id(self):
	return self.id


    def _get_cursor(self):
	return self.db_conn.cursor()


    def _create(self):
	ins_stat="INSERT INTO {0} (".format(self.table)
	for column in self.db_fields.keys():
	    ins_stat+=column+','
	ins_stat=ins_stat[:-1]+") VALUES ("
	for column in self.db_fields.keys():
	    ins_stat+="%s,"
	ins_stat=ins_stat[:-1]+") RETURNING id"
	cur=self._get_cursor()
	if not cur:
	    return False
	stat=cur.mogrify(ins_stat,(self.db_fields.values()))
	try:
	    cur.execute(stat)
	except Exception as e:
	    logger.error("Cannot create stat record: {0}".format(e.pgerror))
	    cur.close()
	    self.db_conn.rollback()
	    return False
	self.id=cur.fetchone()[0]
	cur.close()
	self.db_conn.commit()
#	logger.debug("Object for table {0} created".format(self.table))
	return True


    def __del__(self):
	if self.prod_conn:
	    if not self.prod_conn.closed:
		self.prod_conn.close()



class genericStat(generic):

    def __init__(self,in_db_conn,in_table,in_fk_field,in_id):
	super(genericStat,self).__init__(in_db_conn)
	self.table=in_table
	self.db_fields[in_fk_field]=in_id



class genericName(generic):

    def __init__(self,in_db_conn,in_id=None):
	super(genericName,self).__init__(in_db_conn)
	self.stat_obj=None
	self.runtime_stat_obj=None
	self.sub_table=None
	self.sub_fk=None
	if in_id:
	    self.id=in_id
	self.stat_query=None
	self.runtime_stat_query=None



    def _populate(self):
	cur=self._get_cursor()
	if not cur:
	    return False
	try:
	    cur.execute("SELECT * FROM {0} WHERE id=%s".format(self.table),(self.id,))
	except Exception as e:
	    logger.error("Cannot populate host cluster with id {0}. {1}".format(self.id,e.pgerror))
	    cur.close()
	    self.db_conn.rollback()
	    return False
	res=cur.fetchone()
	self.db_fields=zip_field_names(res,cur.description)
	cur.close()
#	self.db_conn.commit()
#	logger.debug("Object for table {0} populated. ID: {1}".format(self.table,self.id))
	return True



    def get_dependants(self,obs=False):
	ids=[]
	dependant_q="SELECT id FROM {0} WHERE {1}={2} AND alive".format(self.sub_table,self.sub_fk,self.id)
	if obs:
	    dependant_q+=" AND observable"
	cur=self._get_cursor()
	if not cur:
	    return False
	try:
	    cur.execute(dependant_q)
	except Exception as e:
	    logger.error(" Generic get_dependants. Cannot get info about dependants: {0}".format(e.pgerror))
	    cur.close()
	    self.db_conn.rollback()
	    return False
	else:
	    refs=cur.fetchall()
	    cur.close()
	    for ref in refs:
		ids.append(ref[0])
#	logger.debug("Get dependants list for object {0} ID {1}: {2}".format(self.sub_table,self.id,ids))
	return ids



    def set_prod_conn(self):
	try:
	    self.prod_conn=psycopg2.connect(self.prod_dsn)
	except Exception as e:
	    logger.warning("Cannot connect to production DB: {0}".format(self.prod_dsn))
	    logger.warning("Error: {0}".format(e))
	    return False
#	logger.debug("Connection to prod DB established. DSN: {0}".format(self.prod_dsn))
	return True


    def _get_p_cursor(self):
	if not self.prod_conn or self.prod_conn.closed:
	    if not self.set_prod_conn():
		return False
	return self.prod_conn.cursor()


    def stat(self,in_time_id):
	p_cur=self._get_p_cursor()
	if not p_cur:
	    return False
	try:
	    p_cur.execute(self.stat_query)
	except Exception as e:
	    logger.error("Canot get statistic info: {0}".format(e.pgerror))
	    p_cur.close()
	    self.prod_conn.rollback()
	    return False
	stat_res=p_cur.fetchone()
	desc=p_cur.description
	p_cur.close()
	self.stat_obj.set_field_dict(zip_field_names(stat_res,desc))
	self.stat_obj.set_field('time_id',in_time_id)
#	logger.debug("Stat generic method")
	return self.stat_obj._create()


    def runtime_stat(self,in_time_id):
	cur=self._get_p_cursor()
	if not cur:
	    return False
	try:
	    cur.execute(self.runtime_stat_query)
	except Exception as e:
	    logger.error("Canot get runtime statistic info: {0}".format(e.pgerror))
	    cur.close()
	    self.prod_conn.rollback()
	    return False
	self.runtime_stat_obj.set_field_dict(zip_field_names(cur.fetchone(),cur.description))
	self.runtime_stat_obj.set_field('time_id',in_time_id)
	cur.close()
#	logger.debug("Runtime stat generic method")
	return self.runtime_stat_obj._create()


    def retire(self):
	if self.id:
	    cur=self._get_cursor()
	    if not cur:
		logger.error("Return from generic.retire no cur obtained")
		return False
	    upd_stat=cur.mogrify("UPDATE {0} SET alive=FALSE WHERE id=%s".format(self.table),(self.id,))
	    try:
		cur.execute(upd_stat)
	    except Exception as e:
		logger.error("Cannot retire object from table {0}. {1}".format(self.table,e.pgerror))
		cur.close()
		self.db_conn.rollback()
		return False
	    cur.close()
	return True


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
