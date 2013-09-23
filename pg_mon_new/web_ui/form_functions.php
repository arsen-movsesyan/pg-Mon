<?
include_once("include/class_SQL.php");

function add_host_form() {
?>
<form name=add_host_form method=POST action=index.php>
<table border=0>
    <tr>
	<td>Host Name</td>
	<td><input type=text name=in_host_name required></td>
    </tr><tr>
	<td>IP Address</td>
	<td><input type=text name=in_ip_address required></td>
    </tr><tr>
	<td>Username</td>
	<td><input type=text name=in_username placeholder=postgres></td>
    </tr><tr>
	<td>Password</td>
	<td><input type=pasword name=in_password></td>
    </tr><tr>
	<td>Maintenance DB Name</td>
	<td><input name-in_db_name placeholder=postgres></td>
    </tr><tr>
	<td>Is Masetr</td>
	<td><input type=checkbox name=in_is_master checked></td>
    </tr><tr>
	<td>Observable</td>
	<td><input type=checkbox name=in_observable checked></td>
    </tr><tr>
	<td>SSL Mode</td>
	<td><select name=in_ssl_mode>
<?
$in_sql=new SQL();
$in_sql->select_c("SELECT * FROM enum_sslmode");
$ssl_results=$in_sql->get_result();
$option_string='';
for ($i=0;$i<sizeof($ssl_results);$i++) {
    $option_string.="<option value=".$ssl_results[$i]['id'];
    if ($ssl_results[$i]['sslmode'] == 'prefer') {
	$option_string.= " selected";
    }
    $option_string.=">".$ssl_results[$i]['sslmode']."</option>";
}
echo $option_string;
?>
	    </select>
	</td>
    </tr><tr>
	<td>Port</td>
	<td><input type=text name=in_port size=4 placeholder=5432></td>
    </tr><tr>
	<td>FQDN</td>
	<td><input type=text name=in_fqdn></td>
    </tr><tr>
	<td valign=top>Description</td>
	<td><textarea name=in_description></textarea></td>
    </tr><tr align=center>
	<td><input type=submit name=add_host_submit value=Submit></td>
	<td><input type=reset value=Reset></td>
    </tr>
</table>
</form>
<?
}

?>