<?
require_once("common/interface_Table.php");
require_once("database/class_DbConn.php");
/********************************************************************************************************/
/* This class represents one row from any table which hase non composit not autoincremented PRIMARY KEY */
/********************************************************************************************************/

class GenericTable implements Table {
    protected $table_name;
    protected $id;
    protected $pk;
    protected $database_fields;
    protected $modified_fields;
    protected $loaded;
    protected $sql;

    public function __construct($in_table_name,$in_pk_field,$in_id=false) {
	$this->pk=$in_pk_field;
	$this->table_name=$in_table_name;
	$this->database_fields=array();
	$this->modified_fields=array();
	$this->loaded=false;
	$this->id=$in_id;
    }

/************** Config **************/
    public function set_db_conf($conf_file,$conn_type=false) {
	$this->sql=new DbConn($conf_file,$conn_type);
    }



/************ Interface ************/
    public function save() {
	foreach ($this->modified_fields as $field=>$value) {
	    if ($value) {
		return true;
	    }
	}
	return false;
    }

/************ Interface ************/
    public function get_table_name() {
	return $this->table_name;
    }

/************ Interface ************/
    public function get_table_structure() {
	return array_keys($this->database_fields);
    }

/************ Interface ************/
    public function get_field($field) {
	if (!$this->loaded) {
	    $this->_reload();
	}
	if (array_key_exists($field,$this->database_fields)) {
	    return $this->database_fields[$field];
	}
	return false;
    }

/************ Interface ************/
    public function get_all_fields() {
	if (!$this->loaded) {
	    $this->_reload();
	}
	return $this->database_fields;
    }

/************ Interface ************/
    public function get_id() {
	return $this->id;
    }

/************ Interface ************/
    public function destroy() {
	if ($this->id) {
	    $this->sql->non_select_c("DELETE FROM ".$this->table_name." WHERE ".$this->pk."=".$this->id);
	}
    }

/************ Interface ************/
    public function set_field($field, $value) {
	$this->database_fields[$field]=$value;
	$this->modified_fields[$field]=true;
	$this->loaded=false;
    }


    public function force_loaded() {
	$this->loaded=true;
    }

    public function load() {
	$this->_reload();
    }

    public function __destruct() {}

/***********************************************************************************/
/***********************************************************************************/

    protected function _reload() {
	if ($this->id) {
	    $this->sql->select_c("SELECT * FROM ".$this->table_name." WHERE ".$this->pk."=".$this->id);
	}
	if ($this->sql->get_num_rows() == 0) {
	    return false;
	}

#	$result_fields=$this->sql->get_row_hash();
	$this->database_fields=$this->sql->get_row_hash();
	foreach ($this->database_fields as $key=>$value) {
	    $this->modified_fields[$key]=false;
	}
	$this->loaded=true;
	return true;
    }

    protected function _case_insert() {
	$stmt="INSERT INTO ".$this->table_name." (";
	foreach ($this->database_fields as $key => $value) {
	    if ($value != "") {
		$stmt.="$key,";
	    }
	}
	$stmt=substr($stmt,0,strlen($stmt)-1);
	$stmt.=") VALUES (";
	foreach ($this->database_fields as $key => $value) {
	    if ($value != "") {
		if (!is_numeric($value)) {
		    $value="'".$this->sql->escape($value)."'";
		}
		$stmt .= $value.",";
	    }
	}
	$stmt=substr($stmt,0,strlen($stmt)-1).")";
	$stmt.=" RETURNING ". $this->pk;
	return $stmt;
    }

    protected function _case_update() {
	$stmt="UPDATE ".$this->table_name." SET ";
	foreach ($this->database_fields as $key => $value) {
	    if ($this->modified_fields[$key]) {
		if (!is_numeric($value)) {
		    $value="'".$this->sql->escape($value)."'";
		}
		if ($value == "") {
		    $stmt.="$key = NULL, ";
		} else {
		    $stmt.="$key = $value, ";
		}
	    }
	}
	$stmt=substr($stmt,0,strlen($stmt)-2);
	$stmt.=" WHERE ".$this->pk."=".$this->id;
	return $stmt;
    }
}

?>
