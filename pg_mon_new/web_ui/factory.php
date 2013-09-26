<?
class MySQL {

    private $result = NULL;
    private $link = NULL;
    private static $instance = NULL;

// returns a singleton instance of MySQL class (chainable)

    public static function factory($host, $user, $password, $database) {
	if (self::$instance === NULL) {
	    self::$instance = new MySQL($host, $user, $password, $database);
	}
	return self::$instance;
    }

// connect to MySQL
    public function __construct($host, $user, $password, $database) {
	if (FALSE === ($this->link = mysqli_connect($host, $user, $password, $database))) {
	    throw new Exception('Error : ' . mysqli_connect_error());
	}
    }

// perform query
    public function query($query) {
	if (is_string($query) AND empty($query) === FALSE) {
	    if (FALSE === ($this->result = mysqli_query($this->link, $query))) {
		throw new Exception('Error performing query ' . $query . ' Error message :' .mysqli_error($this->link));
	    }
	}
    }

// fetch row from result set
    public function fetch() {
	if (FALSE === ($row = mysqli_fetch_assoc($this->result))) {
	    mysqli_free_result($this->result);
	    return FALSE;
	}
	return $row;
    }

// get insertion ID
    public function getInsertID() {
	return mysqli_insert_id($this->link);
    }

// count rows in result set
    public function countRows() {
	if ($this->result !== NULL) {
	    return mysqli_num_rows($this->result);
	}
    }

// implement destructor to close the database connection
    function __destruct() {
	mysqli_close($this->link);
    }
}

##As you can see, now the “MySQL” class defines a brand new factory method that returns Singletons of the class in question. In doing so, it’s possible to reduce to one the number of database handlers used by the respective persistent class. You'll understand this better if you look at the improved definition of this class, which now reads as follows:

class User {

    private $data = array();
    private $id = NULL;
    private $db = NULL;

// constructor
    public function __construct($id = NULL) {
	$this->db = MySQL::factory('host', 'user', 'password', 'database');
	if ($id !== NULL) {
	    $this->id = $id;
	    $this->db->query('SELECT * FROM users WHERE id=' . $this->id);
	    $this->data = $this->db->fetch();
	}
    }

// set undeclared property
    public function __set($property, $value) {
	if ($property !== 'name' and $property !== 'email') {
	    return;
	}
	$this->data[$property] = $value;
    }

// get undeclared property
    public function __get($property) {
	if (isset($this->data[$property]) === TRUE) {
	    return $this->data[$property];
	}
    }

// save object to session variable
    public function __destruct() {
	if ($this->id === NULL) {
	    $this->db->query("INSERT INTO users (id, name, email) VALUES (NULL, '$this->name', '$this->email')");
	} else {
	    $this->db->query("UPDATE users SET name = '$this->name', email = '$this->email' WHERE id = $this->id");
	}
    }
}
?>
