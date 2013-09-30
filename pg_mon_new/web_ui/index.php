<?
session_start();
include_once("form_functions.php");
include_once("post_functions.php");
include_once("classes/class_HostList.php");
include_once("classes/class_HostDbStat.php");
include_once("classes/class_TableList.php");
include_once("classes/class_Facade.php");

define("DEFAULT_FROM_HOUR_BACK",1);
define("DEFAULT_TO_HOUR_BACK",0);

define_session_vars();
define_session_stat_range();

$host_list='';
$result_page='';
$table_list='';
$stat_info='Stat';

$facade=new Facade();
$hl=new HostList();
$hdst=new HostDbStat();
$tbl=new TableList();

if (isset($_GET['action'])) {
    if ($_GET['action'] == 'add') {
	$result_page=add_host_form();
    } elseif ($_GET['action'] == 'home') {
	reset_conf();
    } elseif ($_GET['action'] == 'stat') {
#	print_r($_GET);
	$stat_info=$_GET['info'];
    } elseif ($_GET['action'] == 'logout') {
	logout();
    }
} else {
    if (isset($_POST['add_host_submit'])) {
	$new_host_id=add_host($_POST);
#	$hdst->set_header("Host <b>".$_POST['in_host_name']."</b> successfully added");
    } elseif (isset($_POST['stat_range_submit'])) {
	define_session_stat_range();
    }
}

$table_list=$facade->wrap_single_column($tbl->get_table_list());
$host_list.=$hl->get_string();

$result_page=$facade->render_top_info($hdst->get_host_info(),$hdst->get_host_stat(),$hdst->get_db_info(),$hdst->get_db_stat());

include_once("template.php");

?>
