from SimpleSPARQL.PrettyQuery import prettyquery as p

def loadTranslations(axpress, n) :
  n.bind('dt', '<http://dwiel.net/axpress/datetime/0.1/>')
  
  # NOTE: dt.time is represented by python timedelta from midnight, no date information is present
  
  import datetime

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
  
  "%time% (on |in |)%date%"
  "%date% at %time%"
  rule("time on date", """
    dt[a.is] = "%time_s% (on |in |)%date_s%"
  """, """
    d[a.is] = "%date_s%"
    d[dt.date] = date
    t[a.is] = "%time_s%"
    t[dt.time] = time
    dt[dt.datetime] = dt.compose(date, time)
  """)
  rule("date at time", """
    dt[a.is] = "%date_s% at %time_s%"
  """, """
    d[a.is] = "%date_s%"
    d[dt.date] = date
    t[a.is] = "%time_s%"
    t[dt.time] = time
    dt[dt.datetime] = dt.compose(date, time)
  """)
  def fn(vars) :
    vars['datetime'] = datetime.datetime.combine(vars['date'], vars['time'])
  rule("date+time", """
    d[dt.date] = _date
    t[dt.time] = _time
  """, """
    dt.compose(date, time) = _datetime
  """, fn)
  
  def fn(vars) :
    vars['text'] = str(vars['dt'])
  rule("display datetime", """
    foo[dt.datetime] = _dt
  """, """
    foo[simple_display.text] = _text
  """, fn)
  
  # NOTE: this should be writable in many fewer lines:
  """
  x[a.is] = "%dt.unit_time% from now" | "in %dt.unit_time%"
    =>
  x[dt.datetime] = _dt
    fn
  return datetime.datetime.now() + unit_time
  """

  rule("from now a", """
    x[axpress.is] = "%unit_time% from now" | "in %unit_time%"
  """, """
    x[dt.unit_time_from_now][axpress.is] = "%unit_time%"
  """)
  def from_now(vars) :
    vars['dt'] = datetime.datetime.now() + vars['ut']
  rule("from now", """
    x[dt.unit_time_from_now][dt.unit_time] = _ut
  """, """
    x[dt.datetime] = _dt
  """, from_now)
  
  ############# unit time
  "5 minutes"
  "12 days"
  "1.5 hours"
  "3 days (and |)5 minutes"
  def unit_time_min(vars) :
    vars['ut'] = timedelta(minutes = vars['number'])
  rule("x minutes", """
    x[axpress.is] = "%number% (min|mins|minute|minutes)"
  """, """
    x[dt.unit_time] = _ut
  """, unit_time_min)
  

  "%unix_timestamp%"
  "%unit_time% ago"
  "%minutes% till %hour%"
  