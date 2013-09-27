<?
require_once("class_GOpm.php");

class HostCluster extends GOpm {

    public function HostCluster($in_id=false) {
	parent::initialize('host_cluster',$in_id);
	$this->depend_obj='database_name';
	$this->reference_field='hc_id';
    }


    public function get_stat($start=1,$end=0) {
	$ret='';
	$this->stat_query="SELECT * FROM pm_bgwriter_stat_diff(%s,%s) WHERE host_id='".$this->get_id()."'";
	$stat=parent::get_stat($start,$end);
	if (count($stat) == 0) {
	    $ret="No statistic available";
	} else {
	    $keys=array();
	    $values=array();
	    foreach ($stat[0] as $p=>$v) {
		if ($p == 'host_id')
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
