<?
require_once("class_GOpm.php");

class DatabaseName extends GOpm {

    public function DatabaseName($in_id=false) {
	parent::initialize('database_name',$in_id);
	$this->depend_obj='schema_name';
	$this->reference_field='dn_id';

    }


    public function get_stat($start=1,$end=0) {
	$this->stat_query="SELECT dsd.*
	    FROM pm_database_stat_diff(%s,%s) dsd
	    JOIN pm_master_db_lookup_view mdv ON dsd.db_id=mdv.db_id
	    WHERE mdv.host_id=".$this->get_field('hc_id')."
	    AND mdv.db_id=".$this->get_id();
	parent::get_stat($start,$end);
    }
}

?>
