<?
session_start();
include_once("form_functions.php");
include_once("post_functions.php");
include_once("classes/class_HostList.php");
include_once("classes/class_HostDbStat.php");
include_once("classes/class_TableList.php");
include_once("classes/class_TableStat.php");
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
$table_stat=new TableStat();

if (isset($_REQUEST['action'])) {
    if ($_REQUEST['action'] == 'add') {
	$stat_info=add_host_form();
    } elseif ($_REQUEST['action'] == 'home') {
	reset_conf();
    } elseif ($_REQUEST['action'] == 'stat') {
	$_SESSION['stat_type']=$_REQUEST['info'];
	$stat_list=$table_stat->get_stat_info($_REQUEST['info']);
	$stat_info=$facade->wrap_nested_array($stat_list,'table_id');
    } elseif ($_REQUEST['action'] == 'logout') {
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

$stat_link=render_link();
include_once("template.php");

?>
