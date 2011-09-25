<?php
    $to = $_GET['to'];
    $to = preg_replace('/mailto:/', '', $to);
?>

<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html lang="en" xmlns="http://www.w3.org/1999/xhtml" xml:lang="en">
<head>
  <title>compose email</title>
  <style>
	h1 { font-size: 150% ; }
	h2 { font-size: 125% ; }
	table { border-collapse: collapse ; border: 1px solid black ; }
	td, th
	{ border: 1px solid black ;
		padding-left:0.5em; padding-right: 0.5em; 
		padding-top:0.2ex ; padding-bottom:0.2ex 
	}
	body {
		background-color: #eee;
		margin: 0;
	}
	
  </style>
  <script language="javascript">
	function toggleDiv(divid){
		if(document.getElementById(divid).style.display == 'none'){
		document.getElementById(divid).style.display = 'block';
		}else{
		document.getElementById(divid).style.display = 'none';
		}
	}
  </script>
  <link rel="stylesheet" href="index.css"/>
</head>
<body>
  <a href="http://localhost/english/show-rules.php">rules</a>
  <form action="exec.php" method="post">
    <input type="text" id="main-form-query" name="query" size="60"/>
    <input type="hidden" id="lastquery" name="lastquery" value="compose"/>
    <input type="hidden" id="main-form-sid" name="sid" value="100"/>
  </form>
  <center><h3>compose email</h3></center>
  <a href="http://localhost/english/exec.php?query=emails">back to email</a>
  
  <center>
  <form action="submit-email.php" method="post">
    to: <input type="text" id="to" name="to" size="40" value="<?php echo $to ?>"/><br>
    subject: <input type="text" id="subject" name="subject" size="40" /><br>
    <textarea id="body" name="body" rows="30" cols="100"></textarea><br>
    <input type="submit" id="submit" name="submit" value="send" /><br>
  </form>
  </center>
  
</body>
</html>