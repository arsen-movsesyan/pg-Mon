<?
include_once("classes/class_HostCluster.php");
include_once("include/class_SQL.php");

$sql=new SQL();
#$sql->select_c("SELECT id FROM host_cluster WHERE alive AND observable");
$sql->select_c("SELECT id FROM host_cluster");

echo "<hr width=70%>";
echo "<a href=index.php?action=add&object=host>Add host</a><br>";
echo "<hr width=70%>";
echo "Regitstered ".$sql->get_num_rows()." hosts<br>";

if ($sql->get_num_rows() > 0) {
    $hosts=$sql->get_result();
    foreach ($hosts as $id) {
#	echo $id['id']."<br>";
	$hc= new HostCluster($id['id']);
	echo "<a href=index.php?level=host&action=stat&host_id=".$hc->get_id().">".$hc->get_field('hostname')."</a><br>";
    }
}
?>