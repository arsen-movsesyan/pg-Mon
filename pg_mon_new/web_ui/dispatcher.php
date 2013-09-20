<?
include_once("classes/class_HostCluster.php");
include_once("include/class_SQL.php");

$sql=new SQL();
$sql->select_c("SELECT id FROM host_cluster WHERE alive AND observable");

echo "Regitstered ".$sql->get_num_rows()." hosts<br>";
echo "Add host<br>";


if ($sql->get_num_rows() > 0) {
} else {
    while ($host=$sql->get_result()) {
	echo "Host is ".$host."<br>";
    }
}
?>