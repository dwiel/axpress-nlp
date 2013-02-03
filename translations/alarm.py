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

# display
"(show (me |)(all (of |)|)(my |)alarms"
"(show (me |)(all (of |)|)(my |)alarms %datetime_range%"

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
"email me tomorrow at 4pm reminding me to call mom"
"IM me in 3 hours reminding me to go home"

# phone calls are too expensive for now ...
"set an alarm for tomorrow at 5, remind me with a phone call"
"set a phone call alarm for tomorrow at 6"
"call my phone tomorrow at 3pm"

from datetime import datetime

# new thread, test if any alarms have been set, etc.
# or if on android, set alarm through native interface

def loadTranslations(axpress) :
  axpress.n.bind('alarm', '<http://dwiel.net/axpress/alarm/0.1/>')
  axpress.n.bind('dt', '<http://dwiel.net/axpress/datetime/0.1/>')
  rule = axpress.rule

  def alarm_new(vars) :
    import pymongo
    alarm_queue = pymongo.Connection().axpress.alarm_queue
    
    dt = vars['dt']
    message = vars['message']
    alarm = {'datetime' : dt, 'message' : message}
    
    if alarm_queue.find(alarm).count() :
      vars['response'] = "You already have an alarm set for %s" % str(dt)
    elif dt > datetime.now() :
      alarm_queue.insert(alarm)
      vars['response'] = "alright, I've set an alarm for %s" % str(dt)
    else :
      vars['response'] = "sorry, no alarm was set since %s is in the past." % str(dt)
  
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

  # setting alarms
  rule("set alarm with message", """
    r[axpress.is] = "remind me to %message% (at |)%datetime%"
  """, """
    r = alarm.new(when, what)
    when[axpress.is] = "%datetime%"
    what[string.text] = "%message%"
  """)

  def alarm_kill_all(vars) :
    import pymongo
    alarm_queue = pymongo.Connection().axpress.alarm_queue
    
    num_alarms = alarm_queue.count()
    alarm_queue.remove()
    vars['response'] = "removed all (%d) of your alarms" % num_alarms
  rule("kill all alarms", """
    a[axpress.is] = "(kill|del|delete|rm|remove)( all|) alarm(s|)"
  """, """
    a[string.text] = _response
  """, alarm_kill_all)
  
  def alarm_count(vars) :
    import pymongo
    alarm_queue = pymongo.Connection().axpress.alarm_queue
    
    num_alarms = alarm_queue.count()
    if num_alarms == 0 :
      num_alarms = 'no alarms'
    elif num_alarms == 1 :
      num_alarms = '1 alarm'
    else :
      num_alarms = '%d alarm' % num_alarms
    vars['response'] = "you have %s" % num_alarms    
  rule("count alarms", """
    a[axpress.is] = "(alarm count|how many alarms( do I have|)|count alarms)"
  """, """
    a[string.text] = _response
  """, alarm_count)
  
