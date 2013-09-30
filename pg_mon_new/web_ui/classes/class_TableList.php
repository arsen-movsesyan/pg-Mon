<?

include_once("include/class_GenericInfo.php");

class TableList extends GenericInfo {
    private $table_list;

    public function __construct() {
	$this->sql=SQL::factory();
    }

    private function _create_table_list() {
	$tbl_list_q="SELECT table_id,tbl_name FROM pm_master_table_lookup_view
	    WHERE host_id=".$this->level['hc_id']."
	    AND db_id=".$this->level['dn_id'];
	if (isset($this->level['sn_id'])) {
	    $tbl_list_q.=" AND schema_id=".$this->level['sn_id'];
	}
	$this->sql->select_c($tbl_list_q);
	$this->table_list=$this->sql->get_result();
    }

    public function get_table_list() {
	if ($this->level == NULL)
	    $this->_define_level();
	if (isset($this->level['dn_id']))
	    $this->_create_table_list();
	return $this->table_list;
    }


    public function get_string() {
	if ($this->level == NULL)
	    $this->_define_level();
	if (isset($this->level['dn_id'])) {
	    $this->_create_table_list();
	    $this->string="<table border=0>";
	    foreach ($this->table_list as $tbl) {
		$this->string.="<tr><td><a href=".$_SERVER['PHP_SELF']."?action=stat&hc_id=".$this->level['hc_id']."&dn_id=".$this->level['dn_id'];
		if (isset($this->level['sn_id'])) {
		    $this->string.="&sn_id=".$this->level['sn_id'];
		}
		$this->string.="&tn_id=".$tbl['table_id'].">".$tbl['tbl_name']."</a></td></tr>\n";
	    }
	    $this->string.="</table>";
	} else {
	    $this->table_string='';
	}
	return parent::get_string();
    }
}

?>
