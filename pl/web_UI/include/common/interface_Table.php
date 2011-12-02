<?
interface Table {
    public function get_table_structure();
    public function get_table_name();
    public function get_all_fields();
    public function get_field($field);
    public function set_field($field, $value);
    public function get_id();
    public function save();
    public function destroy();
}
?>
