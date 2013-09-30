<?
require_once("class_GOpm.php");

class DatabaseName extends GOpm {
    protected $stat_query;
    private $db_size=NULL;


    public function DatabaseName($in_id=false) {
	parent::initialize('database_name',$in_id);
	$this->depend_obj='schema_name';
	$this->reference_field='dn_id';
	if ($in_id) {
	    $this->stat_query="SELECT dsd.*
		FROM pm_database_stat_diff(%s,%s) dsd
		JOIN pm_master_db_lookup_view mdv ON dsd.db_id=mdv.db_id
		WHERE mdv.host_id=".$this->get_field('hc_id')."
		AND mdv.db_id=".$this->get_id();
	}
    }

    private function _get_db_size($pretty) {
	$sql=SQL::factory();
	$sql->select_c("SELECT db_size,pg_size_pretty(db_size) AS db_size_pretty
FROM database_stat
WHERE time_id=(SELECT MAX(time_id) FROM database_stat)
AND dn_id=".$this->get_id());
	$info=$sql->get_result();
	if ($pretty)
	    $this->db_size=$info[0]['db_size_pretty'];
	else
	    $this->db_size=$info[0]['db_size'];
    }


    public function get_info() {
	if ($this->db_size == NULL) {
	    $this->_get_db_size(true);
	}
	return array('Database'=> $this->get_field('db_name'),
	    'DB Size'=>$this->db_size);
    }

}

?>
