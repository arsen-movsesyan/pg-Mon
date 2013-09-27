<?
include_once("include/class_SQL.php");
include_once("class_HostCluster.php");
include_once("class_DatabaseName.php");
include_once("class_SchemaName.php");

class Stat {
    private $sql;
    private $level=array();
    private $string='';
    private $host_info;
    private $host_stat;
    private $dn_info;
    private $dn_stat;

    private $status_header=NULL;

    public function __construct() {
	$this->sql=SQL::factory();
    }

    public function set_level($in_level) {
	$this->level=$in_level;
    }

    public function set_header($in_header) {
	$this->status_header=$in_header;
    }

    public function get_string() {
	$ret="<table border=0 width=100%>";
	$ret.=$this->_create_host_info();
#	$ret.="<tr><td colspan=2><hr width=70%></td></tr>";
#	$ret.=$this->_create_db_info();
#	$this->_create_table_list();
	$ret.="</table>";
	return $ret;
    }

    private function _create_db_info() {
	$template='';
	if (isset($this->level['dn_id'])) {
	    $dn=new DatabaseName($this->level['dn_id']);
	    $this->dn_info="Database: <b>".$dn->get_field('db_name')."</b>";
	    $this->dn_stat=$dn->get_stat();
	    $template.="
		<tr><td colspan=2><hr width=70%></td></tr>
		<tr valign=top>
		    <td>".$this->dn_info."</td>
		    <td>".$this->dn_stat."</td>
		</tr>";
	}
	return $template;
    }

    private function _create_table_list() {
	$tbl_list_q="SELECT table_id,tbl_name FROM pm_master_table_lookup_view
	    WHERE host_id=".$this->level['hc_id']."
	    AND db_id=".$this->level['dn_id'];
	if (isset($this->level['sn_id'])) {
	    $tbl_list_q.=" AND schema_id=".$this->level['sn_id'];
	}
	$this->sql->select_c($tbl_list_q);
	$tbl_list=$this->sql->get_result();
	$template='';
	foreach ($tbl_list as $tbl) {
	    foreach ($tbl as $p=>$v) {
		$template.="$p => $v <br>";
	    }
	}
	return $template;
    }


    private function _create_host_info() {
	$template='';
	if (isset($this->level['hc_id']) and $this->status_header === NULL) {
	    $hc=new HostCluster($this->level['hc_id']);
	    $this->host_info="Host: <b>".$hc->get_field('hostname')."</b><br>IP Addres: <b>".$hc->get_field('param_ip_address')."</b>";
	    $this->host_stat=$hc->get_stat();
	    $template.="
		<tr valign=top>
		    <td width=19%>".$this->host_info."</td>
		    <td>".$this->host_stat."</td>
		</tr>";
	    $template.=$this->_create_db_info();
	}
	return $template;
    }


}

?>
