<?
include_once("common/class_GenericTable.php");
include_once("common/interface_GetError.php");

class TableAuthSource extends GenericTable implements GetError {
    protected $login_field;
    protected $password_field;
    protected $error_codes;



    public function __construct($in_table_name,$in_pk_field,$in_l_field,$in_passwd_field) {
	parent::__construct($in_table_name,$in_pk_field,false);
	$this->login_field=$in_l_field;
	$this->password_field=$in_passwd_field;
	$this->error_codes=array();
    }

    public function search($in_login,$in_passwd) {
	$login=strtolower($in_login);
	$login=$this->sql->escape($login);
	$this->sql->select_c("SELECT ".$this->pk." FROM ".$this->table_name." WHERE ".$this->login_field."='".$login."'");
	$l_num=$this->sql->get_num_rows();
	if ($l_num > 1) {
	    $this->error_codes[]=AUTH_ERROR_LOGIN_MULTIPLE;
	} elseif ($l_num == 0) {
	    $this->error_codes[]=AUTH_ERROR_LOGIN_NOT_FOUND;
	} else {
	    $id=$this->sql->get_row_hash();
	    $this->id=$id[$this->pk];
	    $this->load();
	    if ($this->database_fields[$this->password_field] != md5($in_passwd)) {
		$this->error_codes[]=AUTH_ERROR_PASSWORD_MISSMATCH;
	    }
	}
	if (count($this->error_codes) != 0) {
	    return false;
	}
	return true;
    }

    public function get_error() {
	return $this->error_codes;
    }

    public function save() {}
    public function destroy() {}
//    public function set_field($field, $value) {}
}

?>
