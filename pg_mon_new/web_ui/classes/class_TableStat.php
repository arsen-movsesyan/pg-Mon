<?

include_once("include/class_GenericInfo.php");

class TableStat extends GenericInfo {
# Basic Usage
    private $bi_stmt;
# Index Usage
    private $iu_stmt;
# HOT Updates
    private $hs_stmt;
# Heap usage
    private $ps_stmt;
# Heap usage
    private $is_stmt;
# Vacuum Analyze stat
    private $vs_stmt;

    public function __construct() {
	parent::__construct();
	$this->bi_stmt="SELECT mtl.tbl_name,tsv.* 
	    FROM pm_master_table_lookup_view mtl
	    JOIN pm_table_size_view tsv ON mtl.table_id=tsv.table_id
	    WHERE mtl.host_id=%s
	    AND mtl.db_id=%s";
	$this->iu_stmt="SELECT mtl.tbl_name,vip.*
	    FROM pm_master_table_lookup_view mtl
	    JOIN vw_index_pct(".$_SESSION['from_hour_back'].",".$_SESSION['to_hour_back'].") vip ON mtl.table_id=vip.table_id 
	    WHERE mtl.host_id=%s AND mtl.db_id=%s";
	$this->hs_stmt="SELECT mtl.tbl_name,hup.*
	    FROM pm_master_table_lookup_view mtl
	    JOIN vw_hot_update_pct(".$_SESSION['from_hour_back'].",".$_SESSION['to_hour_back'].") hup ON mtl.table_id=hup.table_id
	    WHERE mtl.host_id=%s
	    AND mtl.db_id=%s";
	$this->ps_stmt="
	    SELECT mtl.tbl_name,thp.*
	    FROM pm_master_table_lookup_view mtl
	    JOIN vw_table_heap_pct(".$_SESSION['from_hour_back'].",".$_SESSION['to_hour_back'].") thp ON mtl.table_id=thp.table_id
	    WHERE mtl.host_id=%s
	    AND mtl.db_id=%s";
	$this->is_stmt="SELECT mtl.table_id,mtl.tbl_name,mil.idx_name,isv.idx_size AS real_size,isd.index_id,isd.idx_scan,isd.idx_tup_read,isd.idx_tup_fetch
	    FROM pm_master_index_lookup_view mil
	    JOIN pm_master_table_lookup_view mtl ON mtl.table_id=mil.table_id
	    JOIN pm_index_stat_diff(".$_SESSION['from_hour_back'].",".$_SESSION['to_hour_back'].") isd ON mil.index_id=isd.index_id
	    JOIN pm_index_size_view isv ON isd.index_id=isv.index_id
	    WHERE mtl.host_id=%s
	    AND mtl.db_id=%s";
	$this->vs_stmt="SELECT mtl.table_id,mtl.tbl_name,lvs.last_vacuum,lvs.last_autovacuum,lvs.last_analyze,lvs.last_autoanalyze
	    FROM pm_last_va_stat lvs
	    JOIN pm_master_table_lookup_view mtl ON mtl.table_id=lvs.table_id
	    WHERE mtl.host_id=%s
	    AND mtl.db_id=%s";
    }


    public function get_stat_info($info_type,$order_by=false) {
	if ($this->level == NULL)
	    $this->_define_level();
	$si=array();
	if (isset($this->level['dn_id'])) {
	    $stmt=$this->{$info_type."_stmt"};
	    if (isset($this->level['sn_id']))
		$stmt.=" AND mtl.schema_id=".$this->level['sn_id'];
	    if ($order_by)
		$stmt.=" ORDER BY ".$order_by;
	    $query=sprintf($stmt,$this->level['hc_id'],$this->level['dn_id']);
#	    echo $query."<br>";
	    $this->sql->select_c($query);
	    $si=$this->sql->get_result();
	}
	return $si;
    }

}

?>
