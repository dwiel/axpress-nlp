from SimpleSPARQL.PrettyQuery import prettyquery as p

def loadTranslations(axpress, n) :
  n.bind('dt', '<http://dwiel.net/axpress/datetime/0.1/>')
  
  # NOTE: dt.time is represented by python datetime.time
  
  from datetime import time

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
  
  "5( |)pm"
  "5 oclock( this afternoon)" # this afternoon isnt a time or a datetime maybe a daterange?
  "5 tonight" # am or pm ?
  "5:00"
  d = {
    'am' : 'am',
    'morning' : 'am',
    'this morning' : 'am',
    'pm' : 'pm',
    'tonight' : 'pm',
    'evening' : 'pm',
    'this evening' : 'pm',
  }
  import string
  def input_fn(vars):
    if 'ampm' in vars and vars['ampm'] not in d :
      return False
    return all(c in string.digits+':' for c in vars['i'])

  def t_fn(vars):
    if ':' in vars['i'] :
      hour, min = vars['i'].split(':')
      hour = int(hour)
      min  = int(min)
    else :
      hour = int(vars['i'])
      min  = 0
    
    if hour > 12 or 'ampm' not in vars :
      vars['time'] = time(hour = hour, minute = min)
    else :
      if d[vars['ampm']] == 'am' :
        vars['time'] = time(hour = hour, minute = min)
      else :
        vars['time'] = time(hour = 12 + hour, minute = min)
  rule("# am/pm", """
    t[a.is] = "%i%(| oclock) %ampm%"
  """, """
    t[dt.time] = _time
  """, t_fn, input_fn)
  # NOTE: bug: 7:45pm does work with "%i%%ampm%", doing it the 'hard' way for now
  #   SEE bug in Compiler.py:230 about only returning one possible string match
  def make_ampm_fn(ampm) :
    def ampm_fn(vars) :
      vars['ampm'] = ampm
      return t_fn(vars)
    return ampm_fn
  rule("# am/pm", """
    t[a.is] = "%i%pm"
  """, """
    t[dt.time] = _time
  """, make_ampm_fn('pm'), input_fn)
  rule("# am/pm", """
    t[a.is] = "%i%am"
  """, """
    t[dt.time] = _time
  """, make_ampm_fn('am'), input_fn)
  rule("# with no am/pm", """
    t[a.is] = "%i%(| oclock)"
  """, """
    t[dt.time] = _time
  """, t_fn, input_fn)
  "17 hundred( hours)"
  rule("# am/pm", """
    t[a.is] = "%i%(| hundred)(| hours)"
  """, """
    t[dt.time] = _time
  """, t_fn, input_fn)

  # simple display
  def display_fn(vars) :
    print 'display_fn', vars
    vars['out'] = str(vars['time'])
  rule("display time", """
    d[dt.time] = _time
  """, """
    d[simple_display.text] = _out
  """, display_fn)

