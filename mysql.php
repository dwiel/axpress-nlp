<?

$link=mysql_connect('localhost','root','badf00d');

# get the language
if(isset($_POST['language'])) {
	$language = stripslashes($_POST['language']);
} else {
	$language = stripslashes($_GET['language']);
}

if(!strcmp($language, '')) {
	$language = 'english';
}

echo 'language:'.$language.':<br />';

mysql_select_db('nlp', $link);

$query = sprintf("SELECT language_id FROM languages WHERE name = '%s'",
  mysql_real_escape_string($language));
$lang_result = mysql_query($query);
$row = mysql_fetch_row($lang_result);
$language_id = $row[0];

?>
