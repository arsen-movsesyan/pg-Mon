<?

?>
<html>
<head>
<title>Pg-Mon</title>
</head>

<link href="styles.css" rel="stylesheet" type="text/css" />

<body>

<table border="1" class="main">
<tbody>
    <tr>
	<td class="logo">Logo</td>
	<td class="top_info"><?=$result_page?></td>
	<td class="config"><div class="range_set"><?=select_range_form()?></div></td>
    </tr><tr>
	<td class="search">Search</td>
	<td class="top_menu">

<table class="main">
  <tr>
    <td class="menuitem"><a class="menu" href="<?$_SERVER['PHP_SELF']?>?action=home">Home</a></td>
    <td class="menuitem"><a class="menu" href="<?$_SERVER['PHP_SELF']?>?action=stat&info=bi">Basic Info</a></td>
    <td class="menuitem"><a class="menu" href="<?$_SERVER['PHP_SELF']?>?action=stat&info=iu">Index Usage</a></td>
    <td class="menuitem"><a class="menu" href="<?$_SERVER['PHP_SELF']?>?action=stat&info=hs">HOT Stat</a></td>
    <td class="menuitem"><a class="menu" href="<?$_SERVER['PHP_SELF']?>?action=stat&info=ps">Heap Stat</a></td>
    <td class="menuitem"><a class="menu" href="<?$_SERVER['PHP_SELF']?>?action=stat&info=vs">Vacuum Stat</a></td>
    <td class="menuitem"><a class="menu" href="<?$_SERVER['PHP_SELF']?>?action=stat&info=ih">Index Hit Stat</a></td>
    <td class="menuitem"><a class="menu" href="<?$_SERVER['PHP_SELF']?>?action=logout">Logout</a></td>
  </tr>
</table>

	</td>
	<td class="right_thin">Reserved</td>
    </tr><tr>
	<td class="host_list"><?=$host_list?></td>
	<td class="main_stat"><?=$stat_info?></td>
	<td class="table_list"><?=$table_list?></td>
    </tr><tr>
	<td class="copyright">Copyright</td>
	<td class="bottom" colspan="2">Bottom</td>
    </tr>
<tbody>
</table>
</body>
</html>
