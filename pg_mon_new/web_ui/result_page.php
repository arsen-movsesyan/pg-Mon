<?
include_once("classes/class_HostCluster.php");
include_once("classes/class_DatabaseName.php");

include_once("include/class_SQL.php");

$header_string='';

if (isset($_SESSION['host_id'])) {
    $hc=new HostCluster($_SESSION['host_id']);
    $header_string="Host <b>".$hc->get_field('hostname')."</b>";
    if (isset($_SESSION['db_id'])) {
	$dn=new DatabaseName($$_SESSION['db_id']);
	$header_string.=" Database <b>".$dn->get_field('db_name')."</b>";
	if (isset($_SESSION['sc_id'])) {
	    if (isset($_SESSION['tn_id'])) {
		;
	    }
	}
    }
}
?>
<table border=1>
    <tr bgcolor=#CCCCCC>
	<td><b>Databases</b></td>
	<td width=100% align=center>Host <b><?=$hc->get_field('hostname')?></b></td>
    </tr><tr valign=top>
	<td>
<?
foreach ($hc->get_dependant_ids() as $db_id) {
    $dn=new DatabaseName($db_id);
    echo $dn->get_field('db_name')."<br>";
}
?>
	</td><td>
<?
	echo "Result here";
?>
	</td>
    </tr>
</table>
<?


?>
