<html>
<body>
<? require 'mysql.php' ?>
<? require 'header.php' ?>
<br><br>
<form method="POST" action="new-rule-submit.php">
<input type="hidden" name="language" value="<?php echo $language; ?>" />
Matches: <input type="text" size=100 name="match" /><br>
Matchtype: <input type="text" size=100 name="matchtype" /><br>
Type:	<select name="type">
		  <option>Function</option>
			<option>Python</option>
		  <option>Query</option>
		  <option>Data</option>
		</select><br>
Content:<br><textarea rows="20" cols="100" name="content"></textarea><br>
Match Function Type:<select name="match_function_type">
	<option>Function</option>
	<option>Python</option>
</select><br>
Match Function:<br><textarea rows="20" cols="100" name="match_function"></textarea><br>
<input type="submit" />
</form>
</body>
</html>
