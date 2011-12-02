<?

require_once("database/class_DbConn.php");
require_once("common/class_DataObject.php");

class DataObjectCollection {
    protected $table;
    protected $struct_name;

    protected $items;
    protected $sql;

    public function __construct($table,$struct_name,$db_conf_file) {
	$this->table_name=$table;
	$this->items=array();
	$this->struct_name=$struct_name;
	$this->sql=new DbConn($db_conf_file,false);
    }

/*
    public function get_by_pk($id,$pk='id') {
	$new_do=new DataObject($this->struct_name);
	$this->sql->select_c("SELECT * FROM ".$this->table_name." WHERE ".$this->sql->escape($pk)."='".$this->sql->escape($id)."'");
	$new_do->populate($this->sql->get_row_hash());
	return $new_do->get_struct();
    }
*/
    public function get_by_fv($vf=array()) {
	$stmt="SELECT * FROM ".$this->table_name;
	if (!empty($fv)) {
	    $stmt.=" WHERE ";
	    foreach ($fv as $field=>$value) {
		$stmt.=$field."='".$this->sql->escape($value)."' AND ";
	    }
	    $stmt=substr($stmt,0,-5);
	}
	$this->sql->select_c($stmt);
	if ($this->sql->get_num_rows() != 0) {
	    for ($i=0;$i<$this->sql->get_num_rows();$i++) {
		$new_do= new DataObject($this->struct_name);
		$new_do->populate($this->sql->get_row_hash($i));
		$this->items[]=$new_do->get_struct();
	    }
	}
	return count($this->items);
    }

    public function get_array() {
	return $this->items;
    }
}

?>
