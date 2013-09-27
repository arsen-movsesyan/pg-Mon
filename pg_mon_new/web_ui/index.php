<?
include_once("form_functions.php");
include_once("post_functions.php");
include_once("classes/class_HostList.php");
include_once("classes/class_Stat.php");


$result_page='';
$host_list='';

$hl=new HostList();
$st=new Stat();


if (isset($_GET['action'])) {
    if ($_GET['action'] == 'add') {
	$result_page.=add_host_form();
#    } elseif ($_GET['action'] == 'stat') {
#	;
    } else {
	$st->set_level($hl->get_level());
    }
} else {
    if (isset($_POST['add_host_submit'])) {
	$new_host_id=add_host($_POST);
	$st->set_header("Host <b>".$_POST['in_host_name']."</b> successfully added");
    }
}

$host_list.=$hl->get_string();
$result_page.=$st->get_string();

include_once("template.php");
?>
