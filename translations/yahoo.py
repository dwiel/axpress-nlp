def loadTranslations(axpress) :
  axpress.n.bind('yahoo', '<http://dwiel.net/axpress/yahoo/0.1/>')

  # http://lethain.com/entry/2008/jul/11/search-recipes-for-yahoo-s-boss-in-python/
  # yahoo search bindings
  def yahoo_search(vars):
    from yos.boss import ysearch
    from yos.yql import db
    data = ysearch.search(vars['query'],count=10)
    table = db.create(data=data)
    return table.rows

  axpress.register_translation({
    'name' : '',
    'input' : """
      search[yahoo.query] = _query
    """,
    'output' : """
      search[yahoo.dispurl] = _dispurl
      search[yahoo.title] = _title
      search[yahoo.url] = _url
      search[yahoo.abstract] = _abstract
      search[yahoo.clickurl] = _clickurl
      search[yahoo.date] = _date
      search[yahoo.size] = _size
    """,
    'function' : yahoo_search,
  })
  
