import table
import settings
from tablename import TableName
from functionname import FunctionName

logger=settings.logger

class SchemaName(table.genericName):


    def __init__(self,in_db_conn,in_prod_conn,in_id=None):
	super(SchemaName,self).__init__(in_db_conn,in_id)
	self.table='schema_name'
	self.sub_fk='sn_id'
	self.prod_conn=in_prod_conn
	if in_id:
	    self._populate()


    def discover_tables(self):
	cur=self._get_p_cursor()
	if not cur:
	    logger.error("Returning from SN.discover_tables no p_cur obtained")
	    return False
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
	    return False
	prod_tbls=cur.fetchall()
	cur.close()
	cur=self._get_cursor()
	if not cur:
	    logger.error("Returning from SN.discover_tables no cur obtained")
	    return False
	try:
	    cur.execute("SELECT obj_oid,tbl_name,id FROM table_name WHERE sn_id={0} AND alive".format(self.id))
	except Exception as e:
	    logger.error("Cannot execute tables discovery query on Local: {0}".format(e.pgerror))
	    cur.close()
	    return False
	local_tbls=cur.fetchall()
	cur.close()
	for l_table in local_tbls:
	    for p_table in prod_tbls:
		if l_table[0] == p_table[0] and l_table[1] == p_table[1]:
		    old_table=TableName(self.db_conn,self.prod_conn,l_table[2])
		    if not old_table.discover_indexes():
			logger.error("SN.discover_tables False from tn.discover_indexes for old")
		    if not old_table.discover_toast():
			logger.error("SN.discover_tables False from tn.discover_toast for old")
		    break
	    else:
		old_table=TableName(self.db_conn,self.prod_conn,l_table[2])
		if not old_table.retire():
		    logger.error("SN.discover_tables() cannot retire old")
		else:
		    logger.info("Retired table {0} in schema {1}".format(l_table[1],self.db_fields['sch_name']))
	for p_table in  prod_tbls:
	    for l_table in local_tbls:
		if p_table[0]==l_table[0] and p_table[1]==l_table[1]:
		    break
	    else:
		logger.info("Created new table: {0} in schema {1}".format(p_table[1],self.db_fields['sch_name']))
		new_table=TableName(self.db_conn,self.prod_conn)
		new_table.set_fields(sn_id=self.id,tbl_name=p_table[1],obj_oid=p_table[0],has_parent=p_table[2])
		if not new_table._create():
		    logger.error("SN.discover_tables() cannot create new")
		else:
		    logger.info("Create new table {0}".format(p_table[1]))
		    if not new_table.discover_indexes():
			logger.error("SN.discover_tables False from tn.discover_indexes for new")
		    if not new_table.discover_toast():
			logger.error("SN.discover_tables False from tn.discover_toast for new")
	return True



    def discover_functions(self):
	p_cur=self._get_p_cursor()
	if not p_cur:
	    logger.error("Returning from SN.discover_functions no p_cur obtained")
	    return False
	try:
	    p_cur.execute("""SELECT p.oid AS pro_oid,p.proname AS funcname,p.proretset,t.typname,l.lanname
FROM pg_proc p
LEFT JOIN pg_namespace n ON n.oid = p.pronamespace
JOIN pg_type t ON p.prorettype=t.oid
JOIN pg_language l ON p.prolang=l.oid
WHERE (p.prolang <> (12)::oid)
AND n.oid={0}""".format(self.db_fields['obj_oid']))
	except Exception as e:
	    logger.error("Cannot execute functions discovery query on Prod: {0}".format(e.pgerror))
	    p_cur.close()
	    return False
	prod_funcs=p_cur.fetchall()
	p_cur.close()
	cur=self._get_cursor()
	if not cur:
	    logger.error("Returning from SN.discover_functions no cur obtained")
	    return False
	try:
	    cur.execute("SELECT pro_oid,func_name,id FROM function_name WHERE sn_id={0} AND alive".format(self.id))
	except Exception as e:
	    logger.error("Cannot execute functions discovery query on Local: {0}".format(e.pgerror))
	    cur.close()
	    return False
	local_funcs=cur.fetchall()
	cur.close()
	for l_func in local_funcs:
	    for p_func in prod_funcs:
		if l_func[0]==p_func[0] and l_func[1]==p_func[1]:
		    break
	    else:
		old_func=FunctionName(self.db_conn,self.prod_conn,l_func[2])
		if not old_func.retire():
		    logger.error("SN.discover_functions() Cannot retire old")
		else:
		    logger.info("Retired function {0} in schema {1}".format(l_func[1],self.db_fields['sch_name']))
	for p_func in  prod_funcs:
	    for l_func in local_funcs:
		if p_func[0]==l_func[0] and p_func[1]==l_func[1]:
		    break
	    else:
		new_func=FunctionName(self.db_conn,self.prod_conn)
		new_func.set_fields(sn_id=self.id,pro_oid=p_func[0],func_name=p_func[1],proretset=p_func[2],prorettype=p_func[3],prolang=p_func[4])
		if not new_func._create():
		    logger.error("SN.discover_functions() Cannot create new")
		else:
		    logger.info("Created new function: {0} in schema {1}".format(p_func[1],self.db_fields['sch_name']))
	return True



    def get_tables(self):
	self.sub_table='table_name'
	return self.get_dependants(False)

    def get_functions(self):
	self.sub_table='function_name'
	return self.get_dependants(False)



    def stat(self,in_time_id):
	tbls=self.get_tables()
	if not tbls:
	    pass
	else:
	    for tbl in tbls:
		tn=TableName(self.db_conn,self.prod_conn,tbl)
		if not tn.stat(in_time_id):
		    logger.warning("SN.stat False from  tn.stat()")
		if not tn.va_stat(in_time_id):
		    logger.warning("SN.stat False from  tn.va_stat()")
	funcs=self.get_functions()
	if not funcs:
	    pass
	else:
	    for fnc in funcs:
		fn=FunctionName(self.db_conn,self.prod_conn,fnc)
		if not fn.stat(in_time_id):
		    logger.warning("SN.stat False from  fn.stat()")
	return True
