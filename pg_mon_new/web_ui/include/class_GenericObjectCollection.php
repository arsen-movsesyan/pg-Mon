<?
require_once("include/class_SQL.php");
class GenericObjectCollection {
    private $table_name;
    private $class_name;

    private $page_size;
    private $item_count=0;

    private $ids;
    private $obj_array=false;

    public function __construct($table_name,$class_name) {
	$this->table_name=$table_name;
	$this->class_name=$class_name;
	$this->ids=array();
    }

    public function add_id($id) {
	array_push($this->ids,$id);
	$this->item_count++;
    }

    public function set_page_size($page_size) {
	$this->page_size=$page_size;
    }

    public function get_item_count() {
	return $this->item_count;
    }

    private function _id_list($start_lim=0, $end_lim=-1) {
	$list = "";
	if ($end_lim == -1) {
	    $end_lim=sizeof($this->ids)-1;
	}

	for ($i=$start_lim; $i<=$end_lim; $i++) {
	    if (is_numeric($this->ids[$i])) {
		$list.=$this->ids[$i].",";
	    }
	}
	$list=substr($list, 0, strlen($list)-1);
	return $list;
    }

    private function _get_index_from_tuple_id($tuple_id) {
	for ($i=0; $i<=sizeof($this->ids)-1; $i++) {
	    if ($this->ids[$i] == $tuple_id) {
		return $i;
	    }
	}
    }

    public function _populate_object_array($page_num) {
	if ($this->item_count > 0) {
	    if ($page_num > 0) {
		$start_lim=($this->page_size * ($page_num - 1));
		$end_lim = ($start_lim + $items_per_page) - 1;
		if ($end_lim > ($this->item_count-1)) {
		    $end_lim = $this->item_count - 1;
		}
		$stmt = "SELECT * FROM ".$this->table_name." WHERE id IN (".$this->_id_list($start_lim, $end_lim).")";
	    } else {
		$stmt = "SELECT * FROM ".$this->table_name." WHERE id IN (".$this->_id_list().")";
	    }
#            echo $stmt."<br>";
	    $sql=SQL::factory();
	    $sql->select_c($stmt);
	    $result_rows=$sql->get_result();

	    for ($i=0;$i<sizeof($result_rows);$i++) {
		$this_row=$result_rows[$i];
		$this_db_row_id=$this_row['id'];
		$this_index=$this->_get_index_from_tuple_id($this_db_row_id);
		if ($this_index >= 0) {
		    $r_obj_array_index_obj = &$this->obj_array[$this_index];
		    $s="\$r_obj_array_index_obj = new ".$this->class_name."(".$this_db_row_id.");";
		    eval($s);
		    $r_obj_array_index_obj->force_loaded();
		    foreach ($this_row as $key=>$value) {
			if (!is_numeric($key)) {
			    $r_obj_array_index_obj->set_field($key,$value);
			}
		    }
		}
	    }
	}
    }

    public function retreave_objects($page_num=0) {
	if (!$this->object_array) {
	    $this->_populate_object_array($page_num);
	}
	if ($page_num > 0) {
	    $start_lim=$this->page_size * ($page_num-1);
	    $end_lim=$start_lim+$this->page_size-1;
	    if ($end_lim > ($this->item_count-1)) {
		$end_lim=$this->item_count-1;
	    }
	} else {
	    $start_lim=0;
	    $end_lim=$this->item_count-1;
	}
	$ret=array();
	$counter=0;
	for ($i=$start_lim;$i<=$end_lim;$i++) {
	    $ret[$counter]=$this->obj_array[$i];
	    $counter++;
	}
	return $ret;
    }
}
?>
