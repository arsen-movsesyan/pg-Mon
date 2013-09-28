<?
include_once("include/class_SQL.php");
include_once("class_HostCluster.php");
include_once("class_DatabaseName.php");
include_once("class_SchemaName.php");

class Stat {
    private $sql;
    private $level=NULL;
    private $string='';
    private $host_info;
    private $host_stat;
    private $dn_info;
    private $dn_stat;

    private $status_header=NULL;

    public function __construct() {
	$this->sql=SQL::factory();
    }

    private function _define_level() {
	$this->level=array();
	$this->level=$_SESSION['level'];
    }

    public function set_header($in_header) {
	$this->status_header=$in_header;
    }

    public function get_string() {
	$ret="<table border=0>";
	$ret.=$this->_create_host_info();
#	$ret.="<tr><td colspan=2><hr width=70%></td></tr>";
#	$ret.=$this->_create_db_info();
#	$this->_create_table_list();
	$ret.="</table>";
	return $ret;
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
	$template="<tr><td colspan=2><hr width=70%></td></tr>
		<tr>
		    <td>
	<table border=0>";
	foreach ($tbl_list as $tbl) {
	    $template.="<tr><td><a href=".$_SERVER['PHP_SELF']."?action=stat&hc_id=".$this->level['hc_id']."&dn_id=".$this->level['dn_id'];
	    if (isset($this->level['sn_id'])) {
		$template.="&sn_id=".$this->level['sn_id'];
	    }
	    $template.="&tn_id=".$tbl['table_id'].">".$tbl['tbl_name']."</a></td></tr>\n";
	}
	$template.="</table>
	</td>";
	return $template;
    }


    private function _create_table_info() {
	$ret='';
	$ret.=$this->_create_table_list();
	$ret.="<td>Stat here</td></tr>";
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
		<tr>
		    <td>".$this->dn_info."</td>
		    <td>".$this->dn_stat."</td>
		</tr>";
	    $template.=$this->_create_table_info();
	}
	return $template;
    }


    private function _create_host_info() {
	if ($this->level == NULL)
	    $this->_define_level();
	$template='';
	if (isset($this->level['hc_id']) and $this->status_header === NULL) {
	    $hc=new HostCluster($this->level['hc_id']);
	    $this->host_info="Hostname: <b>".$hc->get_field('hostname')."</b><br>IP Addres: <b>".$hc->get_field('param_ip_address')."</b>";
	    $this->host_stat=$hc->get_stat();
	    $template.="
		<tr>
		    <td>".$this->host_info."</td>
		    <td>".$this->host_stat."</td>
		</tr>";
	    $template.=$this->_create_db_info();
	}
	return $template;
    }


}

?>
