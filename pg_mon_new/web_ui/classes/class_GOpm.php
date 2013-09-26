<?
require_once("include/class_GenericObject.php");
#require_once("include/class_GenericObjectCollection.php");

class GOpm extends GenericObject {
    protected $depend_obj;
    protected $reference_field;
    protected $dependant_ids=array();
    protected $stat_query;


    public function initialize($table_name, $tuple_id=false) {
	$this->table_name=$table_name;
	if ($tuple_id) {
	     $this->id=$tuple_id;
	}
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

    public function get_stat($start=1,$end=0) {
	$query=sprintf($this->stat_query,$start,$end);
	$sql=new SQL();
	$sql->select_c($query);
	$stat=$sql->get_result();
	return $stat;
    }
}

?>
