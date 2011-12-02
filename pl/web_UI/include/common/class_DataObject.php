<?

class DataObject {
    protected $struct;

    public function __construct($struct_name) {
	$this->struct = new $struct_name;
    }

    public function get_struct() {
	return $this->struct;
    }

    public function populate($array_hash) {
	foreach (array_keys($array_hash) as $field) {
	    $this->struct->$field=$array_hash[$field];
	}
    }

    public function get(&$sql,$table,$id,$pk='id') {
	$sql->select_c("SELECT * FROM ".$table." WHERE ".$pk."=".$id);
	$this->populate($sql->get_row_hash());
	return $this->struct;
    }
}

?>
