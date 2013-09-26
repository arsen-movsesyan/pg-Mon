<?
require_once("include/class_SQL.php");

class GenericObject {
    private $database_fields;
    private $loaded=0;
    private $modified_fields;
    protected $id;
    protected $table_name;

    public function get_table() {
	return $this->table_name;
    }

    public function reload() {
	$sql = new SQL();
	if (!$sql->select_c("SELECT * FROM ".$this->table_name." WHERE id=".$this->id)) {
	    echo "Cannot select from database with id=".$this->id." Error: ".$sql->last_error();
	    exit;
	}
	$all=$sql->get_result();
	$this->database_fields=$all[0];
	$this->loaded=1;
	if (sizeof($this->modified_fields) > 0) {
	    foreach ($this->modified_fields as $key => $value) {
		$this->modified_fields[$key] = false;
	    }
	}
    }

    private function load() {
	$this->reload();
	$this->loaded=1;
    }

    public function force_loaded() {
	$this->loaded=1;
    }

    public function get_field($field) {
	if ($this->loaded == 0) {
	    $this->load();
	}
	return $this->database_fields[$field];
    }

    public function get_all_fields() {
#	if ($this->loaded == 0) {
#	    $this->load();
#	}
	return $this->database_fields;
    }

    public function get_id() {
	return $this->id;
    }

#    public function initialize($table_name, $tuple_id=false) {
#	$this->table_name=$table_name;
#	if ($tuple_id) {
#	    $this->id=$tuple_id;
#	}
#    }

    public function set_field($field, $value) {
	if ($this->loaded == 0) {
	    if ($this->id) {
		$this->load();
	    }
	}
	$this->database_fields[$field]=$value;
	$this->modified=1;
	$this->modified_fields[$field]=true;
    }

    public function destroy() {
	if ($this->id) {
	    $sql = new SQL();
	    if (!$sql->delete_c($this->table_name,array('id'=>$this->id))) {
		echo "Cannot destroy row id. Error: ".$sql->last_error."<br>";
		echo "Query: ".$sql->get_last_query();
		return false;
	    }
	}
	return true;
    }

    public function Save() {
	$sql = new sql();

	if (!$this->id) {
#	    $this->loaded=0;
#	}

#	if ($this->loaded == 0) {
# assume this is a new entity
	    if (!$sql->insert_c($this->table_name,$this->database_fields,'id')) {
		echo "Cannot create new entry. Error: ".$sql->last_error()."<br>";
		echo "Query: ".$sql->get_last_query();
		return false;
	    }
	    $result=$sql->get_result();
	    $this->id=$result[0]['id'];
	} else {
# assume this is an existing entity
	    unset($this->database_fields['id']);
	    if (!$sql->update_c($this->table_name,$this->database_fields,array('id'=>$this->id))) {
		echo "Cannot update row. Error: ".$sql->last_error()."<br>";
		echo "Query: ".$sql->get_last_query();
		return false;
	    }
	}
	return true;
    }
}
