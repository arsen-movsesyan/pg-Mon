<?
class Facade {
    private $basic_template;

#    public function __construct() {
#
#    }


    public static function wrap_horizontal($in_array,$exclude_field, $table_class="hc_db_stat") {
	if (count($in_array) == 0) {
	    return "No statistic available";
	}
	$keys=$values=array();
	foreach ($in_array[0] as $p=>$v) {
#	    if (array_key_exists($exclude_field,))
	    if ($p == $exclude_field)
		continue;
	    $keys[]=$p;
	    $values[]=$v;
	}
	$ret="<table border=1 class=\"$table_class\"><tr>";
	for ($i=0;$i<count($keys);$i++) {
	    $ret.="<td>".$keys[$i]."</td>";
	}
	$ret.="</tr><tr>";
	for ($i=0;$i<count($values);$i++) {
	    $ret.="<td><b>".$values[$i]."</b></td>";
	}
	$ret.="</tr></table>";
	return $ret;
    }


    public static function wrap_nested_array($in_array,$exclude_field,$table_class="hc_db_stat") {
	if ($in_array) {
	    $param=array_keys($in_array[0]);
	    $ret="<table border=1 class=\"$table_class\"><tr>";
	    for ($i=0;$i<count($param);$i++) {
		if ($param[$i] == $exclude_field)
		    continue;
		$ret.="<td>".$param[$i]."</td>";
	    }
	    $ret.="</tr>";

	    foreach ($in_array as $row) {
		$ret.="<tr>";
		foreach ($row as $p=>$v) {
		    if ($p == $exclude_field)
		    continue;
		    $ret.="<td>".$v."</td>";
		}
		$ret.="</tr>";
	    }
	    $ret.="</table>";
	} else
	    $ret='';
	return $ret;
    }

    public static function wrap_info($in_array,$table_class="hc_db_stat") {
	if ($in_array) {
	    $ret="<table border=1 class=\"$table_class\">";
	    foreach ($in_array as $p=>$v) {
		$ret.="<tr><td>".$p."</td><td><b>".$v."</b></td></tr>";
	    }
	    $ret.="</table>";
	} else
	    $ret='';
	return $ret;
    }

    public static function wrap_single_column($in_array) {
	$ret="<table border=1 class=\"hc_db_stat\">";
	if ($in_array) {
	    foreach ($in_array as $row) {
		$ret.="<tr><td>".$row['tbl_name']."</td></tr>";
	    }
	}
	$ret.="</table>";
	return $ret;
    }


    public function render_top_info($host_info,$host_stat,$db_info,$db_stat) {
	$ret="<table border=1 class= \"top_info\"><tr><td>";
	$ret.=$this->wrap_info($host_info);
	$ret.="</td><td>";
	$ret.=$this->wrap_horizontal($host_stat,'host_id');
	$ret.="</td></tr><tr><td>";
	$ret.=$this->wrap_info($db_info);
	$ret.="</td><td>";
	$ret.=$this->wrap_horizontal($db_stat,'db_id');
	$ret.="</td></tr></table>";
	return $ret;
    }


}

?>
