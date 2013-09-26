<?

?>
<html>
<head>
<title>Pg-Mon</title>
</head>
<body vlink=blue>

<center><h3>Pg-Mon</h3></center>

<table border=0 width=100%>
    <tr valign=top bgcolor=#DDDDDD align=center>
	<td width=19%><b>Host List</b></td>
	<td><b>Result Display</b></td>
    </tr><tr valign=top>
	<td><a href=<?=$_SERVER['PHP_SELF']?>>Home</a>
	<hr width=70%>
	<a href=<?=$_SERVER['PHP_SELF']?>?action=add&object=host>Add host</a>
	<hr width=70%>
	<?=$host_list?></td>
	<td><?=$result_page?></td>
    </tr>
</table>
