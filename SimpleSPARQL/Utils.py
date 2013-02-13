# -*- coding: utf-8 -*-
from Namespaces import Namespaces
from Triple import Triple

from URIRef import URIRef

import time, copy

n = Namespaces()
n.bind('bnode', '<http://dwiel.net/axpress/bnode/0.1/>')

class VarType(type):
  def __getattr__(cls, name) :
    return cls(name)

class Variable(object) :
  # this allows Variable.image, etc
  __metaclass__ = VarType
  
  def __init__(self, name) :
    self.name = name
  
  def __eq__(self, other) :
    if isinstance(other, Variable) :
      return self.name == other.name
    else :
      return False
  
  def __ne__(self, other) :
    if isinstance(other, Variable) :
      return self.name != other.name
    else :
      return True
  
  def __str__(self) :
    return self.__class__.__name__ + '.' + self.name
  
  __repr__ = __str__

class Var(Variable) : pass
class MetaVar(Variable) : pass
class LitVar(Variable) : pass
class OutVar(Variable) : pass
class OutLitVar(Variable) : pass

#str_n_var = str(n.var)
#str_'var' = str('var')
#str_n_lit_var = str(n.lit_var)
#str_n_out_var = str(n.out_var)
#str_n_out_lit_var = str(n.out_lit_var)

#len_n_var = len(n.var)
#len_'var' = len('var')
#len_n_lit_var = len(n.lit_var)
#len_n_out_var = len(n.out_var)
#len_n_out_lit_var = len(n.out_lit_var)

def is_any_var(data) :
  return isinstance(data, Variable)
  #if type(data) == URIRef :
    #if data.find(str_n_var) == 0 :
      #return True
    #elif data.find(str_'var') == 0 :
      #return True
    #elif data.find(str_n_lit_var) == 0 :
      #return True
    #elif data.find(str_n_out_var) == 0 :
      #return True
    #elif data.find(str_n_out_lit_var) == 0 :
      #return True
  #return False

def is_var(data) :
  return isinstance(data, Var)
  #if type(data) == URIRef :
    #if data.find(str_n_var) == 0 :
      #return True
  #return False

def is_meta_var(data) :
  return isinstance(data, MetaVar)
  #if type(data) == URIRef :
    #if data.find(str_'var') == 0 :
      #return True
  #return False

def is_lit_var(data) :
  return isinstance(data, LitVar)
  #if type(data) == URIRef :
    #if data.find(str_n_lit_var) == 0 :
      #return True
  #return False  

def is_out_var(data) :
  return isinstance(data, OutVar)
  #if type(data) == URIRef :
    #if data.find(str_n_out_var) == 0 :
      #return True
  #return False

def is_out_lit_var(data) :
  return isinstance(data, OutLitVar)
  #if type(data) == URIRef :
    #if data.find(str_n_out_lit_var) == 0 :
      #return True
  #return False

def var_name(v) :
  return v.name
  #if uri.find(str_n_var) == 0 :
    #return uri[len_n_var:]
  #elif uri.find(str_'var') == 0 :
    #return uri[len_'var':]
  #elif uri.find(str_n_lit_var) == 0 :
    #return uri[len_n_lit_var:]
  #elif uri.find(str_n_out_var) == 0 :
    #return uri[len_n_out_var:]
  #elif uri.find(str_n_out_lit_var) == 0 :
    #return uri[len_n_out_lit_var:]
  #else :
    #raise Exception('data is not a variable' % str(uri))

def var_type(v) :
  assert is_any_var(v)
  # NOTE: might want to change this to a bunch of ifs and isinstances
  return type(var_type)
  
  #if uri.find(n.var) == 0 :
    #return n.var
  #elif uri.find('var') == 0 :
    #return 'var'
  #elif uri.find(n.lit_var) == 0 :
    #return n.lit_var
  #elif uri.find(n.out_var) == 0 :
    #return n.out_var
  #elif uri.find(n.out_lit_var) == 0 :
    #return n.out_lit_var
  #else :
    #raise Exception('data is not a variable' % str(uri))

