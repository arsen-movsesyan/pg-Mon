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
	    $sql=SQL::factory();
	    $sql->select_c("SELECT id FROM ".$this->depend_obj." WHERE ".$this->reference_field."=".$this->get_id());
	    for ($i=0;$i < $sql->get_num_rows();$i++) {
		$this->dependant_ids[$i]=$sql->get_result()[$i]['id'];
	    }
	}
	return $this->dependant_ids;
    }

    public function get_stat() {
	$ret='';
	$query=sprintf($this->stat_query,$_SESSION['from_hour_back'],$_SESSION['to_hour_back']);
	$sql=SQL::factory();
	$sql->select_c($query);
	$stat=$sql->get_result();
	if (count($stat) == 0) {
	    $ret="No statistic available";
	} else {
	    $keys=array();
	    $values=array();
	    foreach ($stat[0] as $p=>$v) {
		if ($p == 'host_id' or $p == 'db_id')
		    continue;
		$keys[]=$p;
		$values[]=$v;
	    }
	    $ret="<table border=0><tr>";
	    for ($i=0;$i<count($keys);$i++) {
		$ret.="<td>".$keys[$i]."</td>";
	    }
	    $ret.="</tr><tr>";
	    for ($i=0;$i<count($values);$i++) {
		$ret.="<td><b>".$values[$i]."</b></td>";
	    }
	    $ret.="</tr></table>";
	}
	return $ret;
    }
}

?>
