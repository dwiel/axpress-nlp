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
    if not str :
      raise "str should never be empty, see 'if back == '' :' below"
    
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
      
      # if the string is finished
      if back == '' :
        # its only ok for back to be empty if this pattern ends in a const
        if len(const) == 1 and const[0] and const[0][-1] == '$' :
          yield (front,)
        else :
          pass
      else :
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
  pat = '^'+pat+'$'
  const, vars = split_string(pat)

  # if a var is right at the begenning or end of the string, then there
  # isn't an empty const string before or after it.  To achieve this,
  # remove empty string const values at the end of begenning of the list
  if const[0] == '' or const[0] == '^' :
    const = const[1:]
    allow_first_empty = False
  else :
    allow_first_empty = True
  if const[-1] == '' or const[-1] == '$':
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
