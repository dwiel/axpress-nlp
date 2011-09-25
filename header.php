<link rel="stylesheet" type="text/css" href="jquery.autocomplete.css" />
<script type="text/javascript" src="jquery-1.3.2.min.js"></script>
<script type="text/javascript" src="jquery.autocomplete.js"></script>

<a href="new-language.php">new language</a>|
<a href="show-rules.php?language=<?php echo $language; ?>">show rules</a>|
<a href="new-rule.php?language=<?php echo $language; ?>">new rule</a>|
<a href="http://wiki.dwiel.net/NaturalLanguageParserService.Documentation">help</a>
<form method="get" action="">
switch to: <input type="text" name="language" id="language_input"/>
<input type="submit" />
</form>

<form method="post" action="nlp.php">
<input type="hidden" name="language" value="<?php echo $language; ?>" />
<input type="text" name="query" size=100 />
<input type="checkbox" name="debug">Debug</input>
<input type="submit" />
</form>

<script>
$(document).ready(function() {
  $("#language_input").autocomplete("language_autocomplete.php");
});
</script>