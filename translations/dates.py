from SimpleSPARQL.PrettyQuery import prettyquery as p

def loadTranslations(axpress, n) :
  n.bind('dt', '<http://dwiel.net/axpress/datetime/0.1/>')
  
  from datetime import timedelta
  
  def rule(name, input, output, fn=None, input_function=None, **kwargs) :
    options = {
      n.meta.name   : name,
      n.meta.input  : input,
      n.meta.output : output,
      n.meta.function : fn,
      n.meta.input_function : input_function
    }
    options.update(kwargs)
    axpress.register_translation(options)
  
  # for some reason this didn't work out ...
  #def dow(possibilities, day_name) :
    #rule(day_name, """
      #_[dt.day_of_week_string] = u"%s"
    #""" % possibilities, """
      #_[dt.day_of_week] = "%s"
    #""" % day_name)
  
  #dow("(monday|mon|m)", "monday")
  #dow("(tuesday|tues|tue)", "tuesday")
  #dow("(wednesday|wed|w)", "wednesday")
  #dow("(thursday|thurs|thur|th)", "thursday")
  #dow("(friday|fri|f)", "friday")
  #dow("(saturday|sat)", "saturday")
  #dow("sunday", "sunday")
  
  d = {
    "monday"    : ["monday", "mon", "m"],
    "tuesday"   : ["tuesday", 'tues', 'tue'],
    'wednesday' : ['wednesday', 'wed', 'w'],
    'thursday'  : ['thursday', 'thur', 'th'],
    'friday'    : ['friday', 'fri', 'f'],
    'saturday'  : ['saturday', 'sat'],
    'sunday'    : ['sunday', 'sun'],
  }
  rev_d = {}
  for name, shorts in d.iteritems() :
    for short in shorts :
      rev_d[short] = name
  def fn(vars) :
    vars['dow'] = rev_d[vars['dow_str']]
  def dow_string_input_function(vars) :
    return vars['dow_str'] in rev_d
  rule('day_name', """
      _[dt.day_of_week_string] = _dow_str
    """, """
      _[dt.day_of_week] = _dow
    """, fn, dow_string_input_function)
  
  dow_to_dow_i = {
    'monday'    : 0,
    'tuesday'   : 1,
    'wednesday' : 2,
    'thursday'  : 3,
    'friday'    : 4,
    'saturday'  : 5,
    'sunday'    : 6,
  }
  def dow_fn(vars) :
    vars['dowi'] = dow_to_dow_i[vars['dow']]
  rule('dow to dow i', """
    d[dt.day_of_week] = _dow
  """, """
    d[dt.day_of_week_int] = _dowi
  """, dow_fn)
  
  """
  # might be nice to write it like this: (though what I did above isn't too bad
  # for now)
  # with a macro (or is this just a function?) :
  
  def dow(in, out)
    _[dt.day_of_week_string] = in
    =>
    _[dt.day_of_week] = out
  """
  
  # TODO: :type_name syntax
  # TODO: a.is double syntax for all of these?
  # date
  def d(s, fn) :
    def new_fn(vars) :
      vars['date'] = fn(vars)
    
    # should this rule also accept a.is strings?  it will get quite poluted ...
    rule(s, """
      d[dt.date_string] = "%s"
    """ % s, """
      d[dt.date] = _date
    """, new_fn)
    
    rule(s +' a', """
      d[a.is] = "%s"
    """ % s, """
      d[dt.date] = _date
    """, new_fn)
  
  from datetime import date
  d("today", lambda x : date.today())
  d("tomorrow", lambda x : date.today() + timedelta(days = 1))
  d("yesterday", lambda x : date.today() - timedelta(days = 1))
  
  # "this wednesday", "friday"
  # Q: if today is wednesday, does "tuesday" mean yesterday or next tuesday?
  # A: this tuesday for now
  def this_day_of_week(vars) :
    print 'this_day_of_week', vars
    dow_i = vars['dow_i']
    
    d = date.today()
    dow_i_today = d.weekday()
    
    print dow_i_today, dow_i
    if dow_i > dow_i_today :
      vars['date'] = date.today() + timedelta(days = dow_i - dow_i_today)
    elif dow_i == dow_i_today :
      vars['date'] = date.today()
    else :
      vars['date'] = date.today() + timedelta(days = 7 - dow_i_today + dow_i)
  rule("this dow str - naked", """
    this_dow[a.is] = "%dow_str%"
  """, """
    dow[dt.day_of_week_string] = "%dow_str%"
    dow[dt.this_day_of_week] = this_dow
  """)
  rule("this dow str - this", """
    this_dow[a.is] = "this %dow_str%"
  """, """
    dow[dt.day_of_week_string] = "%dow_str%"
    dow[dt.this_day_of_week] = this_dow
  """)
  rule("this dow", """
    dow[dt.day_of_week_int] = _dow_i
  """, """
    dow[dt.this_day_of_week] = d
    d[dt.date] = _date
  """, this_day_of_week)
  
  # next thursday
  def next_day_of_week(vars) :
    print 'next_day_of_week', vars
    dow_i = vars['dow_i']
    
    d = date.today()
    dow_i_today = d.weekday()
    
    print dow_i_today, dow_i
    if dow_i > dow_i_today :
      vars['date'] = date.today() + timedelta(days = dow_i - dow_i_today)
    elif dow_i == dow_i_today :
      vars['date'] = date.today() + timedelta(days = 7)
    else :
      vars['date'] = date.today() + timedelta(days = 7 - dow_i_today + dow_i)
  rule("next dow str", """
    next_dow[a.is] = "next %dow_str%"
  """, """
    dow[dt.day_of_week_string] = "%dow_str%"
    dow[dt.next_day_of_week] = next_dow
  """)
  rule("next dow", """
    dow[dt.day_of_week_int] = _dow_i
  """, """
    dow[dt.next_day_of_week] = d
    d[dt.date] = _date
  """, next_day_of_week)
  
  def last_day_of_week(dow_i) :
    d = date.today()
    dow_i_today = d.weekday()
    
    if dow_i > dow_i_today :
      return date.today() - timedelta(days = dow_i - dow_i_today)
    elif dow_i == dow_i_today :
      return date.today() - timedelta(days = 7)
    else :
      # TODO: double check this part
      return date.today() - timedelta(days = 7 - dow_i_today + dow_i)
  rule("last dow str", """
    last_dow[a.is] = "last %dow_str%"
  """, """
    dow[dt.day_of_week_string] = "%dow_str%"
    dow[dt.last_day_of_week] = last_dow
  """)
  rule("last dow", """
    dow[dt.day_of_week_int] = _dow_i
  """, """
    dow[dt.last_day_of_week] = d
    d[dt.date] = _date
  """, last_day_of_week)
  
  d("day after %date%", lambda vars : vars['date'] + timedelta(days = 1))
  d("day before %date%", lambda vars : vars['date'] - timedelta(days = 1))
  
  # TODO
  "%:dt.unit_time_in_days% before/after %:dt.date%"
  "last %:dt.day_of_week% of the month"
  "last %:dt.day_of_week% of the year"
  "3rd %:dt.day_of_week% of %month%"
  "%:dt.year% %:dt.month% %:dt.day%"
  "%:dt.month_name% %:dt.day_of_month% %:dt.year [default:this year]%"
  
  rule('a.is day_of_week_string', """
    x[a.is] = s
  """, """
    x[dt.day_of_week_string] = s
  """)
  
  rule('day of prayer', """
    d[a.is] = "day of prayer"
  """, """
    d[dt.day_of_week] = "sunday"
  """)
  
  rule('day of week is this week', """
    d[dt.day_of_week] = _dow
  """, """
    d[dt.this_day_of_week] = d
  """)
  
  # simple display
  def fn(vars) :
    print 'fn', vars
    vars['out'] = str(vars['date'])
  rule("display date", """
    d[dt.date] = _date
  """, """
    d[simple_display.text] = _out
  """, fn)

  # simple display
  rule("display date", """
    d[dt.day_of_week] = _out
  """, """
    d[simple_display.text] = _out
  """)


  ## a few naked strings just for testing slowdowns
  ## 10 - 0.35 s -> 0.8 s
  ## 20 - 0.35 s -> 1.25 s
  ## also, this is without any new branches explored due to new information
  #for x in range(20) :
    #rule("%d str - naked" % x, """
      #x[a.is] = "%x_str%"
    #""", """
      #m[dt.x_string] = "%x_str%"
      #m[dt.x] = x
    #""")

def test() :
  pass
