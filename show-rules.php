<html>
<body>
<?
require 'mysql.php';
require 'header.php';
?>
<br><br>
<?

$result = mysql_query('select * from rules');
while($row = mysql_fetch_array($result, MYSQL_ASSOC))
{
	echo "<div class='row'>\n";
	echo "<div class='id'><a href='modify-rule.php?language={$language}&rule_id={$row['rule_id']}'>{$row['rule_id']}</a>\n";

	// get the list of matches
	$query = sprintf("SELECT m FROM matches WHERE rule_id = '%s' AND matchtype = (SELECT matchtype FROM matches WHERE rule_id = '%s' LIMIT 1);",
				mysql_real_escape_string($row['rule_id']),
				mysql_real_escape_string($row['rule_id']));
	$matches = mysql_query($query);
	echo "<div class='matches'>Matches:\n";
	while($matchrow = mysql_fetch_array($matches, MYSQL_ASSOC))
	{
		$matchrow['m'] = htmlspecialchars($matchrow['m']);
		echo "<div class='match'>{$matchrow['m']}</div>\n";
	}
	echo "</div>\n";
	
	// get the list of matchtypes
	$query = sprintf("SELECT matchtype FROM matches WHERE rule_id = '%s' AND m = (SELECT m FROM matches WHERE rule_id = '%s' LIMIT 1);",
				mysql_real_escape_string($row['rule_id']),
				mysql_real_escape_string($row['rule_id']));
	$matches = mysql_query($query);
	echo "<div class='matchetypes'>Matchtypes:\n";
	while($matchrow = mysql_fetch_array($matches, MYSQL_ASSOC))
	{
		$matchrow['matchtype'] = htmlspecialchars($matchrow['matchtype']);
		echo "<div class='match'>{$matchrow['matchtype']}</div>\n";
	}
	echo "</div>\n";
	
	// display the rest of the rule
	$row['rule_id'] = htmlspecialchars($row['rule_id']);
	$row['type'] = htmlspecialchars($row['type']);
	$row['content'] = htmlspecialchars($row['content']);
	echo "Type: <div class='type'>{$row['type']}</div>\n",
	     "Content:<br>\n",
	     "<div class='content'><pre>{$row['content']}</pre></div>\n",
	     "</div>\n";

	// get the match function
	$query = sprintf("SELECT function, type FROM functions WHERE function_id = (SELECT function_id FROM matches WHERE rule_id = '%s' LIMIT 1);",
				mysql_real_escape_string($row['rule_id']));
	$matches = mysql_query($query);
	$matchrow = mysql_fetch_array($matches, MYSQL_ASSOC);
	$matchrow['function'] = htmlspecialchars($matchrow['function']);
	$matchrow['type'] = htmlspecialchars($matchrow['type']);
	echo "<div class='match-function-title'>Match Function Type:\n";
	echo "<div class='match-function-type'>{$matchrow['type']}</div>\n";
	echo "<div class='match-function-title'>Match Function:\n";
	echo "<div class='match-function-code'><pre>{$matchrow['function']}</pre></div>\n";
	echo "</div>\n";
	
}
?>
</body>
</html>
