<?
include_once("include/class_SQL.php");

class GenericInfo {
    protected $string;
    protected $sql;
    protected $level=NULL;

    public function __construct() {
	$this->sql=SQL::factory();
    }

    protected function _define_level() {
	$this->level=array();
	$this->level=$_SESSION['level'];
    }


    public function get_string() {
	return $this->string;
    }


}

?>
