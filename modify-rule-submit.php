<?
// $link=mysql_connect('localhost','root');
// mysql_select_db('english',$link);
require 'mysql.php';

$query = sprintf("UPDATE rules SET type = '%s', content = '%s' WHERE rule_id = '%s'",
	mysql_real_escape_string(stripslashes($_POST['type'])),
	mysql_real_escape_string(stripslashes($_POST['content'])),
	mysql_real_escape_string(stripslashes($_POST['rule_id'])));
echo $query,"<br>";
mysql_query($query);

// update the function table/id
// need to determine if there used to be a function before this edit
$query = sprintf("SELECT function_id FROM matches WHERE rule_id = '%s' LIMIT 1",
			mysql_real_escape_string($_POST['rule_id']));
echo $query,"<br>";
$matches = mysql_query($query);
$matchrow = mysql_fetch_array($matches, MYSQL_ASSOC);
$old_function_id = htmlspecialchars($matchrow['function_id']);
if($old_function_id == "") {	// if there didn't used to be a match_function
	// if there still isn't a match_function, don't need to do anything
	if($_POST['match_function'] == "") {
		$function_id = "NULL";
	} else {	// if there is a match_function now
		$query = sprintf("INSERT INTO functions (function) VALUES ('%s')",
			mysql_real_escape_string(stripslashes($_POST['match_function'])));
		echo "$query<br>";
		mysql_query($query);
		
		$result = mysql_query("select LAST_INSERT_ID()");
		$row = mysql_fetch_array($result, MYSQL_ASSOC);
		$function_id = $row['LAST_INSERT_ID()'];		
	}
} else {
	// if there used to be a match_function, but there isn't anymore ...
	if($_POST['match_function'] == "") {
		// delete the old one
		$query = sprintf("DELETE FROM functions WHERE function_id = '%s'",
			mysql_real_escape_string($old_function_id));
		echo "$query<br>";
		mysql_query($query);
		$function_id = "NULL";
	} else {	// if there is a match_function now and there was one before too
		$query = sprintf("UPDATE functions SET function = '%s', type = '%s' WHERE function_id = '%s'",
			mysql_real_escape_string(stripslashes($_POST['match_function'])),
			mysql_real_escape_string(stripslashes($_POST['match_function_type'])),
			mysql_real_escape_string($old_function_id));
		echo "$query<br>";
		mysql_query($query);
	
		$function_id = $old_function_id;
	}
}


// remove all of the old rule matches
$query = sprintf("DELETE FROM matches WHERE rule_id = %s;",
	mysql_real_escape_string(stripslashes($_POST['rule_id'])));
echo $query,"<br>";
mysql_query($query);

$rule_id = $_POST['rule_id'];

$matchtypeary = split(",", $_POST['matchtype']);
$matchary = split(",", $_POST['match']);
foreach ($matchtypeary as &$matchtype) {
	$matchtype = trim($matchtype);
	foreach ($matchary as &$match) {
		$match = trim($match);
		$query = sprintf("INSERT INTO matches VALUES ('%s', '%s', %s, '%s')",
			mysql_real_escape_string(stripslashes($matchtype)),
			mysql_real_escape_string(stripslashes($match)),
			mysql_real_escape_string(stripslashes($function_id)),
			mysql_real_escape_string(stripslashes($rule_id)));
		echo $query,"<br>";
		mysql_query($query);
	}
}

?>
<!-- <META HTTP-EQUIV="Refresh" CONTENT="0; URL=show-rules.php?language=<?php echo $language; ?>"> -->
