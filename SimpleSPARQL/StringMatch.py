import re

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

def _match(str, const) :
  """
  @arg str the string to match against
  @arg const is a list of constant substring to split the str from
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
      if not front :
        continue
      
      # we split based on the firts known constant substring, now look 
      # for the rest of the splits
      for m in _match(back,  const[1:]) :
        yield (front,) + m

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
  matches = list(_match(str, const))
  if matches :
    ms = []
    for m in matches :
      ms.append({k: v for k, v in zip(vars, m)})
    return ms
  else :
    return False

assert match("%x%o%y%", "dogod") == [
  {'x' : 'd', 'y' : 'god'},
  {'x' : 'dog', 'y' : 'd'},
]
    
assert match("%a%XY%b%YZ%c%", "abcXYdefXYghYZijYZkl") == [
  {'a' : 'abc', 'b' : 'defXYgh', 'c' : 'ijYZkl'},
  {'a' : 'abc', 'b' : 'defXYghYZij', 'c' : 'kl'},
  {'a' : 'abcXYdef', 'b' : 'gh', 'c' : 'ijYZkl'},
  {'a' : 'abcXYdef', 'b' : 'ghYZij', 'c' : 'kl'},
]
assert match("%a%XY%b%YZ%c%", "XYdefXYghYZijYZkl") == [
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

