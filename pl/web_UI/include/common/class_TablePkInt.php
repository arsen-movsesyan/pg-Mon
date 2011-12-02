<?
require_once("common/class_GenericTable.php");
/********************************************************************************************************/
/* This class represents one row from any table which hase non composit not autoincremented PRIMARY KEY */
/********************************************************************************************************/

class TablePkInt extends GenericTable {
    protected $existing;

    public function __construct($in_table_name,$in_pk_field,$in_id=false) {
	parent::__construct($in_table_name,$in_pk_field,$in_id);
	$this->existing=false;
	if ($in_id) {
	    $this->existing=true;
	}
    }

    public function set_field($field,$value) {
	parent::set_field($field,$value);
	if ($field==$this->pk) {
	    $this->id=$value;
	    $this->existing=false;
	}
    }

    public function is_existing() {
	return $this->existing;
    }

    public function save() {
	if (!$this->existing) {
	    $query=$this->_case_insert();
	} else {
	    $query=$this->_case_update();
	}
	if (parent::save()) {
	    $this->sql->select_c($query);
	}
    }
}

?>
