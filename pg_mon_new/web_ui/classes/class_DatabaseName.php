<?
require_once("include/class_GenericObject.php");

class DatabaseName extends GenericObject {

    public function DatabaseName($in_id=false) {
	parent::initialize('database_name',$in_id);
    }

}

?>
