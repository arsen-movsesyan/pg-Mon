<?
require_once("class_GOpm.php");

class DatabaseName extends GOpm {
    protected $stat_query;

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


#    public function get_stat($start=1,$end=0) {
#	$ret='';
#	$this->stat_query="SELECT dsd.*
#	    FROM pm_database_stat_diff(%s,%s) dsd
#	    JOIN pm_master_db_lookup_view mdv ON dsd.db_id=mdv.db_id
#	    WHERE mdv.host_id=".$this->get_field('hc_id')."
#	    AND mdv.db_id=".$this->get_id();
#	$stat=parent::get_stat($start,$end);
#	if (count($stat) == 0) {
#	    $ret="No statistic available";
#	} else {
#
#	}
#	return $ret;
#    }
}

?>
