<?
#include_once("include/class_SQL.php");
include_once("include/class_GenericInfo.php");
include_once("class_HostCluster.php");
include_once("class_DatabaseName.php");
include_once("class_SchemaName.php");

class HostList extends GenericInfo {
    private $host_list;

    public function __construct() {
	parent::__construct();
	$this->_host_list();

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
	$dn=new DatabaseName($this->level['dn_id']);
	foreach ($dn->get_dependant_ids() as $sn_id) {
	    $sn=new SchemaName($sn_id);
	    $string.="<li><a href=".$_SERVER['PHP_SELF']."?action=stat&info=si&hc_id=".$this->level['hc_id']."&dn_id=".$this->level['dn_id']."&sn_id=".$sn->get_id().">";
	    if (isset($this->level['sn_id']) and $this->level['sn_id'] == $sn->get_id()) {
		$string.="<b>".$sn->get_field('sch_name')."</b>";
	    } else
		$string.=$sn->get_field('sch_name');
	    $string.="</a></li>";
	}
	$string.="</ul>";
	return $string;
    }

    private function _get_db_list() {
	$string="<ul>";
	$hc=new HostCluster($this->level['hc_id']);
	foreach ($hc->get_dependant_ids() as $db_id) {
	    $dn=new DatabaseName($db_id);
	    $string.="<li><a href=".$_SERVER['PHP_SELF']."?action=stat&info=di&hc_id=".$this->level['hc_id']."&dn_id=".$dn->get_id().">";
	    if (isset($this->level['dn_id']) and $this->level['dn_id'] == $dn->get_id()) {
		$string.="<b>".$dn->get_field('db_name')."</b>";
		$string.=$this->_get_sch_list();
	    } else
		$string.=$dn->get_field('db_name');
	    $string.="</a></li>";
	}
	$string.="</ul>";
	return $string;
    }


    public function get_string() {
	if ($this->level == NULL)
	    $this->_define_level();
	if (count($this->host_list) == 0)
	    $this->string="No hosts registered";
	else {
	    $this->string="<ul>";
	    foreach ($this->host_list as $hc) {
		$this->string.="<li><a href=".$_SERVER['PHP_SELF']."?action=stat&info=ci&hc_id=".$hc->get_id().">";
		if (isset($this->level['hc_id']) and $this->level['hc_id'] == $hc->get_id()) {
		    $this->string.="<b>".$hc->get_field('hostname')."</b>";
		    $this->string.=$this->_get_db_list();
		} else
		    $this->string.=$hc->get_field('hostname');
		$this->string.="</a></li>\n";
	    }
	    $this->string.="</ul>";
	}
	return parent::get_string();
    }


}

?>
