""" alarm """

# so far, something like 4 hours

# setting
#"wake me (up |up at |at |)%datetime%"
#"set (an |)alarm (for |)%datetime%"

# changing
"change (my |)%datetime% alarm to %datetime%"

# silencing
"(turn off|silence) (my |)%datetime% alarm"
"(turn off|silence) all (of |)(my |)%datetime% alarm"

# delete
"(delete|remove|kill) (my |)%datetime% alarm"

# named days
"haloween"
"christmas"
"my birthday"

# vague datetime
#   for detecting when we should ask for more details
"this evening"
"tomorrow"
"this year"
"this century"
"later"
"in the future"

# later:
"set an alarm for tomorrow at 5, remind me with a phone call"
"set a phone call alarm for tomorrow at 6"
"call my phone tomorrow at 3pm"
"email me tomorrow at 4pm reminding me to call mom"
"IM me in 3 hours reminding me to go home"

from datetime import datetime

alarm_queue = []
# new thread, test if any alarms have been set, etc.
# or if on android, set alarm through native interface

def loadTranslations(axpress, n) :
  n.bind('alarm', '<http://dwiel.net/axpress/alarm/0.1/>')
  n.bind('dt', '<http://dwiel.net/axpress/datetime/0.1/>')

  def rule(name, input, output, fn=None, input_function=None, **kwargs) :
    assert isinstance(name, basestring)
    assert isinstance(input, basestring)
    assert isinstance(output, basestring)
    options = {
      n.meta.name   : name,
      n.meta.input  : input,
      n.meta.output : output,
      n.meta.function : fn,
      n.meta.input_function : input_function
    }
    options.update(kwargs)
    axpress.register_translation(options)
  
  def alarm_new(vars) :
    dt = vars['dt']
    message = vars['message']
    
    if dt > datetime.now() :
      alarm_queue.append((dt, message))
      vars['response'] = "alright, I've alarm set for %s" % str(dt)
    else :
      vars['response'] = "%s is in the past ..." % str(dt)
  
  # raw set alarm function
  rule("new alarm", """
    ret = alarm.new(when, what)
    when[dt.datetime] = _dt
    what[string.text] = _message
  """, """
    ret[string.text] = _response
  """, alarm_new)
  
  # setting alarms
  rule("basic set alarm", """
    r[axpress.is] = "set (an |)alarm (for |)%datetime%" |
                    "wake me (up |up at |at |)%datetime%"
  """, """
    r = alarm.new(when, what)
    when[axpress.is] = "%datetime%"
    what[string.text] = "bzzt ... alarm!"
  """)
