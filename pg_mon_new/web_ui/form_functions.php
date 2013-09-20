<?
function add_host_form() {
?>
<form name=add_host_form method=POST action=index.php>
<table border=1>
    <tr>
	<td>Host Name</td>
	<td><input type=text name=in_host_name required></td>
    </tr><tr>
	<td>IP Address</td>
	<td><input type=text name=in_ip_address required></td>
    </tr><tr>
</table>
</form>
<?
}

?>