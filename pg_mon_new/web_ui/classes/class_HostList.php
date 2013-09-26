<?
include_once("include/class_SQL.php");
include_once("class_HostCluster.php");
include_once("class_DatabaseName.php");
include_once("class_SchemaName.php");

class HostList {
#    private $host_string='';
    private $sql;
#    private $host_list=array();
    private $selected_hc_id;
    private $selected_dn_id;
    private $selected_sn_id;
#    private $nested_array=array();
#    private $selected_tn_id;
#    private $selected_in_id;


    private $db_list;


    public function __construct() {
	$this->sql=SQL::factory();
	$this->_host_list();
    }

    private function _define_level() {
	$this->selected_hc_id=(isset($_GET['hc_id']) ? $_GET['hc_id'] : NULL);
	$this->selected_dn_id=(isset($_GET['dn_id']) ? $_GET['dn_id'] : NULL);
	$this->selected_sn_id=(isset($_GET['sn_id']) ? $_GET['sn_id'] : NULL);
#	$this->selected_tn_id=(isset($_GET['tn_id']) ? $_GET['tn_id'] : NULL);
#	$this->selected_in_id=(isset($_GET['in_id']) ? $_GET['in_id'] : NULL);
    }

    private function _host_list() {
	$this->sql->select_c("SELECT id FROM host_cluster");
	$hosts=$this->sql->get_result();
	foreach ($hosts as $id) {
	    $hc= new HostCluster($id['id']);
	    $this->host_list[]=$hc;
	}
    }

    private function _get_sch_list() {
	$string="<ul>";
	$dn=new DatabaseName($this->selected_dn_id);
	foreach ($dn->get_dependant_ids() as $sn_id) {
	    $sn=new SchemaName($sn_id);
	    $string.="<li><a href=".$_SERVER['PHP_SELF']."?action=stat&hc_id=".$this->selected_hc_id."&dn_id=".$this->selected_dn_id."&sn_id=".$sn->get_id().">";
	    if ($this->selected_sn_id == $sn->get_id()) {
		$string.="<b>".$sn->get_field('sch_name')."</b>";
	    } else {
		$string.=$sn->get_field('sch_name');
	    }
	    $string.="</a></li>";
	}
	$string.="</ul>";
	return $string;
    }

    private function _get_db_list() {
	$string="<ul>";
	$hc=new HostCluster($this->selected_hc_id);
	foreach ($hc->get_dependant_ids() as $db_id) {
	    $dn=new DatabaseName($db_id);
	    $string.="<li><a href=".$_SERVER['PHP_SELF']."?action=stat&hc_id=".$this->selected_hc_id."&dn_id=".$dn->get_id().">";
	    if ($this->selected_dn_id == $dn->get_id()) {
		$string.="<b>".$dn->get_field('db_name')."</b>";
		$string.=$this->_get_sch_list();
	    } else {
		$string.=$dn->get_field('db_name');
	    }
	    $string.="</a></li>";
	}
	$string.="</ul>";
	return $string;
    }


    public function get_string() {
	$this->_define_level();
	if (count($this->host_list) == 0)
	    $string="No hosts registered";
	else {
	    $string="<ul>";
	    foreach ($this->host_list as $hc) {
		$string.="<li><a href=".$_SERVER['PHP_SELF']."?action=stat&hc_id=".$hc->get_id().">";
		if ($this->selected_hc_id == $hc->get_id()) {
		    $string.="<b>".$hc->get_field('hostname')."</b>";
		    $string.=$this->_get_db_list();
		} else {
		    $string.=$hc->get_field('hostname');
		}
		$string.="</a></li>";
	    }
	    $string.="</ul>";
	}
	return $string;
    }

    public function set_host_id($id) {
	$this->selected_hc_id=$id;
    }

    public function get_nested_array() {
	$array=array();
	if ($this->selected_hc_id)
	    $array['hc_id']=$this->selected_hc_id;
	if ($this->selected_dn_id)
	    $array['dn_id']=$this->selected_dn_id;
	if ($this->selected_sn_id)
	    $array['sn_id']=$this->selected_sn_id;
	return $array;
    }


}

?>
