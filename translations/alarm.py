""" alarm """

# so far, something like 4 hours

# setting
"wake me (up |up at |at |)%datetime%"
"set (an |)alarm (for |)%datetime%"

# changing
"change (my |)%datetime% alarm to %datetime%"

# silencing
"(turn off|silence) (my |)%datetime% alarm"

# delete
"(delete|remove|kill) (my |)%datetime% alarm"

# unit_time
"5 minutes"
"12 days"
"1.5 hours"
"3 days (and |)5 minutes"

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
