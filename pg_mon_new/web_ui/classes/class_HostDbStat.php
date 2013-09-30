<?
include_once("include/class_GenericInfo.php");
include_once("class_HostCluster.php");
include_once("class_DatabaseName.php");

class HostDbStat extends GenericInfo {
    private $host_info=NULL;
    private $host_stat;
    private $dn_info=NULL;
    private $dn_stat;

#    private $level=NULL;

#    public function __construct() {
#	$this->sql=SQL::factory();
#    }


    public function get_string() {
	$ret="<table border=1>";
	$ret.=$this->_create_host_info();
	$ret.="</table>";
	return $ret;
    }

    private function _create_db_info() {
	if (isset($this->level['dn_id'])) {
	    $dn=new DatabaseName($this->level['dn_id']);
	    $this->dn_info=$dn->get_info();
	    $this->dn_stat=$dn->get_stat();
	}
    }


    private function _create_host_info() {
	if ($this->level == NULL)
	    $this->_define_level();
	if (isset($this->level['hc_id'])) {
	    $hc=new HostCluster($this->level['hc_id']);
	    $this->host_info=$hc->get_info();
	    $this->host_stat=$hc->get_stat();
	}
    }

    public function get_host_info() {
	if ($this->host_info == NULL)
	    $this->_create_host_info();
	return $this->host_info;
    }

    public function get_db_info() {
	if ($this->dn_info == NULL)
	    $this->_create_db_info();
	return $this->dn_info;
    }

    public function get_host_stat() {
	return $this->host_stat;
    }

    public function get_db_stat() {
	return $this->dn_stat;
    }


}

?>
