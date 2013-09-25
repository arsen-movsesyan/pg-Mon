<?
include_once("header.php");
include_once("form_functions.php");
include_once("post_functions.php");
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
home_link();
include_once("dispatcher.php");
?>	</td>
	<td valign=top>
<?
if (isset($_GET['action'])) {
    if ($_GET['action'] == 'add') {
	eval("add_".$_GET['object']."_form();");
    } elseif ($_GET['action'] == 'stat') {
	$_SESSION['action']='stat';
	$_SESSION['host_id']=$_GET['host_id'];
#	if ($_GET['level'] == 'host') {
#	    include_once("result_page.php");
#	}
	if ($_GET['level'] == 'db') {
	    $_SESSION['db_id']=$_GET['db_id'];
	}
	if ($_GET['level'] == 'sch') {
	    $_SESSION['sch_id']=$_GET['sch_id'];
	}
	$_SESSION['level']=$_GET['level'];
	include_once("result_page.php");
    }

} else {
    if (isset($_POST['add_host_submit'])) {
	add_host($_POST);
	unset($_POST);
	home_link();
    } else {
	echo "Welcome to pg-Mon";
    }
}
?>
	</td>
    </tr>
</table>

<br>

<?
include_once("footer.php");
?>
