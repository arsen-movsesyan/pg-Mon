import table
import settings
from tablename import TableName
from functionname import FunctionName

logger=settings.logger

class SchemaName(table.genericName):


    def __init__(self,in_db_conn,in_prod_dsn,in_id=None):
	super(SchemaName,self).__init__(in_db_conn,in_id)
	self.table='schema_name'
	if in_id:
	    self._populate()
	    self.prod_dsn=in_prod_dsn
	    self.sub_fk='sn_id'



    def discover_tables(self):
	if not self.prod_conn or self.prod_conn.closed:
	    if not self.set_prod_conn():
		return False
	cur=self.prod_conn.cursor()
	try:
	    cur.execute("""SELECT r.oid,r.relname,
CASE WHEN h.inhrelid IS NULL THEN 'f'::boolean ELSE 't'::boolean END AS has_parent
FROM pg_class r
LEFT JOIN pg_inherits h ON r.oid=h.inhrelid
WHERE r.relkind='r'
AND r.relnamespace={0}""".format(self.db_fields['obj_oid']))
	except Exception as e:
	    logger.error("Cannot execute tables discovery query on Prod: {0}".format(e.pgerror))
	    cur.close()
	    return
	prod_tbls=cur.fetchall()
	cur.close()
	cur=self.db_conn.cursor()
	try:
	    cur.execute("SELECT obj_oid,tbl_name,id FROM table_name WHERE {0}={1} AND alive".format(self.sub_fk,self.id))
	except Exception as e:
	    logger.error("Cannot execute tables discovery query on Local: {0}".format(e.pgerror))
	    cur.close()
	    return
	local_tbls=cur.fetchall()
	cur.close()
	for l_table in local_tbls:
	    for p_table in prod_tbls:
		if l_table[0]==p_table[0] and l_table[1]==p_table[1]:
		    break
	    else:
		logger.info("Retired table {0} in schema {1}".format(l_table[1],self.db_fields['sch_name']))
		old_table=TableName(self.db_conn,self.prod_dsn,l_table[2])
		old_table.retire()
	for p_table in  prod_tbls:
	    for l_table in local_tbls:
		if p_table[0]==l_table[0] and p_table[1]==l_table[1]:
		    break
	    else:
		logger.info("Created new table: {0} in schema {1}".format(p_table[1],self.db_fields['sch_name']))
		new_table=TableName(self.db_conn,self.prod_dsn)
		new_table.set_fields(sn_id=self.id,tbl_name=p_table[1],obj_oid=p_table[0],has_parent=p_table[2])
		new_table._create()
	self.db_conn.commit()


    def discover_functions(self):
	if not self.prod_conn or self.prod_conn.closed:
	    if not self.set_prod_conn():
		return False
	cur=self.prod_conn.cursor()
	try:
	    cur.execute("""SELECT p.oid AS pro_oid,p.proname AS funcname,p.proretset,t.typname,l.lanname
FROM pg_proc p
LEFT JOIN pg_namespace n ON n.oid = p.pronamespace
JOIN pg_type t ON p.prorettype=t.oid
JOIN pg_language l ON p.prolang=l.oid
WHERE (p.prolang <> (12)::oid)
AND n.oid={0}""".format(self.db_fields['obj_oid']))
	except Exception as e:
	    logger.error("Cannot execute functions discovery query on Prod: {0}".format(e.pgerror))
	    cur.close()
	    return
	prod_funcs=cur.fetchall()
	cur.close()
	cur=self.db_conn.cursor()
	try:
	    cur.execute("SELECT pro_oid,func_name,id FROM function_name WHERE {0}={1} AND alive".format(self.sub_fk,self.id))
	except Exception as e:
	    logger.error("Cannot execute functions discovery query on Local: {0}".format(e.pgerror))
	    cur.close()
	    return
	local_funcs=cur.fetchall()
	cur.close()
	for l_func in local_funcs:
	    for p_func in prod_funcs:
		if l_func[0]==p_func[0] and l_func[1]==p_func[1]:
		    break
	    else:
		logger.info("Retired function {0} in schema {1}".format(l_func[1],self.db_fields['sch_name']))
		old_func=FunctionName(self.db_conn,self.prod_dsn,l_func[2])
		old_func.retire()
	for p_func in  prod_funcs:
	    for l_func in local_funcs:
		if p_func[0]==l_func[0] and p_func[1]==l_func[1]:
		    break
	    else:
		logger.info("Created new function: {0} in schema {1}".format(p_func[1],self.db_fields['sch_name']))
		new_func=FunctionName(self.db_conn,self.prod_dsn)
		new_func.set_fields(sn_id=self.id,pro_oid=p_func[0],func_name=p_func[1],proretset=p_func[2],prorettype=p_func[3],prolang=p_func[4])
		new_func._create()
	self.db_conn.commit()



    def get_tables(self,obs=False):
	self.sub_table='table_name'
	return self.get_dependants(obs)

    def get_functions(self,obs=False):
	self.sub_table='function_name'
	return self.get_dependants(obs)
