<script type="text/javascript" src="/jquery.min.js"></script>
<style type="text/css">
.logblock-body {
  padding-left: 0.25em;
  margin-left: 0.25em;
  border-left: 1px solid #ccc;
}
.logblock-title {
  background-color: #ccc;
}
#string_query {
  width: 50em;
  font-size: 18;
  padding-left: 0.3em;
  margin-left: 1em;
  margin-top: 0.5em;
  line-height: 1.5em;
}
#result {
  width: 750px;
}
.item {
  padding: 1em;
  overflow: hidden;
}
.item .side {
  height: 150px;
  margin-left: 1em;
}
.item img {
  float: left;
}
.item .title {
  font-weight: bold;
  font-size: 125%;
  padding-bottom: 0.5em;
}
ul {
  list-style-type: none;
  padding: 0px;
}
xmp {
  margin: 0;
}
</style>

<form>
<input class="simple" id="string_query" type="text" name="string_query" value="${c.string_query | n}" />
${'<textarea class="advanced" name="query" rows=10 cols=70>' + c.query + '</textarea>' | n} 
<input type="submit" id="submit" value="Send">
<a href="javascript:advanced();">advanced</a>
</form>

<div id="result">
  ${c.ret | n}
</div>

<div id="debug">
  ${c.debug_html | n}
</div>

<script>
  $(function () {
    $('.logblock-title').live('click', function() {
      $(this).next('.logblock-body').toggle();
    });
    
    $('.advanced').hide();
    $('.simple').show();
  });

  function advanced() {
    $('.advanced').toggle();
    $('.simple').toggle();
  }
</script>