<?

session_start();
if(!isset($_SESSION['username'])) {
	$_SESSION['username'] = "temp".mt_rand();
}

// include 'header.php';
// include 'mysql.php';

$descriptorspec = array(
		0 => array("pipe", "r"),  // stdin is a pipe that the child will read from
		1 => array("pipe", "w")   // stdout is a pipe that the child will write to
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

//    echo $_POST['query'];
		fwrite($pipes[0], "<root><query><![CDATA[".$query."]]></query><lastquery>".$lastquery."</lastquery></root>");
//    echo "<xmp><root><query><![CDATA[".$query."]]></query><lastquery>".$lastquery."</lastquery></root></xmp>";
		fclose($pipes[0]);
		
		$out = stream_get_contents($pipes[1]);
		
		//echo "<root><query><![CDATA[".$_POST['query']."]]></query><lastquery>".$lastquery."</lastquery></root>";
		
//    $out = preg_replace('/\n/', '<br>', $out);
//    $out = preg_replace('/\n/', '%0D%0A', $out);
//    $out = preg_replace('/ /', '+', $out);
//    $out = preg_replace('/:/', '%3A', $out);
//    $out = preg_replace('/</', '%3C', $out);
//    $out = preg_replace('/\//', '%2F', $out);
//    $out = preg_replace('/>/', '%3E', $out);
			$out = preg_replace('/&#x0D;/', '\n', $out);
		
//    echo $out;
		
		fclose($pipes[1]);

		// It is important that you close any pipes before calling
		// proc_close in order to avoid a deadlock
		$return_value = proc_close($process);
		
//    echo $out;
//    return;
		if ($out == "") {
				echo "Thank you, I hadn't thought of that.<br>";
				echo "<xmp><root><query><![CDATA[".$query."]]></query><lastquery>".$lastquery."</lastquery></root></xmp>";
				echo $_POST["lastquery"].'<br>';
				echo $_GET["lastquery"].'<br>';
				report("empty string from lua", $query, $lastquery);
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
			//$url = "http://localhost:2020/query?query=".urlencode($SPARQLquery)."&stylesheet=/english/xml-to-html.xsl";
			$url = "http://localhost:2020/query?query=".urlencode($SPARQLquery)."&stylesheet=".urlencode($stylesheet);
			// echo $url;
			$handle = fopen($url, "rb");
			$result = stream_get_contents($handle);
			fclose($handle);
			
			header("Content-type: text/xml");
			
			$result = preg_replace('/<\/sparql>/', '', $result);
			echo $result;
			echo "  <pastqueries>\n";
			// $queryout = htmlspecialchars($out);
			// $queryout = $_POST['query'];
			$queryout = $xml->lastquery;
			echo "    <query>\n";
			echo "      $queryout\n";
			echo "    </query>\n";
			echo "    <fullquery>\n";
			echo "      $queryout\n";
			echo "    </fullquery>\n";
			echo "  </pastqueries>\n";
			echo "  <sparqlquery>\n";
			echo "    <![CDATA[\n$SPARQLquery\n]]>";
			echo "  </sparqlquery>\n";
			echo "</sparql>";
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
