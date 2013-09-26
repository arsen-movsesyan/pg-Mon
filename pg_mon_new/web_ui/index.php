<?
#session_start();
include_once("form_functions.php");
include_once("post_functions.php");
include_once("classes/class_HostList.php");

$result_page='';
$host_list='';

$hl=new HostList();
$st=new Stat()


if (isset($_GET['action'])) {
    if ($_GET['action'] == 'add') {
	$result_page.=add_host_form();
#    } elseif ($_GET['action'] == 'stat') {
#	;
    }

} else {
    if (isset($_POST['add_host_submit'])) {
	$new_host_id=add_host($_POST);
	$hl->set_host_id($new_host_id);
    }
}

$host_list.=$hl->get_string();

include_once("template.php");
#print_r($hl->get_nested_array());
#session_destroy();
?>
