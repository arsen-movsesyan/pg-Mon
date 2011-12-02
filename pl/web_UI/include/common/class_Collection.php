<?
require_once("database/class_DbConn.php");

class Collection {
    private $table_name;
    private $class_name;
    private $pk;
    private $item_count;
    private $ids;
    private $obj_array;
    private $modified;


    public function __construct($table_name,$class_name,$pk) {
	$this->table_name=$table_name;
	$this->class_name=$class_name;
	$this->pk=$pk;
	$this->ids=array();
	$this->modified=true;
	$this->item_count=0;
    }

/*** Configuration part ***/
    public function add_id($new_id) {
	array_push($this->ids,$new_id);
	$this->item_count++;
	$this->modified=true;
    }

    public function remove_id($old_id) {
	foreach ($this->ids as $ind=>$exist_id) {
	    if ($exist_id==$old_id) {
		unset($this->ids[$ind]);
	    }
	}
	$this->item_count--;
	$this->modified=true;
    }

    public function flush_array() {
	$this->ids=array();
	$this->item_count=0;
    }


/*** Metadata Interface ***/
    public function get_table_name() {
	return $this->table_name;
    }

    public function get_item_count() {
	return $this->item_count;
    }

    public function get_pk() {
	return $this->pk;
    }


/*** Data Interface ***/
    public function get_id_array() {
	return $this->ids;
    }


    public function get_object_array() {
	if ($this->modified) {
	    $this->_populate_object_array();
	}
	return $this->_retreive_objects();
    }

/************* Private part **********************/

    private function _id_list($start_lim=0, $end_lim=-1) {
	$list = "";
	if ($end_lim == -1) {
	    $end_lim=sizeof($this->ids) - 1;
	}

	for ($i=$start_lim; $i<=$end_lim; $i++) {
	    if (is_numeric($this->ids[$i])) {
                $list .= $this->ids[$i].",";
	    }
	}
	$list = substr($list, 0, strlen($list)-1);
	return $list;
    }

    private function _get_index_from_tuple_id($tuple_id) {
	for ($i=0; $i <= sizeof($this->ids)-1; $i++) {
	    if ($this->ids[$i] == $tuple_id) {
		return $i;
	    }
	}
    }

    private function _populate_object_array() {
	if ($this->item_count > 0) {
	    $stmt = "SELECT * FROM ".$this->table_name." WHERE ".$this->pk." IN (";
	    $stmt .= $this->_id_list().")";

/****************************************************************************************************/ 
/* Todo: place DB Connection into Application layer so every App should  use it's own DB connection */
/****************************************************************************************************/ 
	    $sql = new DbConn;
/****************************************************************************************************/ 
/****************************************************************************************************/ 
	    $sql->select_c($stmt);
	    $result_rows = $sql->get_result();

	    for ($i=0; $i < sizeof($result_rows); $i++) {
		$this_row = $result_rows[$i];
		$this_db_row_id = $this_row['id'];
		$this_index=$this->_get_index_from_tuple_id($this_db_row_id);
		if ($this_index >= 0) {
		    $r_obj_array_index_obj = &$this->obj_array[$this_index];
		    $s="\$r_obj_array_index_obj = new ".$this->class_name."(".$this_db_row_id.");";
		    eval($s);
		    foreach ($this_row as $key=>$value) {
			if ($key != $this->pk) {
			    $r_obj_array_index_obj->set_field($key,$value);
			}
		    }
		    $r_obj_array_index_obj->force_loaded();
		}
	    }
	}
	$this->modified=false;
    }

    private function _retreive_objects() {
	$ret=array();
	for ($i=0; $i < $this->item_count; $i++) {
	    $ret[] = $this->obj_array[$i];
	}
	return $ret;
    }
}
?>
