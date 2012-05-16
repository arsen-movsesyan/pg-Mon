#from sys import exit
#import logging
import psycopg2

#logger = logging.getLogger('pg_mon_logger')
db_conn=psycopg2.connect("host=localhost dbname=test_work user=postgres")

###################################################################################################
###################################################################################################

class generic(object):
    table=None
    id=None
    fk_field=None
    fk_value=None
    db_fields={}
#    cursor=db_conn.cursor()

    def set_fields(self,*args,**kwargs):
	for k in kwargs.keys():
	    self.db_fields[k]=kwargs[k]

    def get_field(self,field):
	for k in db_fields.keys():
	    if k==field:
		return db_fields[k]
	return None


    def create(self):
	if not self.id:
	    ins_stat="INSERT INTO {0} (".format(self.table)
	    fields=self.db_fields.keys()
	    for column in fields:
		ins_stat+=column+','
	    ins_stat=ins_stat[:-1]+") VALUES ("
	    for column in fields:
		ins_stat+="'{0}',".format(self.stat_fields[column])
	    ins_stat=ins_stat[:-1]+") RETURNING id"
	    print ins_stat
#	    try:
#		self.cursor.execute(ins_stat)
#	    except Exception as e:
#		print e.pgerror
#		return
#	    db_conn.commit()
#	    self.id=self.cursor.fetchone()[0]


class genericStat(generic):

    def __init__(self,fk_id,time_id):
	self.db_fields['time_id']=time
	self.db_fields[self.fk_field]=fk_id
	super(genericStat,self)__init__(*args,**kwargs)


class genericName(generic):

    def __init__(self,id=None):
	if id:
	    self.id=id
	    self._populate()
	super(genericName,self).__init__(*args,**kwargs)

    def _populate(self):
	init_stat="SELECT * FROM {0} WHERE id={1}".format(self.table,self.id)
	print init_stat
#	try:
#	    self.cursor.execute(upd_stat)
#	except Exception as e:
#	    print e.pgerror
#	    return
#	fields=cursor.description
#	res=cursor.fetchone()
#	f_names=[]
#	for field in fields:
#	    f_names.append(field.name)
#	self.db_fields=dict(zip(f_names,res))
#	self.id=self.db_fields['id']


    def delete(self):
	if self.id:
	    upd_stat="UPDATE {0} SET alive='f' WHERE id={1}".format(self.table,self.id)
	    print upd_stat
#	    try:
#		self.cursor.execute(upd_stat)
#	    except Exception as e:
#		print e.pgerror
#		return
#	    db_conn.commit()

