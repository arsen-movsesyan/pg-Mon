<?
require_once("include/class_GenericObject.php");

class HostCluster extends GenericObject {

    public function HostCluster($in_id=false) {
	parent::initialize('host_cluster',$in_id);
    }

    public function add($in_ip_address,$in_hostName) {
	$this->set_field('hostname',$in_hostName);
	$this->set_field('param_ip_address',$in_ip_address);
	if (func_num_args() > 2) {
	
	}
    }
}

?>
