<?
include_once("include/class_SQL.php");


function add_host_form() {
    $ip_pattern="\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}";
#    $ip_pattern="^(([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\.){3}([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])$";

    $form_string="
<form name=add_host_form method=POST action=".$_SERVER['PHP_SELF'].">
<table border=0>
    <tr>
	<td>Host Name <font color=red>*</font></td>
	<td><input type=text name=in_host_name required></td>
    </tr><tr>
	<td>IP Address <font color=red>*</font></td>
	<td><input type=text name=in_ip_address required pattern=$ip_pattern></td>
    </tr><tr>
	<td colspan=2><hr width=60%></td>
    </tr><tr>
	<td>Username</td>
	<td><input type=text name=in_username placeholder=postgres></td>
    </tr><tr>
	<td>Password</td>
	<td><input type=pasword name=in_password></td>
    </tr><tr>
	<td>Maintenance DB Name</td>
	<td><input name=in_db_name placeholder=postgres></td>
    </tr><tr>
	<td>Is Slave</td>
	<td><input type=checkbox name=in_is_slave> (Default Master)</td>
    </tr><tr>
	<td>Suspend</td>
	<td><input type=checkbox name=in_suspended> (Default Observable)</td>
    </tr><tr>
	<td>SSL Mode</td>
	<td><select name=in_ssl_mode>";

    $in_sql=SQL::factory();
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
    $form_string.=$option_string;
    $form_string.="
	    </select>
	</td>
    </tr><tr>
	<td>Port</td>
	<td><input type=text name=in_port size=4 placeholder=5432 pattern=\"\d{1,5}\"></td>
    </tr><tr>
	<td>FQDN</td>
	<td><input type=text name=in_fqdn></td>
    </tr><tr>
	<td valign=top>Description</td>
	<td><textarea name=in_description></textarea></td>
    </tr><tr>
	<td  colspan=2><hr width=60%></td>
    </tr><tr align=center>
	<td><input type=submit name=add_host_submit value=Submit></td>
	<td><input type=reset value=Reset></td>
    </tr>
</table>
</form>";
    return $form_string;
}

function select_range_form() {
    $ret="<form method=post action=".$_SERVER['PHP_SELF']." oninput=\"start_back.value=r_start.value;
end_back.value=r_end.value\">
    From Hours back <input type=range name=r_start value=1 min=1 max=100>&nbsp;<output name=start_back for=r_start>1</output><br>
    To Hour Back <input type=range name=r_end value=0 min=0 max=99>&nbsp;<output name=end_back for=r_end>0</output><br>
    <input type=submit name=range_submit value=Set></form>";

    return $ret;
}

?>