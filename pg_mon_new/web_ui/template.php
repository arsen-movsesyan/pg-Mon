<?

?>
<html>
<head>
<title>Pg-Mon</title>
</head>
<link href="styles.css" rel="stylesheet" type="text/css" />
<body vlink="blue">
<table border="1" class="main">
<tbody>
    <tr>
	<td class="top" colspan="2"><div class="range_set"><?=select_range_form()?></div></td>
    </tr><tr>
	<td class="host_text">Hosts</td>
	<td class="topmenu"><a href=<?=$_SERVER['PHP_SELF']?>?action=home>Home</a></td>
    </tr><tr>
	<td class="host_list"><a href=<?=$_SERVER['PHP_SELF']?>?action=add&object=host>Add host</a>
	<?=$host_list?></td>
	<td class="main_window"><?=$result_page?></td>
    </tr><tr>
	<td class="copyright">Copyright</td>
	<td class="bottom">Botom</td>
    </tr>
</tbody>
</table>
</body>
</html>