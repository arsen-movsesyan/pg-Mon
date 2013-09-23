<?
require_once("include/class_GenericObject.php");
require_once("include/class_GenericObjectCollection.php");

class GOpm extends GenericObject {
    protected $depend_obj;
    protected $reference_field;
    protected $dependant_ids=array();
    protected $stat_obj;


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

    public function get_stat($stat_name,$start=1,$end=0) {
	$self_table=preg_split('_',$this->get_table());
	if (get_class($this) == 'HostCluster') {
	    $self_table[0]='bgwriter';
	}
	$stat_object=ucwords($self_table[0])."Stat'";
	$this->stat_obj=new GenericObjectCollection();
	eval($stat_name."(".$this->get_id().",".$start.",".$end.")");
	return $this->stat_obj;
    }
}

?>
