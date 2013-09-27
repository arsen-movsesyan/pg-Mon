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
	$this->_create_header();
	return $this->status_header."<hr width=70%>".$this->string;
    }

    private function _create_header() {
	if (isset($this->level['hc_id']) and $this->status_header === NULL) {
	    $hc=new HostCluster($this->level['hc_id']);
	    $this->host_info="Host: <b>".$hc->get_field('hostname')."</b><br>IP Addres: <b>".$hc->get_field('param_ip_address')."</b>";
	    $this->host_stat=$hc->get_stat(50,49);
	}
	$this->status_header="
<table border=0 width=100%>
    <tr valign=top>
	<td width=19%>".$this->host_info."<br>".select_range_form()."</td>
	<td>".$this->host_stat."</td>
    </tr>
</table>";
    }


}

?>
