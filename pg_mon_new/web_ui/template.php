<?
include_once("classes/class_HostCluster.php");
include_once("include/class_SQL.php");

$host_list='';


$sql=new SQL();
#$sql->select_c("SELECT id FROM host_cluster WHERE alive AND observable");
$sql->select_c("SELECT id FROM host_cluster");


$host_list.="<hr width=70%>
<a href=".$_SERVER['PHP_SELF']."?action=add&object=host>Add host</a><br>
<hr width=70%>
Regitstered ".$sql->get_num_rows()." hosts<br>";

if ($sql->get_num_rows() > 0) {
    $hosts=$sql->get_result();
    foreach ($hosts as $id) {
	$hc= new HostCluster($id['id']);
	$host_list.="<a href=".$_SERVER['PHP_SELF']."?level=host&action=stat&host_id=".$hc->get_id().">".$hc->get_field('hostname')."</a><br>";
    }
}


$result_page="Result Page";
?>
<html>
<head>
<title>Pg-Mon</title>
</head>
<body vlink=blue>

<center><h3>Pg-Mon</h3></center>

<table border=0 width=100%>
    <tr valign=top bgcolor=#DDDDDD align=center>
	<td width=18%><b>Host List</b></td>
	<td><b>Result Display</b></td>
    </tr><tr valign=top>
	<td><?=$host_list?></td>
	<td><?=$result_page?></td>
    </tr>
</table>