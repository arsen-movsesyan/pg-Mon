<?
require_once("common/class_GenericTable.php");
/********************************************************************************************************/
/* This class represents one row from any table which hase non composit not autoincremented PRIMARY KEY */
/********************************************************************************************************/

class TableAutoIncrement extends GenericTable {

    public function save() {
	if (parent::save()) {
	    if (!$this->id) {
		$query=$this->_case_insert();
		$this->sql->select_c($query);
		$new_id=$this->sql->get_row_hash();
		$this->id=$new_id[$this->pk];
	    } else {
		$query=$this->_case_update();
		$this->sql->non_select_c($query);
	    }
	}
    }
}

?>
