from table import genericName
from tablename import TableName
from functionname import FunctionName
from Logger import logger


class SchemaName(genericName):
    table='schema_name'
    sub_fk='sn_id'

    def __init__(self,id=None):
	if id:
	    super(SchemaName,self).__init__(id)
	else:
	    super(SchemaName,self).__init__()


    def discover_tables(self,prod_cursor):
	self.cursor.execute("SELECT obj_oid,tbl_name,id FROM table_name WHERE {0}={1} AND alive".format(self.sub_fk,self.id))
	local_tbls=self.cursor.fetchall()
	try:
	    prod_cursor.execute("""SELECT r.oid,r.relname,
CASE WHEN h.inhrelid IS NULL THEN 'f'::boolean ELSE 't'::boolean END AS has_parent
FROM pg_class r
LEFT JOIN pg_inherits h ON r.oid=h.inhrelid
WHERE r.relkind='r'
AND r.relnamespace={0}""".format(self.db_fields['obj_oid']))
	except Exception as e:
	    logger.error("Cannot execute tables discovery query: {0},{1}".format(e.pgcode,e.pgerror))
#	    prod_cursor.close()
	    return
	prod_tbls=prod_cursor.fetchall()
	for l_table in local_tbls:
	    for p_table in prod_tbls:
		if l_table[0]==p_table[0] and l_table[1]==p_table[1]:
		    break
	    else:
		logger.info("Retired table {0} in schema {1}".format(l_table[1],self.db_fields['sch_name']))
		old_table=TableName(l_table[2])
		old_table.retire()
	for p_table in  prod_tbls:
	    for l_table in local_tbls:
		if p_table[0]==l_table[0] and p_table[1]==l_table[1]:
		    break
	    else:
		logger.info("Created new table: {0} in schema {1}".format(p_table[1],self.db_fields['sch_name']))
		new_table=TableName()
		new_table.set_fields(sn_id=self.id,tbl_name=p_table[1],obj_oid=p_table[0],has_parent=p_table[2])
		new_table.create()
		new_table.truncate()



    def discover_functions(self,prod_cursor):
	self.cursor.execute("SELECT pro_oid,func_name,id FROM function_name WHERE {0}={1} AND alive".format(self.sub_fk,self.id))
	local_funcs=self.cursor.fetchall()
#	print local_funcs
	try:
	    prod_cursor.execute("""SELECT p.oid AS pro_oid,p.proname AS funcname,p.proretset,t.typname,l.lanname
FROM pg_proc p
LEFT JOIN pg_namespace n ON n.oid = p.pronamespace
JOIN pg_type t ON p.prorettype=t.oid
JOIN pg_language l ON p.prolang=l.oid
WHERE (p.prolang <> (12)::oid)
AND n.oid={0}""".format(self.db_fields['obj_oid']))
	except Exception as e:
	    logger.error("Cannot execute function discovery query: {0}".format(e))
#	    prod_cursor.close()
	    return
	prod_funcs=prod_cursor.fetchall()
	for l_func in local_funcs:
	    for p_func in prod_funcs:
		if l_func[0]==p_func[0] and l_func[1]==p_func[1]:
		    break
	    else:
		logger.info("Retired function {0} in schema {1}".format(l_func[1],self.db_fields['sch_name']))
		old_func=FunctionName(l_func[2])
		old_func.retire()
	for p_func in  prod_funcs:
	    for l_func in local_funcs:
		if p_func[0]==l_func[0] and p_func[1]==l_func[1]:
		    break
	    else:
		logger.info("Created new function: {0} in schema {1}".format(p_func[1],self.db_fields['sch_name']))
		new_func=FunctionName()
		new_func.set_fields(sn_id=self.id,pro_oid=p_func[0],func_name=p_func[1],proretset=p_func[2],prorettype=p_func[3],prolang=p_func[4])
		new_func.create()
		new_func.truncate()



    def get_tables(self):
	self.sub_table='table_name'
	return self.get_dependants()

    def get_functions(self):
	self.sub_table='function_name'
	return self.get_dependants()
