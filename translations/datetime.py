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
  # TODO: convert output from a.is to more specific
  # this doesn't work because of multipath join bug ... darn
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
  
  "%unix_timestamp%"
  "in %unit_time%"
  "%unit_time% ago"
  "%unit_time% from now"
