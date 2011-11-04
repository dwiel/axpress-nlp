<?php
	// session can be mapped to a username after logging in ...
	// or the username can be set to anonymous
	
	$link=mysql_connect('localhost','root', 'badf00d');
	mysql_select_db('english',$link);

	session_start();
	if(isset($_SESSION['sid'])) {
		// check to see if this is a valid session
		$query = sprintf("SELECT sid FROM matches WHERE rule_id = '%s' AND matchtype = (SELECT matchtype FROM matches WHERE rule_id = '%s' LIMIT 1);",
				mysql_real_escape_string($row['rule_id']),
				mysql_real_escape_string($row['rule_id']));
		$result = mysql_query($query);
	} else {
		// provide a new session id
		$_SESSION['sid'] = "random";
	}
?>

<html>
	<head>
		<link rel="stylesheet" href="index.css">
	</head>
	<body>
		<div id="middle">
			<div id="please-use-english">
				::english::
			</div>
			<div id="main-form">
				<form action="exec.php" method="post">
					<input id="main-form-query" type="text" name="query" size="40"/>
					<input id="sid" type="hidden" name="sid" value="100"/>
				</form>
			</div>
			<div id="below">
				<div id="below-title">examples:</div>
				<div class="exmaple"><a href="exec.php?query=email">email</a></div>
				<div class="exmaple"><a href="exec.php?query=new email to lucas">new email to lucas</a></div>
				<div class="exmaple"><a href="exec.php?query=emails from last week">emails from last week</a></div>
				<div class="exmaple"><a href="exec.php?query=emails about vacation">emails about vacation</a></div>
			</div>
		</div>
		<div id="description">
			English is an experiment at providing a natural language interface to the domain of email search.  The 
			hope is that it could also be applied to more interesting domains.<br>
			<br>
			A formal grammar defines all meaningful queries and an attempt was made to make this grammar cover many cases is 
			as generic a way as possible.  Each rule in the grammar is accomponied by a function written in Lua.  If
			the rule is a terminal symbol such as "three", the function simply returns the Lua number 3.  If the rule is
			contains parameters as in "%number% days" then the value returned by the function which matched the 
			%number% part of the subquery is passed into the Lua function bound to the variable number.  In this 
			case, the return value would be some Lua Date object.  See the list of <a href="show-rules.php">rules</a>
			used in this grammar for more examples.
		</div>
		<div id="footer">
			<div id="footer-login-title">
				academic <a href="FormalGrammarasaBasis.pdf">paper</a> describing english<br>
				<br>
			</div>
		</div>
	</body>
<script>
function display_description() {
	document.getElementById('description').style.display = 'block';
}
</script>
</html>
