<?
include_once("header.php");
include_once("form_functions.php");
?>
<center><h3>Pg-Mon</h3></center>

<table border=0 width=100%>
    <tr align=center bgcolor=#CCCCCC>
	<td width=14%><b>Hosts<b></td>
	<td><b>Results<b></td>
    </tr>
    <tr>
	<td valign=top>
<?
include_once("dispatcher.php");
?>	</td>
	<td valign=top>
<?
if (isset($_GET['action'])) {
    if ($_GET['action'] == 'add') {
	eval("add_".$_GET['object']."_form();");
    }
    if ($_GET['action'] == 'stat') {
	$_SESSION['action']='stat';
	$_SESSION['host_id']=$_GET['host_id'];
	include_once("result_page.php");
    }
} else {
    echo "Welcome to pg-Mon";
}
?>
	</td>
    </tr>
</table>

<br>

<?
include_once("footer.php");
?>
