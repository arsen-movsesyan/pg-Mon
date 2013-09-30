<?

include_once("include/class_GenericInfo.php");

class TableStat extends GenericInfo {
    private $bi_stmt="
SELECT mtl.tbl_name,tsv.* 
FROM pm_master_table_lookup_view mtl
JOIN pm_table_size_view tsv ON mtl.table_id=tsv.table_id
WHERE mtl.host_id=%s
AND mtl.db_id=%s";
    private $iu_stmt="
SELECT  mtl.tbl_name,vip.*
FROM pm_master_table_lookup_view mtl
JOIN vw_index_pct() vip ON mtl.table_id=vip.table_id
WHERE mtl.host_id=%s
AND mtl.db_id=%s";
    private $hs_stmt="
SELECT mtl.tbl_name,hup.*
FROM pm_master_table_lookup_view mtl
JOIN vw_hot_update_pct() hup ON mtl.table_id=hup.table_id
WHERE mtl.host_id=%s
AND mtl.db_id=%s";
    private $hs_stmt="
SELECT mtl.tbl_name,thp.*
FROM pm_master_table_lookup_view mtl
JOIN vw_table_heap_pct() thp ON mtl.table_id=thp.table_id
WHERE mtl.host_id=%s
AND mtl.db_id=%s";



/*
    public function basic_info($order_by=false) {
	if ($this->level == NULL)
	    $this->_define_level();
	$bi=array();
	if (isset($this->level['dn_id'])) {
	    $bi_stmt="";
	    if (isset($this->level['sn_id']))
		$bi_stmt.=" AND mtl.schema_id=".$this->level['sn_id'];
	    if ($order_by)
		$bi_stmt.=" ORDER BY ".$order_by;
	    $this->sql->select_c($bi_stmt);
	    $bi=$this->sql->get_result();
	}
	return $bi;
    }
*/
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
	    $this->sql->select_c($query);
	    $si=$this->sql->get_result();
	}
	return $si;
    }

}

?>