def var_type_name(t) :
  if type(t) != type :
    t = type(t)
  
  return t.__name__

def var(data) :
  raise Exception("this is depricated?  how is it used?")
  #if is_any_var(data) :
    #return data[len_n_var:]
  #return None

def isstr(v) :
  return isinstance(v, basestring) and not isinstance(v, URIRef)

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
  #pat = '%[\w_]+%'
  return (
    split_re.split(s),
    [p[1:-1] for p in split_re.findall(s)]
  )

from itertools import izip_longest
def merge_string(const, vars) :
  """ merge_string operates oposite of split_string """
  def interleave(const, vars) :
    for c, v in izip_longest(const, vars, fillvalue='') :
      yield c
      yield v
  
  try :
    return ''.join(interleave(const, vars))
  except TypeError, e :
    if 'expected string, LitVar found' in str(e) :
      raise Exception("cant currently use litvars from input in string formating of output, use a custom function for now")
    else :
      raise

def sub_bindings_value(value, bindings) :
  """
  @returns new value and weather or not it was changed by the binding
  """
  if is_any_var(value) and value.name in bindings :
    return bindings[value.name]
  elif isstr(value) :
    # substitute bindings into string
    const, vars = split_string(value)
    vals = [bindings.get(var, '%'+var+'%') for var in vars]
    return merge_string(const, vals)
  return value
  
def sub_bindings_triple(triple, bindings) :
  return [sub_bindings_value(value, bindings) for value in triple]

def sub_bindings_triple_track_changes(triple, bindings) :
  new_values = []
  changed = False
  for value in triple :
    new_value = sub_bindings_value(value, bindings)
    new_values.append(new_value)
    changed = changed or (value != new_value)
  return new_values, changed

def sub_var_bindings(triples, bindings) :
  return [Triple(sub_bindings_triple(triple, bindings)) for triple in triples]

def sub_var_bindings_track_changes(triples, bindings) :
  """ works the same as sub_var_bindings except it return both the new set
  of triples as well as a set of only the triples which were changed.  See
  new_triples in compile.  This is used to know which triples changed and only
  look for new matches using new information."""
  new_triples = []
  changed_triples = []
  for triple in triples :
    new_triple, changed = sub_bindings_triple_track_changes(triple, bindings)
    
    new_triple = Triple(new_triple)
    
    if changed :
      changed_triples.append(new_triple)
    new_triples.append(new_triple)
  
  return new_triples, changed_triples

def sub_var_bindings_set(triples, bindings_set) :
  """
  Substitutes each of the bindings into the set of triples.
  @arg triples is the set of triples to substitute the bindings into
  @arg bindings_set is the set of bindings to substitute into the triples
  @return a generator of triple_sets with bindings substituted in.
  """
  
  #print 'triples',prettyquery(triples)
  #print 'bindings',prettyquery(bindings_set)
  
  for bindings in bindings_set :
    yield sub_var_bindings(triples, bindings)

def explode_binding(bindings) :
  list_of_new_bindings = [{}]
  for var, value in bindings.iteritems() :
    # NOTE: this is where we should change it to look for some
    # specific subclass of list rather than list so that we can also
    # have list values if we want
    if type(value) == list :
      # each value in the list of values is a new set of bindings
      new_list_of_new_bindings = []
      for v in value :
        for new_bindings in list_of_new_bindings :
          tmp_new_bindings = copy.copy(new_bindings)
          tmp_new_bindings[var] = v
          new_list_of_new_bindings.append(tmp_new_bindings)
      list_of_new_bindings = new_list_of_new_bindings
    # NOTE: figure out/document what this means exactly ... perhaps
    # make it a subclass of list instead
    elif type(value) == tuple :
      # each value in the tuple of values is simultaneous
      for new_bindings in list_of_new_bindings :
        # TODO: this is like the explode from before ... need a Bindings class
        # if there are to actually be mutliple values for each variable/key
        new_bindings[var] = value
    else :
      for new_bindings in list_of_new_bindings :
        new_bindings[var] = value
  return list_of_new_bindings

