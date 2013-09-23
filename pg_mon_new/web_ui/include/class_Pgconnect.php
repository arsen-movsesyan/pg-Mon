<?
class Pgconnect {
    protected $db_conn;
    protected $last_error;
    protected $last_query;

    public function __construct() {
#	$conn_string="host=localhost user=postgres dbname=pg_mon";
	$conn_string="host=dbmon user=postgres dbname=pg_mon";
	$this->db_conn=@pg_pconnect($conn_string);
	if (!is_resource($this->db_conn)) {
	    throw new Exception("Cannot connect to database ",E_USER_ERROOR);
	}
    }
    public function last_error() {
	return pg_last_error($this->db_conn);
    }
    
    public function get_last_query() {
	return $this->last_query;
    }
    
    public function __destruct() {
	if (is_resource($this->db_conn)) {
	    @pg_close($this->db_conn);
	}
    }
}
?>