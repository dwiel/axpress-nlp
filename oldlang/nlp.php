<?

session_start();
if(!isset($_SESSION['username'])) {
	$_SESSION['username'] = "temp".mt_rand();
}

// include 'header.php';
// include 'mysql.php';

$descriptorspec = array(
		0 => array("pipe", "r"),  // stdin is a pipe that the child will read from
		1 => array("pipe", "w"),  // stdout is a pipe that the child will write to
		2 => array("pipe", "w"),  // stderr is a pipe that the child will write to
);

$process = proc_open('lua english.lua', $descriptorspec, $pipes);

if(isset($_POST['query'])) {
	$query = stripslashes($_POST['query']);
} else {
	$query = stripslashes($_GET['query']);
}

if(preg_match('/http*/', $query)) {
	echo "That's what bots say.  Could you please say something else?  Thanks!";
	exit();
}

if(isset($_POST['lastquery'])) {
	$lastquery = stripslashes($_POST['lastquery']);
} else {
	$lastquery = stripslashes($_GET['lastquery']);
}

if(isset($_POST['language'])) {
	$language = stripslashes($_POST['language']);
} else {
	$language = stripslashes($_GET['language']);
}

if(!strcmp($language, '')) {
	$language = 'english';
}

if(isset($_POST['debug'])) {
	$debug = stripslashes($_POST['debug']);
} else {
	$debug = stripslashes($_GET['debug']);
}


// log the query
$link=mysql_connect('localhost','root','badf00d');
mysql_select_db('english',$link);

function report($result, $query, $lastquery) {
		$lastquery = preg_replace('/\s+/', ' ', $lastquery);
		$lastquery = preg_replace('/^\s+/', '', $lastquery);
		$lastquery = preg_replace('/\s+$/', '', $lastquery);
		
		$query = preg_replace('/\s+/', ' ', $query);
		$query = preg_replace('/^\s+/', '', $query);
		$query = preg_replace('/\s+$/', '', $query);
	
	$mysqlquery = sprintf("INSERT INTO userlog (username, query, result, lastquery) VALUES ('%s', '%s', '%s', '%s');",
		mysql_real_escape_string($_SESSION['username']),
		mysql_real_escape_string($query),
		mysql_real_escape_string($result),
		mysql_real_escape_string($lastquery));
	mysql_query($mysqlquery);
}



// echo $_POST['query'];

function isWellFormed($xmlString)
{
	libxml_use_internal_errors(true);
	
	$doc = new DOMDocument('1.0', 'utf-8');
	$doc->loadXML($xmlString);
	
	$errors = libxml_get_errors();
	if (empty($errors))
	{
		return true;
	}
	
	$error = $errors[ 0 ];
	if ($error->level < 3)
	{
		return true;
	}
	
	$lines = explode("r", $xmlString);
	$line = $lines[($error->line)-1];
	
	$message = $error->message.' at line '.$error->line.':'.htmlentities($line);
	
	return $message;
}

if (is_resource($process)) {
		// $pipes now looks like this:
		// 0 => writeable handle connected to child stdin
		// 1 => readable handle connected to child stdout
		
		$lastquery = preg_replace('/\s+/', ' ', $lastquery);
		$lastquery = preg_replace('/^\s+/', '', $lastquery);
		$lastquery = preg_replace('/\s+$/', '', $lastquery);

		fwrite($pipes[0], "<root><query><![CDATA[".$query."]]></query><lastquery>".$lastquery."</lastquery><language>".$language."</language></root>");
		if($debug) {
			echo "<xmp><root><query><![CDATA[".$query."]]></query><lastquery>".$lastquery."</lastquery><language>".$language."</language></root></xmp>";
		}
		fclose($pipes[0]);
		
		$out = stream_get_contents($pipes[1]);
		$err = stream_get_contents($pipes[2]);
		
		$out = preg_replace('/&#x0D;/', '\n', $out);
		$err = preg_replace('/&#x0D;/', '\n', $err);
		
		if ($debug) {
			echo '<xmp>'.$err.'</xmp>';
		}
		
		fclose($pipes[1]);

		// It is important that you close any pipes before calling
		// proc_close in order to avoid a deadlock
		$return_value = proc_close($process);
		
		if ($out == "") {
			// nada
		} elseif (isWellFormed($out))	{
		$xml = simplexml_load_string($out);
	}
		
	if($xml != "") {
		$SPARQLquery = $xml->result->query;
		$stylesheet = $xml->result->stylesheet;
		
		$SPARQLquery = preg_replace('/\s/', ' ', $SPARQLquery);
		if($SPARQLquery != "" and $SPARQLquery != " ") {
			report("SPARQLquery recieved", $query, $lastquery);
			// forward to a page that makes the query
			echo $SPARQLquery;
		} elseif ($forwardto = $xml->forwardto) {
			header('Location: '.$forwardto);
		} else {
			report("no comprende: $SPARQLquery", $query, $lastquery);
			echo "no comprende: $SPARQLquery";
		}
	} else {
		echo $out;
		report("echoed", $query, $lastquery);
	}
}

?>
