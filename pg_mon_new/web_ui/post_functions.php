<?
include_once("classes/class_HostCluster.php");

function add_host($in_post) {
    $hc=new HostCluster();
    $hc->set_field('hostname',$in_post['in_host_name']);
    $hc->set_field('param_ip_address',$in_post['in_ip_address']);
    unset($in_post['in_host_name']);
    unset($in_post['in_ip_address']);
    unset($in_post['add_host_submit']);
    foreach (array_keys($in_post) as $param) {
	if ($in_post[$param]) {
	    switch ($param)  {
	    case 'in_username'		: $hc->set_field('param_user',$in_post['in_username']);break;
	    case 'in_password'		: $hc->set_field('param_password',$in_post['in_password']);break;
	    case 'in_db_name'		: $hc->set_field('param_maintenance_dbname',$in_post['in_db_name']);break;
	    case 'in_is_slave'		: $hc->set_field('is_master','f');break;
	    case 'in_suspended'		: $hc->set_field('observable','f');break;
	    case 'in_ssl_mode'		:
		if ($in_post['in_ssl_mode'] != '3') {
		    $hc->set_field('param_sslmode_id',$in_post['in_ssl_mode']);
		}
		break;
	    case 'in_port'		: $hc->set_field('param_port',$in_post['in_port']);break;
	    case 'in_fqdn'		: $hc->set_field('fqdn',$in_post['in_fqdn']);break;
	    case 'in_description'	: $hc->set_field('description',$in_post['in_description']);break;
	    }
	}
    }
    $hc->Save();
    return $hc->get_id();
}

?>
