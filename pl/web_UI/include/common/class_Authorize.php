<?
abstract class Authorize {
    protected $source;
    protected $error;
    protected $id;

    public abstract function validate($in_login,$in_password);

    public function get_source() {
	return $this->source;
    }

    public function get_error() {
	return $this->error;
    }

    public function get_id() {
	return $this->id;
    }
}
?>
