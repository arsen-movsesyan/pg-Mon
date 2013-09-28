<?
require_once("class_GOpm.php");

class HostCluster extends GOpm {
    

    public function HostCluster($in_id=false) {
	parent::initialize('host_cluster',$in_id);
	$this->depend_obj='database_name';
	$this->reference_field='hc_id';
	if ($in_id) {
	    $this->stat_query="SELECT * FROM pm_bgwriter_stat_diff(%s,%s) WHERE host_id='".$this->get_id()."'";
	}
    }


}

?>
