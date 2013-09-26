<pre>
<?
#$url = 'http://username:password@hostname/path?arg=value#anchor';
$url = 'http://hostname.com/path/to/some/api/?arg=value#anchor';

print_r(parse_url($url));


#echo parse_url($url, PHP_URL_PATH);

$path_parts = pathinfo('/www/htdocs/inc/lib.inc.php');
echo '/www/htdocs/inc/lib.inc.php'."<br><br>";

print_r($path_parts);

?>
</pre>