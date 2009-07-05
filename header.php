<a href="show-rules.php?language=<?php echo $language; ?>">show rules</a>|
<a href="new-rule.php?language=<?php echo $language; ?>">new rule</a>|
<a href="http://wiki.dwiel.net/NaturalLanguageParserService.Documentation">help</a>

<form method="post" action="nlp.php">
<input type="hidden" name="language" value="<?php echo $language; ?>" />
<input type="text" name="query" size=100 />
<input type="checkbox" name="debug">Debug</input>
<input type="submit" />
</form>
