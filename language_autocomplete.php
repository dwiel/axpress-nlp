<?
require 'mysql.php';

if(isset($_POST['q'])) {
  $q = stripslashes($_POST['q']);
} else {
  $q = stripslashes($_GET['q']);
}

$result = mysql_query(sprintf("select * from languages where name like '%s%%'", mysql_real_escape_string($q)));
while($row = mysql_fetch_array($result, MYSQL_ASSOC))
{
  echo $row['name'];
  echo "\n";
}

?>
