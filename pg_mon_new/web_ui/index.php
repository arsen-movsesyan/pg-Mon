<?
include_once("header.php");

#define("FILE_LOCATION",'/usr/home/arsen/work/LMS/common/file_location/');

#if (!empty($_POST)) {

#}

?>
<center><h3>Pg-Mon</h3></center>
<table border=1 width=100%>
    <tr align=center bgcolor=#CCCCCC>
	<td width=20%><b>Hosts<b></td>
	<td><b>Results<b></td>
    </tr>
    <tr>
	<td>
<?
include_once("dispatcher.php");
?>	</td>
	<td>Result</td>
    </tr>
</table>

<br>

<?
include_once("footer.php");
?>
