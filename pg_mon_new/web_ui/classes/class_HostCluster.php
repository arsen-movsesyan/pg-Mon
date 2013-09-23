<?
require_once("class_GOpm.php");

class HostCluster extends GOpm {

    public function HostCluster($in_id=false) {
	$this->depend_obj='database_name';
	$this->reference_field='hc_id';
	parent::initialize('host_cluster',$in_id);
    }

    public function add($in_ip_address,$in_hostName,$in_params=array()) {
	$this->set_field('hostname',$in_hostName);
	$this->set_field('param_ip_address',$in_ip_address);
	if (count($in_params) >1 ) {
	    foreach (array_keys($in_params) as $param) {
		$this->set_field($param,$in_params[$param]);
	    }
	}
	echo "Fields are: ".$this->database_fields."<br>";
    }
}

?>
