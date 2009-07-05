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

mysql_select_db($language, $link);

?>
