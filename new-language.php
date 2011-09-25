<html>
<body>
<?
require 'mysql.php';
require 'header.php';
?>

<h2>New Language:</h2>
<form action="new-language-submit.php" method="post">
Language Name: <input type="text" name="language" id="language_input" /><br>
<input type="submit" />
</form>