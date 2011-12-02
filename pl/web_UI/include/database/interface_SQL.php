<?
interface SQL {
    public function select_c($sql);
    public function non_select_c($sql);
    public function escape($string);
    public function get_result();
    public function get_row_hash($row_num);
    public function get_last_error();
    public function get_last_query();
    public function get_num_rows();
}
?>
