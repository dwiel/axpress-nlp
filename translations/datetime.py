from SimpleSPARQL.PrettyQuery import prettyquery as p

# TODO:
"%unix_timestamp%"
"%minutes% till %hour%"

def loadTranslations(axpress) :
  axpress.n.bind('dt', '<http://dwiel.net/axpress/datetime/0.1/>')
  
  # NOTE: dt.time is represented by python timedelta from midnight, no date information is present
  
  import datetime

  def rule(name, input, output, fn=None, input_function=None, **kwargs) :
    options = {
      'name'   : name,
      'input'  : input,
      'output' : output,
      'function' : fn,
      'input_function' : input_function
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

  def fn(vars) :
    vars['text'] = str(vars['td'])
  rule("display timedelta", """
    foo[dt.timedelta] = _td
  """, """
    foo[simple_display.text] = _text
  """, fn)

  # NOTE: this should be writable in many fewer lines:
  """
  x[a.is] = "%dt.timedelta% from now" | "in %dt.timedelta%"
    =>
  x[dt.datetime] = _dt
    fn
  return datetime.datetime.now() + timedelta
  """
  
  def make_is_number(name) :
    """ makes an input_function which tests in name is a valid number
    note: name can be a name of a varialbe or a list of names
    """
    if isinstance(name, basestring) :
      def is_number(vars) :
        try :
          float(vars[name])
          return True
        except ValueError:
          return False
      return is_number
    else :
      # more than one name to test
      names = name
      def is_number(vars) :
        try :
          p('n', names)
          map(lambda name:float(vars[name]), names)
          return True
        except ValueError:
          return False
      return is_number
    
  # in 10 hours
  rule("from now a", """
    x[axpress.is] = "%timedelta% (from now|into the future|in the future)" | "in %timedelta%"
  """, """
    x[dt.timedelta_from_now][axpress.is] = "%timedelta%"
  """)
  def from_now(vars) :
    vars['dt'] = datetime.datetime.now() + vars['td']
  rule("from now", """
    x[dt.timedelta_from_now][dt.timedelta] = _td
  """, """
    x[dt.datetime] = _dt
  """, from_now)
  
  # 5 minutes ago
  rule("timedelta ago a", """
    x[axpress.is] = "%timedelta% (ago|in the past)"
  """, """
    x[dt.timedelta_ago][axpress.is] = "%timedelta%"
  """)
  def ago(vars) :
    vars['dt'] = datetime.datetime.now() - vars['td']
  rule("timedelta ago", """
    x[dt.timedelta_ago][dt.timedelta] = _td
  """, """
    x[dt.datetime] = _dt
  """, ago)

  ############# timedelta
  "5 minutes"
  "12 days"
  "1.5 hours"
  def make_timedelta(name, matches) :
    def timedelta_fn(vars) :
      vars['td'] = datetime.timedelta(**{name : float(vars['number'])})
    rule("x %s" % name, """
      x[axpress.is] = "%number%( |)xxx"
    """.replace('xxx', matches), """
      x[dt.timedelta] = _td
    """,
    timedelta_fn,
    input_function = make_is_number('number'))
  
  # TODO: more complete, see http://en.wikipedia.org/wiki/Unit_of_time
  make_timedelta('microseconds', '(microsec|microsecs|microsecond|microseconds)')
  make_timedelta('milliseconds', '(ms|millisec|millisecs|millisecond|milliseconds)')
  make_timedelta('seconds',      '(s|sec|second|seconds)')
  make_timedelta('minutes',      '(m|min|mins|minute|minutes)')
  make_timedelta('hours',        '(h|hr|hrs|hour|hours)')
  make_timedelta('days',         '(d|day|days)')
  make_timedelta('weeks',        '(w|wk|week|weeks)')
  make_timedelta('months',       '(m|month|months)')
  make_timedelta('years',        '(y|yr|year|years)')
  make_timedelta('decades',      '(decade|decades)')
  
  # timdelta summing
  "3 days (and |)5 minutes"
  def add_timedeltas(vars) :
    vars['td_out'] = vars['td1'] + vars['td2']
  # NOTE: allowing 3 days 5 mins explodes search ...
  rule('add timedeltas a', """
    td_out[axpress.is] = "%td1_str%( |)(and|\+|,)( |)%td2_str%"
  """, """
    td1[axpress.is] = "%td1_str%"
    td2[axpress.is] = "%td2_str%"
    td_out = dt.add_timedeltas(td1, td2)
  """)
  rule('add timedeltas', """
    t1[dt.timedelta] = _td1
    t2[dt.timedelta] = _td2
    t_out = dt.add_timedeltas(t1, t2)
  """, """
    t_out[dt.timedelta] = _td_out
  """, add_timedeltas)
  