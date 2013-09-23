<?
include_once("classes/class_HostCluster.php");
include_once("classes/class_DatabaseName.php");

include_once("include/class_SQL.php");

$hc=new HostCluster($_SESSION['host_id']);
$header_string="Host <b>".$hc->get_field('hostname')."</b>";

#$hc->get_stat();
$intern_string='Host Results here';

if (isset($_SESSION['db_id'])) {
    $dn=new DatabaseName($_SESSION['db_id']);
    $header_string.=" Database <b>".$dn->get_field('db_name')."</b>";
    $intern_string='Database Results here';
    if (isset($_SESSION['sc_id'])) {
	if (isset($_SESSION['tn_id'])) {
	    $intern_string='Table Results here';
	    if (isset($_SESSION['ind_id'])) {
		$intern_string='Index Results here';
	    }
	}
    }
    
}
?>
<table border=1>
    <tr bgcolor=#CCCCCC>
	<td><b>Databases</b></td>
	<td width=100% align=center><?=$header_string?></td>
    </tr><tr valign=top>
	<td>
<?
foreach ($hc->get_dependant_ids() as $db_id) {
    $dn=new DatabaseName($db_id);
    echo "<a href=index.php?level=db&action=stat&host_id=".$hc->get_id()."&db_id=".$db_id.">".$dn->get_field('db_name')."</a><br>";
}
?>
	</td>
	<td><?=$intern_string?></td>
    </tr>
</table>
<?


?>
