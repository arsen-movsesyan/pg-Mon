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

<table border="1" class="main">
  <tr>
    <td class="menuitem"><a class="menu" href="<?$_SERVER['PHP_SELF']?>?action=home">Home</a></td>
    <td class="menuitem"><a class="menu" href="<?$_SERVER['PHP_SELF']?>?action=add">Add Host</a></td>
    <td class="menuitem"><a class="menu" href="<?$_SERVER['PHP_SELF']?>?action=stat&info=bi<?=$stat_link?> ">Basic Info</a></td>
    <td class="menuitem"><a class="menu" href="<?$_SERVER['PHP_SELF']?>?action=stat&info=iu<?=$stat_link?> ">Seq/Idx Scans</a></td>
    <td class="menuitem"><a class="menu" href="<?$_SERVER['PHP_SELF']?>?action=stat&info=is<?=$stat_link?> ">Index Stat</a></td>
    <td class="menuitem"><a class="menu" href="<?$_SERVER['PHP_SELF']?>?action=stat&info=hs<?=$stat_link?> ">HOT Stat</a></td>
    <td class="menuitem"><a class="menu" href="<?$_SERVER['PHP_SELF']?>?action=stat&info=ps<?=$stat_link?> ">Heap Stat</a></td>
    <td class="menuitem"><a class="menu" href="<?$_SERVER['PHP_SELF']?>?action=stat&info=vs<?=$stat_link?> ">Vacuum Stat</a></td>
<!--
    <td class="menuitem"><a class="menu" href="<?$_SERVER['PHP_SELF']?>?action=stat&info=ih<?=$stat_link?> ">Index Hit Stat</a></td>
-->
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
</tbody>
</table>
</body>
</html>
