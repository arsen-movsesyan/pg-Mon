<?
include_once("database/interface_SQL.php");
class PgSQL implements SQL {
    private $result_rows;
    private $num_rows;
    private $last_error;
    private $last_query;
    private $db_conn;
    private $q_handle;

// Input parameter $conn_type defines connection (true=>regular, false=>persistent)
    public function __construct($conf_file,$conn_type=false) {
//	$params=parse_ini_file("config/pg_params.ini",true);
	$params=parse_ini_file($conf_file,true);
	$lc=$params['local_conn'];
	$string='';
	foreach ($lc as $k=>$v) {
	    $string.=$k."=".$v." ";
	}
	$string=trim($string);

	if ($conn_type) {
	    $this->db_conn=pg_pconnect($string);
	} else {
	    $this->db_conn=pg_connect($string);
	}

        if (!is_resource($this->db_conn)) {
	    $this->last_error=pg_last_error($this->db_conn);
	    echo $this->get_last_error()."<br>";
	    echo "Unable to connect to the database using \"$conn_string\"";
	    exit;
	}
	$this->_flush();
    }

    private function _flush() {
	$this->result_rows=array();
	$this->num_rows=0;
	$this->last_error="";
    }

    private function _query($sql) {
	$this->_flush();
	$this->last_query=$sql;
	$q_handle=pg_query($this->db_conn, $sql);

	if (!$q_handle) {
	    $this->last_error=pg_last_error($this->db_conn);
	    echo $this->get_last_error();
	    echo $this->get_last_query();
	    exit;
	}
	$this->q_handle=$q_handle;
	return true;
    }

    public function select_c($sql) {
	$this->_query($sql);
	$this->num_rows=pg_num_rows($this->q_handle);
	while ($row=pg_fetch_assoc($this->q_handle)) {
	    $this->result_rows[]=$row;
	}
        }

    public function non_select_c($sql) {
	$this->_query($sql);
	$this->num_rows=pg_affected_rows($this->q_handle);
	return true;
    }

    public function escape($string) {
	return pg_escape_string($string);
    }

    public function get_result() {
	return $this->result_rows;
    }

    public function get_row_hash($row_num) {
	return $this->result_rows[$row_num];
    }

    public function get_last_error() {
	return $this->last_error."<br>";
    }

    public function get_last_query() {
	return "Query: ".$this->last_query."<br>";
    }

    public function get_num_rows() {
	return $this->num_rows;
    }

/*
    public function __destruct() {
	if (is_resource($this->db_conn)) {
	    pg_close($this->db_conn);
	}
    }
*/
}
?>
