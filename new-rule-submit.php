<?
	require 'mysql.php';
	
	// API call takes:
	// language
	// match - what it matches (the string)
	// matchtype - any, name, person, number, etc
	// type - rule type: function, python, query, data
	// content
	// match_function
	// match_function_type  : function, python
	
	$query = sprintf("INSERT INTO rules (type, content) VALUES ('%s', '%s');",
		mysql_real_escape_string(stripslashes($_POST['type'])),
		mysql_real_escape_string(stripslashes($_POST['content'])));
	echo $query,"<br>";
	mysql_query($query);
	
	$result = mysql_query("select LAST_INSERT_ID()");
	$row = mysql_fetch_array($result, MYSQL_ASSOC);
	$rule_id = $row['LAST_INSERT_ID()'];
	
	if($_POST['match_function'] != "") {
		$query = sprintf("INSERT INTO functions, type (function, type) VALUES ('%s', '%s');",
			mysql_real_escape_string(stripslashes($_POST['match_function'])),
			mysql_real_escape_string(stripslashes($_POST['match_function_type'])));
		mysql_query($query);
	
		$result = mysql_query("select LAST_INSERT_ID()");
		$row = mysql_fetch_array($result, MYSQL_ASSOC);
		$function_id = $row['LAST_INSERT_ID()'];
	} else {
		$function_id = "NULL";
	}
	
	$matchtypeary = split(",", stripslashes($_POST['matchtype']));
	$matchary = split(",", stripslashes($_POST['match']));
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

