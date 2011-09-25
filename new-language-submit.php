<?
require 'mysql.php';

if(isset($_POST['language'])) {
  $language = stripslashes($_POST['language']);
} else {
  $language = stripslashes($_GET['language']);
}

if($language == "") {
  header("Location: show-rules.php");
}

$query = sprintf("SELECT language_id FROM languages WHERE name = '%s'",
  mysql_real_escape_string($language));
$lang_result = mysql_query($query);
$row = mysql_fetch_row($lang_result);
if(gettype($row) != 'array') {
  $sql = sprintf("INSERT INTO languages (name) VALUES ('%s')", mysql_real_escape_string($language));
  $result = mysql_query($sql);
}

header("Location: show-rules.php?language=".$language);
?>
