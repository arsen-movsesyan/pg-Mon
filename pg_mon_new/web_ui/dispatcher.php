<?
include_once("classes/class_HostCluster.php");
include_once("include/class_SQL.php");

$sql=new SQL();
$sql->select_c("SELECT id FROM host_cluster WHERE alive AND observable");

echo "Regitstered ".$sql->get_num_rows()." hosts<br>";
echo "<a href=index.php?action=add&object=host>Add host</a><br>";
echo "<hr width=70%>";

if ($sql->get_num_rows() > 0) {
    $hosts=$sql->get_result();
    foreach ($hosts[0] as $id) {
	$hc= new HostCluster($id);
	echo "<a href=index.php?action=stat&host_id=".$hc->get_id().">".$hc->get_field('hostname')."</a><br>";
    }
}
?>