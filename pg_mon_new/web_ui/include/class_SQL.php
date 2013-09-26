<?
require_once("include/class_Pgconnect.php");

class SQL extends Pgconnect {
    private $affected_rows;
    private $rows_array=array();
    private $result_array=array();
    private static $instance=NULL;

    public static function factory() {
	if (self::$instance == NULL) {
	    self::$instance = new SQL();
	}
	return self::$instance;
    }

    protected function __construct() {
	parent::__construct();
	$this->_flush();
    }

    
    private function _flush() {
	$this->rows_array=array();
	$this->result_array=array();
	$this->last_query="";
    }
    
    public function select_c($query) {
	$this->_flush();
//	$this->last_query=$query;
	$res=@pg_query($this->db_conn,$query);
	if (!is_resource($res)) {
	    return false;
	}
	$this->affected_rows=pg_num_rows($res);
	while ($row=pg_fetch_assoc($res)) {
	    array_push($this->result_array,$row);
	}
//	for ($i=0;$i<pg_num_fields($res);$i++) {
//	    $this->rows_array[$i]=pg_field_name($res,$i);
//	}
	return true;
    }


    public function get_result() {
        return $this->result_array;
    }

    public function get_num_rows() {
	return $this->affected_rows;
    }

    public function insert_c($table,$array_fields_values,$returning=false) {
	$fields=array_keys($array_fields_values);
	$values=array_values($array_fields_values);
	$esc_values=array();
	foreach ($values as $val) {
	    if (!is_numeric($val)) {
		$val="'".pg_escape_string($val)."'";
	    }
	    $esc_values[]=$val;
	}
	
	$query="INSERT INTO $table (";
	$query.=join(', ',$fields);
	$query.=") VALUES (";
	$query.=join(', ',$esc_values);
	$query.=")";
	if ($returning) {
	    $query.=" RETURNING $returning";
	}
	
	$this->_flush();
	$this->last_query=$query;
	$res=pg_query($query);

	if (!is_resource($res)) {
	    return false;
	}
	$this->affected_rows=pg_affected_rows($res);
	if ($returning) {
	    while ($row=pg_fetch_assoc($res)) {
		$this->result_array[]=$row;
	    }
	    $this->rows_array=array_keys($this->result_array);
	}
	return true;
    }
    
    public function update_c($table,$array_fields,$array_conditions) {
	$array_updates=array();
	foreach ($array_fields as $field=>$val) {
	    if (!is_numeric($val)) {
		$val="'".pg_escape_string($val)."'";
	    }
	    $array_updates[]="$field=$val";
	}
	$array_where=array();
	foreach ($array_conditions as $field=>$val) {
	    if (!is_numeric($val)) {
		$val="'".pg_escape_string($val)."'";
	    }
	    $array_where[]="$field=$val";
	}
	$query="UPDATE $table SET ";
	$query.=join(', ',$array_updates);
	$query.=" WHERE ".join(' AND ',$array_where);
	
	$this->_flush();
	$this->last_query=$query;
	$res=pg_query($query);
	if (!is_resource($res)) {
	    return false;
	}
	$this->affected_rows=pg_affected_rows($res);
	return true;
    }
    
    public function delete_c($table,$array_conditions) {
	$array_where=array();
	foreach ($array_conditions as $field=>$val) {
	    if (!is_numeric($val)) {
		$val="'".pg_escape_string($val)."'";
	    }
	    $array_where[]="$field=$val";
	}
	$query="DELETE FROM $table WHERE ".join(' AND ',$array_where);

	$this->_flush();
	$this->last_query=$query;
	$res=pg_query($query);
	if (!is_resource($res)) {
	    return false;
	}
	$this->affected_rows=pg_affected_rows($res);
	return true;
    }
}
?>