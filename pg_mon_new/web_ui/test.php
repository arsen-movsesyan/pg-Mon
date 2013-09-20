<?
function foo($in_a,$in_b) {
    echo "a => $in_a<br>";
    echo "b => $in_b<br>";
    echo "Number of arguments ".func_num_args()."<br>";
    if (func_num_args() > 2) {
	$args=func_get_args();
	for ($n=2;$n<func_num_args();$n++) {
	    echo "Argument: ".$args[$n]."<br>";
	}
    }
}

foo('asd','dfr','s','f','g','h','j');

?>
