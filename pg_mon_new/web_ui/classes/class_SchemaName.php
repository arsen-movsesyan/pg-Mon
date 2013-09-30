<?
require_once("class_GOpm.php");

class SchemaName extends GOpm {

    public function SchemaName($in_id=false) {
	parent::initialize('schema_name',$in_id);
	$this->depend_obj='table_name';
	$this->reference_field='sn_id';
    }

    public function get_info() {
	return false;
    }
}

?>
