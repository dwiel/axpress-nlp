<html>
<body>
<?
include 'mysql.php';
include 'header.php';

$_GET['id'] = intval($_GET['id']);

$query = sprintf("select * from rules where rule_id='%s'",
				 mysql_real_escape_string($_GET['rule_id']));
$result = mysql_query($query);
$row = mysql_fetch_array($result, MYSQL_ASSOC);

$row['matchtype'] = preg_replace('/"/', '&#34;', $row['matchtype']);
$row['type'] = preg_replace('/"/', '&#34;', $row['type']);
$row['content'] = preg_replace('/"/', '&#34;', $row['content']);
$row['match_function'] = preg_replace('/"/', '&#34;', $row['match_function']);

if($row['type'] == "function") {
	$function_selected = "SELECTED";
} elseif ($row['type'] == "python") {
	$python_selected = "SELECTED";
} elseif ($row['type'] == "query") {
	$query_selected = "SELECTED";
} elseif ($row['type'] == "data") {
	$data_selected = "SELECTED";
}

// builf the matches string
$query = sprintf("SELECT m FROM matches WHERE rule_id = '%s' AND matchtype = (SELECT matchtype FROM matches WHERE rule_id = '%s' LIMIT 1);",
			mysql_real_escape_string($row['rule_id']),
			mysql_real_escape_string($row['rule_id']));
$matches = mysql_query($query);
$matches_string = "";
while($matchrow = mysql_fetch_array($matches, MYSQL_ASSOC))
{
	$matches_string .= htmlspecialchars($matchrow['m']) . ", ";
}
$matches_string = substr($matches_string, 0, strlen($matches_string) - 2);

// build the matchtypes string
$query = sprintf("SELECT DISTINCT matchtype FROM matches WHERE rule_id = '%s' AND m = (SELECT m FROM matches WHERE rule_id = '%s' LIMIT 1);",
			mysql_real_escape_string($row['rule_id']),
			mysql_real_escape_string($row['rule_id']));
$matchtypes = mysql_query($query);
$matchtypes_string = "";
while($matchtyperow = mysql_fetch_array($matchtypes, MYSQL_ASSOC))
{
	$matchtypes_string .= htmlspecialchars($matchtyperow['matchtype']) . ", ";
}
$matchtypes_string = substr($matchtypes_string, 0, strlen($matchtypes_string) - 2);

// get the match function
$query = sprintf("SELECT function, type FROM functions WHERE function_id = (SELECT function_id FROM matches WHERE rule_id = '%s' LIMIT 1);",
			mysql_real_escape_string($row['rule_id']));
$matches = mysql_query($query);
$matchrow = mysql_fetch_array($matches, MYSQL_ASSOC);
$match_function = htmlspecialchars($matchrow['function']);
$match_function_type = htmlspecialchars($matchrow['type']);

echo $match_function_type;
if($match_function_type == "function") {
	$match_type_function_selected = "SELECTED";
} elseif ($match_function_type == "python") {
	$match_type_python_selected = "SELECTED";
}				

?>
<br><br>
<form method="POST" action="delete-rule-submit.php">
	<input type="hidden" name="language" value="<?php echo $language; ?>" />
	<input type="hidden" name="rule_id" value="<? echo $_GET['rule_id'] ?>" />
	<input type="submit" value="delete"/>
</form>
<form method="POST" action="modify-rule-submit.php">
<input type="submit" value="Submit"/><br><br>
<input type="hidden" name="language" value="<?php echo $language; ?>" />
Matches: <input type="text" size=100 name="match" value="<? echo $matches_string; ?>"/><br>
Matchtype: <input type="text" size=100 name="matchtype" value="<? echo $matchtypes_string; ?>"/><br>
Type:	<select name="type">
		  <option <?php echo $function_selected; php?> value="Function">Function</option>
			<option <?php echo $python_selected; php?> value="Python">Python</option>
		  <option <?php echo $query_selected; php?> value="Query">Query</option>
		  <option <?php echo $data_selected; php?> value="Data">Data</option>
		</select><br>
Content:<br><textarea rows="20" cols="100" name="content"><? echo $row['content']; ?></textarea><br>
Match Function Type: <select name="match_function_type">
<option <?php echo $match_type_function_selected; php?> value="Function">Function</option>
<option <?php echo $match_type_python_selected; php?> value="Python">Python</option>
</select><br>
Match Function: <br><textarea rows="20" cols="100" name="match_function"><? echo $match_function; ?></textarea><br>
<input type="hidden" name="rule_id" value="<? echo $_GET['rule_id'] ?>" />
<input type="submit" value="Submit"/>
</form>
</body>
</html>