def explode_bindings_set(bindings_set) :
  if isinstance(bindings_set, dict) :
    bindings_set = [bindings_set]
  
  # explode the bindings_set which have multiple values into multiple
  # bindings
  new_bindings_set = []
  for bindings in bindings_set :
    #print 'bindings',prettyquery(bindings)
    new_bindings_set.extend(explode_binding(bindings))
  
  return new_bindings_set
  
def find_vars(query, is_a_var = is_any_var, find_string_vars = False) :
  """
  given a query, find the set of names of all vars, meta_vars and lit_vars
  """
  try :
    iter = query.__iter__()
    
    vars = set()
    for i in iter :
      vars.update(find_vars(i, is_a_var, find_string_vars))
    return vars
  except AttributeError :
    if is_a_var(query) :
      return set([query.name])
    elif find_string_vars and isstr(query) :
      if '%' in query :
        const, vars = split_string(query)
        return set(unicode(v) for v in vars)
      else :
        return set()
    else :
      return set()

def remove_duplicate_triples(triples) :
  """ return a new list of triples with duplicates removed """
  new_triples = []
  for triple in triples :
    if triple not in new_triples :
      new_triples.append(triple)
  return new_triples


class UniqueURIGenerator() :
  """
  usage:
  > urigen = UniqueURIGenerator(rdflib.Namespace("http://example.org/"), "bnode")
  > urigen()
  http://example.org/bnode848538945729345892349857
  """
  
  def __init__(self, namespace = n.bnode, prefix = 'bnode') :
    self.namespace = namespace
    self.prefix = prefix
    self.i = 0
  
  def __call__(self, namespace = None, prefix = None) :
    if namespace == None :
      namespace = self.namespace
    if prefix == None :
      prefix = self.prefix
    
    # incase multiple calls happen in the same time.time()
    self.i += 1
    
    postfix = str(time.time()).replace('.','')
    return namespace[prefix+postfix+str(self.i)]
  



import string

# Load dictionary of entities (HTML 2.0 only...)
#from htmlentitydefs import entitydefs
# Here you could easily add more entities if needed...
entitydefs = {
  'gt' : '>',
  'lt' : '<',
}

def html_encode(s):
  s = string.replace(s,"&","&amp;")  # replace "&" first
  
  #runs one replace for each entity except "&"
  for (ent,char) in entitydefs.items():
    if char != "&": 
      s = string.replace(s,char,"&"+ent+";")
  return s

spaces = ''

def p(*args) :
  from PrettyQuery import prettyquery
  print '%s%s' % (spaces, ' '.join([prettyquery(arg) for arg in args]))

def debug(name, obj=None) :
  from PrettyQuery import prettyquery
  name = name.replace(' ','_')
  print '%s<%s>%s</%s>' % (spaces, name, html_encode(prettyquery(obj)), name)

def logger(f, name=None):
  if name is None:
    name = f.func_name
  def wrapped(*args, **kwargs):
    global spaces
    print '%s<%s>' % (spaces, name)
    spaces += ' '
    #print '\targs:%s' % prettyquery(args)
    #print '\tkwargs:%s' % prettyquery(kwargs)
    #logger.fhwr.write("***"+name+" "+str(f)+"\n"\
            #+str(args)+str(kwargs)+"\n\n")
    result = f(*args, **kwargs)
    #print '\nret:%s' % prettyquery(result)
    spaces = spaces[:-1]
    print '%s</%s>' % (spaces, name)
    return result
  wrapped.__doc__ = f.__doc__
  return wrapped













