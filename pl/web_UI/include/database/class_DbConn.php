<?
require_once("database/class_PgSQL.php");

//class DbConn extends MySQL {
class DbConn extends PgSQL {

    public function DbConn($conf_file,$type=false) {
	parent::__construct($conf_file,$type);
    }
    public function select_c($sql) {
	parent::select_c($sql);
    }
    public function non_select_c($sql) {
	parent::non_select_c($sql);
    }

    public function escape($string) {
	return parent::escape($string);
    }

    public function get_result() {
	return parent::get_result();
    }

    public function get_row_hash($row_num=0) {
	return parent::get_row_hash($row_num);
    }

    public function get_last_error() {
	return parent::get_last_error();
    }

    public function get_last_query() {
	return parent::get_last_query();
    }

    public function get_num_rows() {
	return parent::get_num_rows();
    }
}

?>
