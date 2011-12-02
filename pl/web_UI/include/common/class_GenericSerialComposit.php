<?
require_once("class_GenericRowSerial.php");
require_once("class_GenericObjectCollection.php");

/********************************************************************************************************/
/* This class represents one row from any table which hase non composit not autoincremented PRIMARY KEY */
/********************************************************************************************************/

class GenericSerialComposit extends GenericRowSerial {
    protected $composit;
    protected $composit_populated;
    protected $composit_link_fk;
    protected $composit_alive_field;

    public function __construct($table_name, $pk, $composit_link_fk, $composit_table_name, $composit_class_name, $composit_pk, $my_id, $composit_alive_field='alive') {
	parent::__construct($table_name,$pk,$my_id);
	$this->composit=new GenericObjectCollection($composit_table_name,$composit_class_name,$composit_pk);
	$this->composit_link_fk=$composit_link_fk;
	$this->composit_populated=false;
	$this->composit_alive_field=$composit_alive_field;
	if ($my_id) {
	    $this->_populate_composit_array();
	}
    }

    public function load() {
	parent::load();
	$this->_populate_composit_array();
    }


    public function get_composit_array() {
	if (!$this->loaded) {
	    $this->load();
	}
	return $this->composit->get_object_array();
    }

    public function composit_obj_exists($composit_field,$composit_name) {
	foreach ($this->get_composit_array() as $composit) {
	    if ($composit->get_field($composit_field) == $composit_name) {
		return $composit->get_id();
	    }
	}
	return false;
    }

    protected function _populate_composit_array() {
	if (!$this->composit_populated) {
	    $stmt="SELECT ".$this->composit->get_pk()." FROM ".$this->composit->get_table_name()." WHERE ".$this->composit_link_fk."=".$this->id." AND ".$this->composit_alive_field;
	    $this->sql->select_c($stmt);
	    foreach ($this->sql->get_result() as $fk_id) {
		$this->composit->add_id($fk_id[$this->composit->get_pk()]);
	    }
	    $this->composit_populated=true;
	}
    }
}

?>
