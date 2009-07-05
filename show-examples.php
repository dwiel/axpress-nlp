<?php
	// session can be mapped to a username after logging in ...
	// or the username can be set to anonymous
	
	$link=mysql_connect('localhost','root','badf00d');
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
					<input id="main-form-query" type="text" name="query" size=60/>
					<input id="sid" type="hidden" name="sid" value="100"/>
				</form>
			</div>
			<div id="below">
				<div id="below-title">examples:</div>
				<div class="exmaple"><a href="exec.php?query=email">email</a></div>
				<div class="exmaple"><a href="exec.php?query=new email to lucas">new email to lucas</a></div>
				<div class="exmaple"><a href="exec.php?query=emails from last week">emails from last week</a></div>
				<div class="exmaple"><a href="exec.php?query=emails about vacation">emails about vacation</a></div>
				<div class="exmaple"><a href="exec.php?query=compose">compose</a></div>
				<div class="exmaple"><a href="exec.php?query=moms email">moms email</a></div>
				<div class="exmaple"><a href="exec.php?query=show me all of my email from 3 weeks ago">show me all of my email from 3 weeks ago</a></div>
				<div class="exmaple"><a href="exec.php?query=from lucas&lastquery=email">email, then from lucas</a></div>
				<div class="exmaple"><a href="exec.php?query=from lucas&lastquery=email">email, then from lucas, then from 3 weeks ago</a></div>
				<div class="exmaple"><a href="exec.php?query=most recent 50 emails">most recent 50 emails</a></div>
				<div class="exmaple"><a href="exec.php?query=most recent fourty-nine emails">most recent fourty-nine emails</a></div>
				<div class="exmaple"><a href="exec.php?query=are there any emails from mom?">are there any emails from mom?</a></div>
				<div class="exmaple"><a href="exec.php?query=emails since last week">emails since last week</a></div>
				<div class="exmaple"><a href="exec.php?query=emails titled money">emails titled money</a></div>
				<div class="exmaple"><a href="exec.php?query=today's emails">today's emails</a></div>
			</div>
		</div>
<!--		<div id="footer">
			<div id="footer-login-title">
				<a href="login.php">login/register</a>
			</div>
-->
		</div>
	</body>
</html>
