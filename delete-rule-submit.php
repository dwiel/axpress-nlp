<?
require 'mysql.php';

$query = sprintf("delete from rules where rule_id=%s;",
	mysql_real_escape_string(stripslashes($_POST['rule_id'])));
echo $query;
mysql_query($query);

$query = sprintf("delete from matches where rule_id=%s;",
	mysql_real_escape_string(stripslashes($_POST['rule_id'])));
echo $query;
mysql_query($query);

?>
<META HTTP-EQUIV="Refresh" CONTENT="0; URL=show-rules.php?language=<?=$language?>">
