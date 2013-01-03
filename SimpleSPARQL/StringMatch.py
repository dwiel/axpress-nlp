import re
import json

"""
Why I'm not using regexp 'natively':
http://stackoverflow.com/questions/4091634/finding-all-matches-with-a-regular-expression-greedy-and-non-greedy
"""

split_re = re.compile('%[\w\.:_]+%')
def split_string(s) :
  """
  given a string, split it into two lists:
    the constant parts and the variables.  Here is an example:
    
  split_string("abcd %xyz% efg") => (
    ["abcd ", " efg"], ['xyz']
  )
  """
  return (
    split_re.split(s),
    [p[1:-1] for p in split_re.findall(s)]
  )

def _match(str, const, allow_first_empty) :
  """
  @arg str the string to match against
  @arg const is a list of constant substring to split the str from
  @arg allow_first_empty should be true when the first const is right up 
       against the start, allowing the first 'empty' variable match to be 
       empty and ignored.
  @return generate tuples of substrings from str that fit between the consts
  Note that this function is recursive and recurs by findings all substring 
    that come before const[0] and then recuring on the rest of the string
    with that const removed from the list
    
  """
  if not const :
    # see below.  no empty string matches allowed, even at the end of a string
    if str :
      yield (str,)
  else :
    c = const[0] 
    # find all cases of c in str
    for x in re.finditer(c, str) :
      # front is the string that comes before c
      front = str[:x.start()]
      # back is the string that comes after c
      back  = str[x.end():]
      
      # if the c string was found right at the front of the string, then
      # front will be empty and we don't want to bind a var to an empty
      # string
      if not front and not allow_first_empty :
        continue
      
      # we split based on the first known constant substring, now look 
      # for the rest of the splits
      for m in _match(back, const[1:], False) :
        if front :
          yield (front,) + m
        else :
          yield m

def match(pat, str) :
  """
  @returns a list of bindings.  The bindings are tuples which match
    the order of the variables as they occur in the pattern.
    If there are no matches, the return value is False
    If the pattern matches, but there are no variables, [] is returned
  """
  const, vars = split_string(pat)

  # if a var is right at the begenning or end of the string, then there
  # isn't an empty const string before or after it.  To achieve this,
  # remove empty string const values at the end of begenning of the list
  if const[0] == '' :
    const = const[1:]
    allow_first_empty = False
  else :
    allow_first_empty = True
  if const[-1] == '' :
    const = const[:-1]

  # if there are no variables in the pattern, just do a normal string
  # comparison
  if not vars :
    if pat == str :
      return []
    else :
      return False
  
  # if there were some matches return them, if there were no matches
  # return False
  matches = list(_match(str, const, allow_first_empty))
  if matches :
    ms = []
    for m in matches :
      ms.append({k: v for k, v in zip(vars, m)})
    return ms
  else :
    return False

if __name__ == '__main__' :
  ret = match("%x%o%y%", "dogod")
  #print ret
  assert ret == [
    {'x' : 'd', 'y' : 'god'},
    {'x' : 'dog', 'y' : 'd'},
  ]
      
  assert match("%a%XY%b%YZ%c%", "abcXYdefXYghYZijYZkl") == [
    {'a' : 'abc', 'b' : 'defXYgh', 'c' : 'ijYZkl'},
    {'a' : 'abc', 'b' : 'defXYghYZij', 'c' : 'kl'},
    {'a' : 'abcXYdef', 'b' : 'gh', 'c' : 'ijYZkl'},
    {'a' : 'abcXYdef', 'b' : 'ghYZij', 'c' : 'kl'},
  ]
  ret = match("%a%XY%b%YZ%c%", "XYdefXYghYZijYZkl")
  #print 'ret', json.dumps(ret, indent=4)
  assert ret == [
    {'a' : 'XYdef', 'b' : 'gh', 'c' : 'ijYZkl'},
    {'a' : 'XYdef', 'b' : 'ghYZij', 'c' : 'kl'},
  ]
  assert match("%a%%b%", "abc") == [
    {'a' : 'a', 'b' : 'bc'},
    {'a' : 'ab', 'b' : 'c'},
  ]
  assert match('abc', 'abc') == []
  assert match('abcdef', 'abc') == False
  assert match("%x%o%y%", "digid") == False
  assert match('%x%', 'abc') == [{'x' : 'abc'}]

  # the constant part of a pattern can be arbitrary regexp:
  assert match("%time_s% (on |in |)%date_s%", "5 on friday") == [
    {'time_s' : '5', 'date_s' : 'friday'},
  ]
  assert match("%time_s% (on |in |)%date_s%", "5 friday") == [
    {'time_s' : '5', 'date_s' : 'friday'},
  ]

  ret = match("x %a%", "x y z")
  #print ret
  assert ret == [
    {'a' : 'y z'},
  ]

  assert match("x %a% %b%", "x y z w") == [
    {'a' : 'y', 'b' : 'z w'},
    {'a' : 'y z', 'b' : 'w'},
  ]

  assert match("remind me to %msg% %dt%", "remind me to go to keleinforfers tomorrow at 5 pm") == [
    {'msg': 'go', 'dt': 'to keleinforfers tomorrow at 5 pm'},
    {'msg': 'go to', 'dt': 'keleinforfers tomorrow at 5 pm'},
    {'msg': 'go to keleinforfers', 'dt': 'tomorrow at 5 pm'},
    {'msg': 'go to keleinforfers tomorrow', 'dt': 'at 5 pm'},
    {'msg': 'go to keleinforfers tomorrow at', 'dt': '5 pm'},
    {'msg': 'go to keleinforfers tomorrow at 5', 'dt': 'pm'}
  ]
  
  ret = match("remind me to %msg% (at |)%dt%", "remind me to go to keleinforfers tomorrow at 5 pm")
  #print 'ret', json.dumps(ret, indent=4)
  assert ret == [
    {'msg': 'go', 'dt': 'to keleinforfers tomorrow at 5 pm'},
    {'msg': 'go to', 'dt': 'keleinforfers tomorrow at 5 pm'},
    {'msg': 'go to keleinforfers', 'dt': 'tomorrow at 5 pm'},
    {'msg': 'go to keleinforfers tomorrow', 'dt': '5 pm'},
    {'msg': 'go to keleinforfers tomorrow at 5', 'dt': 'pm'}
  ]
