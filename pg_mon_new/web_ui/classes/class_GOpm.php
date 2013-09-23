<?
require_once("include/class_GenericObject.php");

class GOpm extends GenericObject {
    protected $depend_obj;
    protected $reference_field;
    protected $dependant_ids=array();

    public function __construct() {
	parent::__construct();
    }

    public function get_dependant_ids() {
	if (count($this->dependant_ids) == 0) {
	    $sql=new SQL();
	    $sql->select_c("SELECT id FROM ".$this->depend_obj." WHERE ".$this->reference_field."=".$this->get_id());
	    for ($i=0;$i < $sql->get_num_rows();$i++) {
		$this->dependant_ids[$i]=$sql->get_result()[$i]['id'];
	    }
	}
	return $this->dependant_ids;
    }

}

?>
