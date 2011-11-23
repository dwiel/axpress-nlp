# -*- coding: utf-8 -*-
from SimpleSPARQL import SimpleSPARQL
from Namespaces import Namespaces
from PrettyQuery import prettyquery
from Parser import Parser
from Triple import Triple
from Utils import *

from Bindings import Bindings

from rdflib import URIRef

from itertools import izip, imap
import copy, time, random

def isstr(v) :
  return isinstance(v, basestring) and not isinstance(v, URIRef)

def lua_repr(v) :
  r = repr(v)
  r = re.sub(r"^u('.*')$", r"\1", r)
  return r

class Compiler :
  MAYBE = 'maybe'
  
  def __init__(self, n = None, debug = False) :
    if n :
      self.n = n
    else :
      self.n = Namespaces()
    self.n.bind('out_lit_var', '<http://dwiel.net/axpress/out_lit_var/0.1/>')
    self.n.bind('out_var', '<http://dwiel.net/axpress/out_var/0.1/>')
    
    self.parser = Parser(self.n)
    
    self.translations = []
    self.translations_by_name = {}
    self.translations_by_id = {}
    self._next_num = 0
    self._next_translation_id = 0
    
    self.log_debug = debug
    self.debug_reset()
    self.debug_on = False
  
  def debug_reset(self) :
    self.debug_str = ""
    self.debug_block_id = 0
  
  def debug(self, str, endline='<br>') :
    if self.debug_on :
      self.debug_str += str + endline

  def debugp(self, *args) :
    if self.debug_on :
      self.debug('<xmp>' + ' '.join([prettyquery(arg) for arg in args]) + '</xmp>', '')
    
  def debug_open_block(self, title) :
    """ this is used to generate HTML debug output.  Reset the output first by
    calling debug_reset, then make the compile call, then get the output by 
    calling debugp """
    
    if self.debug_on :
      self.debug_str += """
        <div class="logblock">
        <div class="logblock-title" id="block-title-%d">%s</div>
        <div class="logblock-body" style="display:none" id="block-body-%d">
      """ % (self.debug_block_id, title, self.debug_block_id)
      self.debug_block_id += 1
  
  def debug_close_block(self) :
    if self.debug_on :
      self.debug_str += """</div></div>"""
  
  def register_translation(self, translation) :
    n = self.n
    
    # make sure all of the required keys are present
    required = [n.meta.input, n.meta.output, n.meta.name]
    missing = [key for key in required if key not in translation]
    if missing :
      raise Exception('translation is missing keys: %s' % prettyquery(missing))
    
    if n.meta.function not in translation :
      if n.meta.multi_function not in translation :
        translation[n.meta.function] = lambda x:x
    
    # parse any string expressions
    translation[n.meta.input] = self.parser.parse_query(translation[n.meta.input], reset_bnodes=False)
    translation[n.meta.output] = self.parser.parse_query(translation[n.meta.output], reset_bnodes=False)
    
    ## hash the triples
    #translation[n.meta.input]  = self.hash_triples(translation[n.meta.input])
    #translation[n.meta.output] = self.hash_triples(translation[n.meta.output])
    
    # figure out which variables are in both the input and output of the 
    # translation
    invars = find_vars(translation[n.meta.input], find_string_vars = True)
    outvars = find_vars(translation[n.meta.output], find_string_vars = True)
    #p(translation[n.meta.name])
    #p('invars', invars)
    #p('outvars', outvars)
    constant_vars = list(invars.intersection(outvars))
    translation[n.meta.constant_vars] = constant_vars
    
    translation[n.meta.id] = self.next_translation_id()
    self.translations.append(translation)
    self.translations_by_name[translation[n.meta.name]] = translation
    self.translations_by_id[  translation[n.meta.id  ]] = translation
  
  #def hash_triple(self, triple) :
    #return Triple(triple)
  
  #def hash_triples(self, triples) :
    #return map(self.hash_triple, triples)
  
  def next_translation_id(self) :
    self._next_translation_id += 1
    return self._next_translation_id
  
  def translation_can_follow(self, this, next) :
    #this_property_values = set(triple[1] for triple in this[n.meta.output])
    #next_property_values = set(triple[1] for triple in next[n.meta.input ])
    
    #return this_property_values.intersection(next_property_values)
    for triple in this[n.meta.output] :
      for ntriple in next[n.meta.input] :
        if self.triples_match(ntriple, triple) :
          return True
    
    return False
  
  def compile_translations(self) :
    self.translation_matrix = {}
    for id, translation in self.translations_by_id.iteritems() :
      self.translation_matrix[id] = [
        t for t in self.translations if self.translation_can_follow(translation, t)
      ]
      #p('t', translation[n.meta.name], [t[n.meta.name] for t in self.translation_matrix[id]])
  
  def find_matches(self, value, qvalue) :
    const, vars = split_string(value)
    regex = merge_string(const, ['(?P<%s>.+?)' % var for var in vars])
    g = re.search('^%s$' % regex, qvalue)
    if g :
      self.debugp('r', regex, qvalue, {var : g.group(var) for var in vars})
      return {var : g.group(var) for var in vars}
  
  def string_matches(self, value, qvalue) :
    return self.find_matches(value, qvalue) != None
  
  #@logger
  def values_match(self, value, qvalue) :
    #self.debugp('values_match', value, qvalue)
    if type(value) == URIRef :
      if is_var(value) :
        return True
      elif is_meta_var(value) :
        if type(qvalue) == URIRef :
          return is_any_var(qvalue) and not is_lit_var(qvalue)
        else :
          return False
      elif is_lit_var(value) :
        if type(qvalue) == URIRef :
          return is_lit_var(qvalue) or not is_any_var(qvalue)
        else :
          return True
      elif is_out_lit_var(value) :
        # not often ... probably only in the if matches(q,v) or (v,q) ...
        if is_lit_var(qvalue) :
          return True
        elif is_any_var(qvalue) :
          return False
        else :
          return True
    elif is_out_lit_var(qvalue) :
      return True
    elif isinstance(value, list) :
      ret = any(imap(lambda v : self.values_match(v, qvalue), value))
      return ret
    
    if isstr(value) and isstr(qvalue) :
      return self.string_matches(value, qvalue)
    
    if value == qvalue :
      return True
    
    #return False
  
  _triples_hash = {}
  def triples_match(self, triple, qtriple) :
    #assert isinstance(triple, Triple) and isinstance(qtriple, Triple)
    key = triple.hash + qtriple.hash
    if key in self._triples_hash :
      return self._triples_hash[key]
    
    for tv, qv in izip(triple, qtriple) :
      #print 'v',prettyquery(tv),'q',prettyquery(qv)
      if not self.values_match(tv, qv) :
        self._triples_hash[key] = False
        return False
    self._triples_hash[key] = True
    return True
  
  def find_triple_match(self, triple, query) :
    for qtriple in query :
      if self.triples_match(triple, qtriple) :
        return True
    return False
  
  def get_binding(self, triple, ftriple) :
    binding = Bindings()
    for t, q in izip(triple, ftriple) :
      if is_any_var(t) and self.values_match(t, q):
        # if the same var is trying to be bound to two different values, 
        # not a valid binding
        if t in binding and binding[var_name(t)] != q :
          return Bindings()
        binding[var_name(t)] = q
      elif (is_lit_var(t) or is_var(t)) and is_var(q) :
        binding[var_name(t)] = q
      elif isstr(t) and isstr(q) :
        # BUG: if there is more than one way to match the string with the 
        # pattern this will only return the first
        self.debugp('b', str(t), str(q))
        ret = self.find_matches(str(t), str(q))
        if ret != None:
          for name, value in ret.iteritems() :
            binding[unicode(name)] = unicode(value)
      elif isinstance(t, list) :
        # NOTE: copy and paste from above ...
        #self.debugp(str(t), str(q))
        for ti in t :
          ret = self.find_matches(str(ti), str(q))
          if ret != None:
            for name, value in ret.iteritems() :
              binding[unicode(name)] = unicode(value)
      elif t != q :
        return Bindings()
    return binding
  
  def find_bindings_for_triple(self, triple, facts, reqd_facts) :
    bindings = []
    for ftriple in facts :
      binding = self.get_binding(triple, ftriple)
      #self.debugp('ftriple', triple, ftriple, reqd_facts)
      if not reqd_facts or ftriple in reqd_facts :
        #self.debugp(True)
        binding.matches_reqd_fact = True
      #self.debugp('binding', binding, bindings)
      if binding :
        if binding in bindings :
          for b in bindings :
            if b == binding :
              b.matches_reqd_fact = b.matches_reqd_fact or binding.matches_reqd_fact
        else :
          bindings.append(binding)
    
    #for b in bindings :
      #self.debugp('b', b, b.matches_reqd_fact)
    return bindings
  
  def merge_bindings(self, a, b) :
    """
    a and b are dictionaries.  Returns True if there are keys which are in 
    both a and b, but have different values.  Used in unification
    """
    # WARNING: this should probably return the new binding so that is_out_lit_var
    # never clobbers not is_any_var
    new_bindings = Bindings()
    for k, v in a.iteritems() :
      if k in b and b[k] != v :
        if is_out_lit_var(b[k]) and not is_any_var(v) :
          new_bindings[k] = v
        elif not is_any_var(b[k]) and is_out_lit_var(v) :
          new_bindings[k] = b[k]
        else :
          return False
      else :
        new_bindings[k] = v
    
    # add bindings whose keys are in b, but not a
    for k, v in b.iteritems() :
      if k not in new_bindings :
        new_bindings[k] = v
    
    # if a or b are Bindings objects, merge their matches_reqd_fact values
    new_bindings.matches_reqd_fact = (
      (isinstance(a, Bindings) and a.matches_reqd_fact)
      or
      (isinstance(b, Bindings) and b.matches_reqd_fact)
    )
    
    return new_bindings
  
  def merge_bindings_sets(self, a, b) :
    # see if any of the next_bindings fit with the existing bindings
    new_bindings = []
    for bbinding in b :
      for abinding in a :
        new_binding = self.merge_bindings(abinding, bbinding)
        if new_binding != False :
          # WARNING: this isn't going to copy the values of the bindings!!!
          if new_binding not in new_bindings :
            new_bindings.append(new_binding)
        elif new_binding == self.MAYBE :
          # WARNING: this isn't going to copy the values of the bindings!!!
          new_binding.possible = True
          if new_binding not in new_bindings :
            new_bindings.append(new_binding)
          matches = self.MAYBE
        else :
          pass # binding conflicted
    
    return new_bindings

  def bind_vars(self, translation, facts, reqd_facts, initial_bindings = {}) :
    """
    @arg translation is a list of triples (the input part of the translation)
    @arg facts is a list of triples (the currently known facts)
    @arg reqd_facts is a list of triples of which one must be used in the binding
    @arg initial_bindings is a set of bindings which should be the starting 
        point and included in all returned bindings.  This is used by output
        unification to ensure that some of the input bindings are preserved
    @returns matches, bindings
      matches is True if the query matches the translation
      bindings is a list of bindings for var to value
    """
    
    self.debugp('translation', translation)
    self.debugp('facts', facts)
    self.debugp('reqd_facts', reqd_facts)
    self.debugp('initial_bindings', initial_bindings)
    
    matches = True
    
    # loop through each triple.  find possible bindings for each triple.  If 
    # this triple's bindings conflict with previous triple's bindings then 
    # return false.  It does not bind, unless we are only looking for partial
    # matches like for output unification.  In that case however, I think that
    # technically, there should be a split there so that we return both sets
    # of possible bindings rather than just the first one.
    # WARNING: likely bug,  See above comment
    bindings = [Bindings()]
    for ttriple in translation :
      possible_bindings = self.find_bindings_for_triple(ttriple, facts, reqd_facts)
      
      #for pbinding in possible_bindings :
        #self.debugp('pbinding', pbinding, pbinding.matches_reqd_fact)
      
      new_bindings = self.merge_bindings_sets(bindings, possible_bindings)
      
      #self.debugp('nbind', new_bindings)
      #for nbinding in new_bindings :
        #self.debugp('nbinding', nbinding, nbinding.matches_reqd_fact)
      
      if len(new_bindings) > 0 :
        bindings = new_bindings
      else :
        # in output unification reqd_facts will be False - in that case, we don't
        # care if every triple binds
        if reqd_facts != False :
          return False, []
    
    # merge with initial_bindings after collecting bindings from the facts.  It
    # is more complex to start with the initial_bindings than to end with them
    if initial_bindings :
      bindings = self.merge_bindings_sets(bindings, [initial_bindings])
    
    # get a set of all vars used in the translation
    vars = find_vars(translation, find_string_vars = True)
    
    # if there are no vars, this does still match, but there are no bindings
    if len(vars) == 0 :
      #self.debugp('len(vars)==0')
      return matches, []

    #self.debugp('vars', vars)
    #for binding in bindings :
      #self.debugp('binding', binding, binding.matches_reqd_fact)
    
    # keep only the bindings which contain bindings for all of the vars and 
    # match a reqd_triple.  In output unification reqd_facts is False and we 
    # only need partial bindings so this step isn't necessary
    if reqd_facts != False:
      bindings = [binding for binding in bindings if len(binding) == len(vars) and binding.matches_reqd_fact]
    
    # if there are no bindings, failed to find a match
    if len(bindings) == 0 :
      #self.debugp('len(bindings)==0')
      return False, []
    
    #self.debugp('matches', matches, bindings)
    return matches, bindings
  
  def find_bindings(self, facts, pattern, output_vars, reqd_triples, root = False, initial_bindings = {}) :
    """
    @arg facts is the set of triples whose values are attempting to matched to
    @arg pattern is the pattern whose variables are attempting to be matched
    @arg output_vars are variables which are not allowed to be bound to a 
      literal variable in the pattern
    @arg reqd_triples is a set of triples which is a subset of the data of which
      at least one must be used in the bindings
    @arg root is True only on the first set of matches to inform find_bindings
      that a 0 length pattern matches.  Otherwise, 0 length patterns don't match
      
    @return matches, set_of_bindings
      matches is True iff the query matched the set of data
      set_of_bindings is the set of bindings which matched the data
    """
    if len(pattern) == 0 and root:
      return True, [Bindings()]
    
    # check that all of the translation inputs match part of the query
    if reqd_triples != False:
      for triple in pattern :
        #self.debugp('find_triple_match', triple, facts)
        if not self.find_triple_match(triple, facts) :
          #self.debugp('False')
          return False, None
    
    # find all possible bindings for the vars if any exist
    matches, bindings_set = self.bind_vars(pattern, facts, reqd_triples, initial_bindings)
    return matches, bindings_set
  
  def partial_match_exists(self, pattern, reqd_triples) :
    # check that one of the reqd_triples match part of the query
    for triple in pattern :
      if self.find_triple_match(triple, reqd_triples) :
        return True
    return False
    
  def testtranslation(self, translation, query, output_vars, reqd_triples, root = False) :
    """
    @returns matches, bindings
      matches is True if the translation is guaranteed to match the query.  It 
        is self.MAYBE if the translation might match the query and False if it
        is guaranteed to not match the query.
      bindings is the set of bindings which allow this translation to match the
        query
    """
    # HEURISTIC
    # make sure that the translation's input matches part of the reqd_triples
    # otherwise, not a new path
    #p('translation[self.n.meta.input]', translation[self.n.meta.input])
    #p('query', query)
    #p('reqd_triples', reqd_triples)
    if not self.partial_match_exists(translation[self.n.meta.input], reqd_triples) :
      return False, None
      
    matches, bindings = self.find_bindings(query, translation[self.n.meta.input], output_vars, reqd_triples, root)
    
    if matches :
      return matches, bindings
    else :
      return matches, None
  
  # return all triples which have at least one var in vars
  def find_specific_var_triples(self, query, vars) :
    return [triple for triple in query if any(map(lambda x:is_out_lit_var(x) and var_name(x) in vars, triple))]

  def next_num(self) :
    self._next_num += 1
    return self._next_num

  #@logger
  def next_steps(self, query, history, output_vars, reqd_triples, root = False) :
    """
    @arg query the query in triples set form
    @arg history the history of steps already followed
    @arg output_vars is a set of variables which are not allowed to be bound as
      an input to a translation
    @returns the set of next guaranteed_steps and possible_steps.
      Ensures that this set of translation and bindings haven't already been 
      searched.....
    """
    #p('query', query)
    #p('output_vars', output_vars)
    #p('reqd_triples', reqd_triples)
    n = self.n
    
    guaranteed_steps = []
    possible_steps = []
    
    # the translation_queue is a list of translations that will be searched.  
    # There are some heuristics which alter the order that the translations are
    # searched in
    #translation_queue = list(self.translations)
    if history :
      translation_queue = self.translation_matrix[history[-1][0].get(n.meta.id)]
    else :
      translation_queue = list(self.translations)
    
    ## HEURISTIC
    ## sort translation queue so that the most recently applied translation is 
    ## tested last.  This helps avoid infite applications of the same translation
    #if history :
      #names = [h[0].get(n.meta.name) for h in history]
      #names = [name for name in names if name]
      
      #translation_queue = [
        #t for t in translation_queue if t.get(n.meta.name) not in names
      #]
      #translation_queue.extend([h[0] for h in history])
    
    # HEURISTIC
    # stop DFS search at depth 5
    if history :
      #print '#'*80
      #print len(history)
      if len(history) >= self.depth :
        translation_queue = []
    #print len(history)
    
    for translation in translation_queue :
      # HEURISTIC
      if history :
        inverse_function = history[-1][0].get(n.meta.inverse_function) 
        if inverse_function :
          if inverse_function == translation[n.meta.name] :
            continue
      
      #self.debug('testing ' + translation[n.meta.name])
      #p('testing', translation[n.meta.name])
      matches, bindings_set = self.testtranslation(translation, query, output_vars, reqd_triples, root)
      if matches :
        # we've found a match, now we just need to find the bindings.  This is
        # the step where we unify the new information (generated by output 
        # triples) with existing information.
        self.debug('found match ' + translation[n.meta.name])
        #p('translation[n.meta.name]', translation[n.meta.name])
        for bindings in bindings_set :
          # copies the bindings so we can manipulate it while keeping the 
          # possible property intact
          new_bindings = Bindings(possible = bindings.possible)
          # replace the bindings which the translation defines as constant with
          # the exact binding value
          # replace the other bindings which are variables, with variables with
          # the name from the query and the type from the translation ...
          for var, value in bindings.iteritems() :
            if var in translation[n.meta.constant_vars] :
              new_bindings[var] = value
            elif is_any_var(value) :
              new_var = n.lit_var[var_name(value)+'_'+str(self.next_num())]
              new_bindings[var] = new_var
            else :
              assert "none shall pass"
          
          # input_bindings map from translation space to query space
          input_bindings = bindings
          # output_bindings map from translation space to query space
          output_bindings = {}
          
          # initial_bindings are the bindings that we already know from the 
          # input unification that must also hold true for output unification
          # some of the initial_binding vars don't appear in the output triples
          # so we can get rid of them
          output_triple_vars = find_vars(translation[n.meta.output], find_string_vars = True)
          output_triples = translation[n.meta.output]
          #self.debugp('constant_vars', translation[n.meta.constant_vars])
          initial_bindings = dict(
            (unicode(name), bindings[name]) for name in translation[n.meta.constant_vars]
              if name in bindings and 
                name in output_triple_vars
          )
          
          # used in a couple places later on
          output_lit_vars = find_vars(translation[n.meta.output], is_lit_var)
          
          #self.debugp('input_bindings', input_bindings)
          #self.debugp('initial_bindings', initial_bindings)
          
          if n.meta.input_function in translation :
            #self.debugp('n.meta.input_function', translation[n.meta.input_function])
            if not translation[n.meta.input_function](input_bindings) :
              #self.debugp('didnt pass input function')
              continue
          #self.debugp('query', query)
          #self.debugp('output_triples', output_triples)
          #self.debugp('initial_bindings', initial_bindings)
          
          # unify output_triples with query
          output_matches, output_bindings_set = self.find_bindings(query, output_triples, [], False, initial_bindings = initial_bindings)
          if not output_matches :
            output_bindings_set = [initial_bindings]
          
          for output_bindings in output_bindings_set :
            # if var is a lit var in the output_triples, then its output bindings
            # must bind it to a new variable since it will be computed and set by
            # the translation function and may not have the same value any more
            # WARNING: I think this means that find_bindings might not do the 
            # right thing if it thinks that it can bind whatever it wants to 
            # lit_vars.  lit_vars for example shouldn't bind to literal values
            
            self.debugp('output_bindings', output_bindings)
            
            # if get_bindings found variable to variable matches, we will need
            # to alter the triples in the existing query (not just add triples)
            # unified_bindings maps old query variables to new query variables
            unified_bindings = {}
            for var in output_lit_vars :
              new_lit_var = n.lit_var[var+'_out_'+str(self.next_num())]
              if var in output_bindings :
                if is_any_var(output_bindings[var]) :
                  unified_bindings[var_name(output_bindings[var])] = new_lit_var
              output_bindings[var] = new_lit_var
            
            #self.debugp('unified_bindings', unified_bindings)
            #self.debugp('output_bindings', output_bindings)
            
            for var in find_vars(translation[n.meta.output], is_var) :
              #print var
              if var not in output_bindings :
                output_bindings[var] = n.var[var+'_'+str(self.next_num())]
            
            #self.debugp('output_bindings', output_bindings)
            
            # generate the new query by adding the output triples with 
            # output bindings substituted in
            #p('output_bindings', output_bindings)
            new_triples = sub_var_bindings(translation[n.meta.output], output_bindings)
            # TODO:is this necessary:
            # I wonder if the triples which are changed here need to be added to
            # new_triples ...
            new_query, new_query_new_triples = sub_var_bindings_track_changes(query, unified_bindings)
            new_query.extend(new_triples)
            new_triples.extend(new_query_new_triples)
            
            # remove output_bindings which are not constant_vars or lit_vars (in
            # the translation's output triples.  An example of an instance when
            # a variable would be in output_bindings that we would remove here is
            # when an output_triple has normal variables which are not used in 
            # the input, but also aren't bound to anything by the translation fn.
            # we want to know if that variable binds to anything for creating 
            # new_triples above, but as far as the evaluator is concerned, it has
            # no value and thus no output binding
            output_bindings = {
              var: binding for var, binding in output_bindings.iteritems()
              if var in output_lit_vars or
                var in translation[n.meta.constant_vars]
            }
            
            self.debugp('new_triples', new_triples)
            self.debugp('new_query', new_query)
            self.debugp('output_bindings', output_bindings)
            
            # TODO: this will need to be better fleshed out when we want to 
            # support possible steps.  For now execution always goes to the elif 
            # below
            if matches == self.MAYBE :
              possible_steps.append({
                'query' : query,
                'input_bindings' : input_bindings,
                'output_bindings' : output_bindings,
                'translation' : translation,
                'new_triples' : new_triples,
                'new_query' : new_query,
                'guaranteed' : [],
                'possible' : [],
              })
            elif matches == True :
              var_triples = self.find_specific_var_triples(new_query, self.reqd_bound_vars)
              partial_bindings, partial_solution_triples, partial_facts_triples = self.find_partial_solution(var_triples, new_query, new_triples)
              #partial_triples = [triple for triple in partial_triples if triple in new_triples]
              
              guaranteed_steps.append({
                'input_bindings' : input_bindings,
                'output_bindings' : output_bindings,
                'translation' : translation,
                'new_triples' : new_triples,
                'new_query' : new_query,
                'guaranteed' : [],
                'possible' : [],
                'partial_solution_triples' : partial_solution_triples,
                'partial_facts_triples' : partial_facts_triples,
                'partial_bindings' : partial_bindings,
              })
    
    return guaranteed_steps, possible_steps
  
  def find_solution_values_match(self, tv, qv) :
    """
    does the pattern (value) in tv match the value of qv?
    """
    if is_any_var(tv) :
      if is_out_lit_var(tv) :
        # if the pattern is an out_lit_var, qv must be a lit_var or a literal
        if is_lit_var(qv):
          return {tv : qv}
        elif is_any_var(qv) :
          return False
        else :
          return {tv : qv}
      elif is_out_var(tv) :
        # not sure if this is really right ...
        if is_any_var(qv) :
          if var_name(tv) == var_name(qv) :
            return {tv : qv}
        return False
      elif is_out_lit_var(qv) :
        # This happens when a query is looking for a literal variable and a 
        # translation is willing to provide a variable, just not a literal one.
        # (see lastfm similar artist output variable similar_artist) and a query
        # wanting it to be literal
        #raise Exception("Does this really happen?")
        return False
      elif is_lit_var(tv) and is_lit_var(qv) :
        return True
      elif is_any_var(qv) :
        return var_name(tv) == var_name(qv)
      return False
    else :
      return tv == qv
  
  def find_solution_triples_match(self, triple, qtriple) :
    """
    does the pattern in triple match the qtriple?
    """
    bindings = {}
    for tv, qv in izip(triple, qtriple) :
      #p(tv, qv, self.find_solution_values_match(tv, qv))
      ret = self.find_solution_values_match(tv, qv)
      if not ret :
        return False
      elif isinstance(ret, dict) :
        bindings.update(ret)
    return bindings or True
  
  def find_solution_triple(self, triple, facts) :
    """
    does the pattern defined in triple have a match in facts?
    """
    for ftriple in facts :
      bindings = self.find_solution_triples_match(triple, ftriple)
      #p(triple)
      #p(ftriple)
      #p()
      if bindings :
        if bindings :
          return bindings, ftriple
        else :
          return True, ftriple
    return False, None
    
  def find_solution(self, var_triples, facts) :
    """
    returns True if a solution for var_triples can be found in facts
    @arg var_triples is the set of triples which need to be bound in query for
      a solution to exist
    @arg query is the query to find a solution satisfying var_triples in
    @returns True iff a solution exists
    """
    bindings = {}
    for triple in var_triples :
      new_bindings, ftriple = self.find_solution_triple(triple, facts)
      if not new_bindings :
        return False
      #if isinstance(new_bindings, dict) :
        #bindings.update(new_bindings)
      bindings.update(new_bindings)
    return bindings or True
  
  def find_partial_solution(self, var_triples, facts, interesting_facts) :
    """
    returns a list triples from var_triples which have matches in facts
    """
    bindings = {}
    found_var_triples = []
    fact_triples = []
    for triple in var_triples :
      #p('triple', triple)
      #p('facts', facts)
      new_bindings, ftriple = self.find_solution_triple(triple, facts)
      if new_bindings :
        if new_bindings == True :
          pass
        else :
          bindings.update(new_bindings)
        if ftriple in interesting_facts :
          found_var_triples.append(triple)
          fact_triples.append(ftriple)
    
    # make bindings just to the variable name not the full URI (if the value of
    # the binding is a varialbe, make sure it is in the n.var namespace)
    # at one point, just the variable name was used, but sometimes the compiler
    # can actually find hard values for the bindings (no evaluation required)
    # and so we must use a full uri
    def normalize(value) :
      if is_any_var(value) :
        return n.var[var_name(value)]
      else :
        return value
    bindings = dict([(var_name(var), normalize(value)) for var, value in bindings.iteritems()])
    return bindings, found_var_triples, fact_triples
  
  def found_solution(self, new_query) :
    # NOTE: it is quite possible that the output unification step has enough 
    # information to know if a solution has been found too, which could make
    # this step unecessary.
    
    # var_triples are the triples which contain the variables which we are 
    # looking to bind
    var_triples = self.find_specific_var_triples(new_query, self.reqd_bound_vars)
    initial_bindings = {var: n.var[var] for var in find_vars(var_triples, lambda x:is_var(x) or is_lit_var(x))}
    
    # see if the triples which contain the variables can bind to any of the 
    # other triples in the query
    found_bindings, bindings_set = self.find_bindings(new_query, var_triples, [], False, initial_bindings = initial_bindings)
    if found_bindings :
      for bindings in bindings_set :
        found_bindings_for = set()
        # find the bindings that are bound to a lit var or a value.  Sometimes
        # a variable will be bound to another variable, but that is not a result
        for k, v in bindings.iteritems() :
          if is_lit_var(v) or not is_any_var(v) :
            found_bindings_for.add(k)
        
        # if we found bindings 
        if found_bindings_for == set(self.reqd_bound_vars) :
          # WARNING: it is possible that multiple bindings will be valid in 
          # which case we should return a set of solutions rather than a 
          # solution
          return {n.var[name] : v for name, v in bindings.iteritems()}
    
    return False
  
  #@logger
  def search(self, query, stack, history, output_vars, new_triples, root = False) :
    """
    follow guaranteed translations and add possible translations to the 
      possible_stack
    this is somewhat of an evaluator ...
    @arg query is the query to start from
    @arg possible_stack is a list which is filled in with next next possible 
      translations to follow after the guaranteed translations have already been
      followed completely
    @history is a list of all the paths we've already explored so we don't 
      repeat them.
    @arg output_vars is a set of variables which are not allowed to be bound as
      an input to a translation
    @new_triples is a set of triples which are new as of the previous 
      translation.  This next translation must take them into account.  If they
      are not needed, then an earlier step could have gotten there already and
      the most recent step was unnecessary
    @return the compiled guaranteed path (see thoughts for more info on this 
      structure)
    """
    
    #p('query', query)
    
    #guaranteed_steps, possible_steps = self.next_steps(query, history, output_vars, new_triples, root)
    ##stack.extend(guaranteed_steps)
    #if not guaranteed_steps :
      #return False
    
    #step = guaranteed_steps[0]
    ##p('stack', stack)
    
    all_steps = []
    while True :
      # see what the guaranteed and possible next steps are
      #print '%'*80
      #p('query', query)
      #p('output_vars', output_vars)
      #p('new_triples', new_triples)
      #p('root', root)
      reqd_bound_vars = []
      self.make_vars_out_vars(query, reqd_bound_vars)
      var_triples = self.find_specific_var_triples(query, reqd_bound_vars)
      guaranteed_steps, possible_steps = self.next_steps(query, history, output_vars, query, root)
      #p('guaranteed_steps', guaranteed_steps)
      #p('possible_steps', possible_steps)
      
      if len(guaranteed_steps) == 0 :
        self.debug_close_block()
        return False
      
      self.debug_open_block('guaranteed_steps')
      self.debugp(guaranteed_steps)
      self.debug_close_block()
      
      ## look at the first step and add the rest of the steps to the stack
      #step       = guaranteed_steps[0]
      ##next_steps = guaranteed_steps[1:]
      ##stack = next_steps.extend(stack)
      
      ## if we've already made this translation, skip it
      #if [step['translation'], step['input_bindings']] in history :
        #continue
      
      for step in guaranteed_steps :
        if [step['translation'], step['input_bindings']] not in history :
          break
      
      all_steps.append(step)
      
      self.debugp(step['translation'][n.meta.name] or '<unnamed>')
      
      # add this step to the history (though since this history object can be 
      # forked by other guaranteed_steps, we must copy it first)
      history.append([step['translation'], copy.copy(step['input_bindings'])])
      
      # if the new information at this point is enough to fulfil the query, done
      # otherwise, recursively continue searching.
      # found_solution is filled with the bindings from the query to the 
      # out_lit_vars
      found_solution = self.found_solution(step['new_query'])
      if found_solution :
        step['solution'] = found_solution
        p('all_steps', all_steps)
        
        def build_ret(steps) :
          if steps :
            step = steps[0]
            step['guaranteed'] = [build_ret(steps[1:])]
            step['possible'] = []
            return step
          else :
            return []
          
        ret = [{
          'guaranteed' : build_ret(all_steps),
          'possible' : []
        }]
        p('ret', ret)
        return ret
      else :
        # NOTE: I think the problem is here.
        # if new_triples is simple, this works
        # if the translation must be unified to the query in order to output
        # then the entire output unification step would need to happen here
        # rather than in next_steps.  Also, if this step was pulled off of the
        # stack, the old input_bindings might not make any sense any more ...
        # how to resolve that?
        
        query = step['new_query']
        #query.extend(step['new_triples'])
        #new_triples = step['new_triples']
    
    return False
  
  def make_vars_out_vars(self, query, reqd_bound_vars) :
    """
    replaces all instances of variables in query whose name is in the 
    reqd_bound_vars list with self.n.out_lit_var variables of the same name
    @arg query is a query to change
    @arg reqd_bound_vars are variable to change
    """
    for triple in query :
      for j, value in enumerate(triple) :
        if is_lit_var(value) and var_name(value) in reqd_bound_vars :
          triple[j] = self.n.out_lit_var[var_name(value)]
        elif is_any_var(value) and var_name(value) in reqd_bound_vars :
          triple[j] = self.n.out_var[var_name(value)]
  
  def extract_query_modifiers(self, query) :
    modifiers = {}
    new_query = []
    for triple in query :
      modified = False
      if triple[0] == self.n.query.query :
        if triple[1] == self.n.query.limit :
          modifiers.update({'limit' : int(triple[2])})
          modified = True
      
      if not modified :
        new_query.append(triple)
    new_query
    
    return new_query, modifiers
  
  def extract_which_translations_fulfil_which_query_triple(self, node, depends = []) :
    which_translations_fulfil_which_query_triple = []
    if 'guaranteed' not in node :
      return []
    for step in node['guaranteed'] :
      for triple in step['partial_solution_triples'] :
        which_translations_fulfil_which_query_triple.append((tuple(triple), step, depends))
      which_translations_fulfil_which_query_triple.extend(self.extract_which_translations_fulfil_which_query_triple(step, depends + [step]))
    return which_translations_fulfil_which_query_triple
  
  def permute_combinations(self, combination, translation) :
    """
    a combination is a dict with each key as a solution triple and each value
    as a translation which will return bindings for the triple.
    This takes a translation, and by looking at its depencies determines if
    TODO: finish figuring out what this does
    """
    new_combination = copy.copy(combination)
    for dependency in translation['depends'] :
      #p('dependency',dependency['translation'][n.meta.name])
      #p('partial_solution_triples',dependency['partial_solution_triples'])
      for depends_triple in dependency['partial_solution_triples'] :
        depends_triple = tuple(depends_triple)
        #p('depends_triple',depends_triple)
        if depends_triple in combination :
          if dependency is not combination[depends_triple] :
            p('ret',False)
            return False
        else :
          new_combination[depends_triple] = dependency
    return new_combination

  def compile(self, query, reqd_bound_vars, input = [], output = []) :
    self.debug_reset()
    
    if isinstance(query, basestring) :
      query = [line.strip() for line in query.split('\n')]
      query = [line for line in query if line is not ""]
    query = self.parser.parse(query)
    
    query, modifiers = self.extract_query_modifiers(query)
    
    self.make_vars_out_vars(query, reqd_bound_vars)
    
    #debug('query',query)
    
    self.reqd_bound_vars = reqd_bound_vars
    var_triples = self.find_specific_var_triples(query, reqd_bound_vars)
    if var_triples == [] :
      raise Exception("Waring, required bound triples were provided, but not found in the query")
    
    self.vars = reqd_bound_vars
    self.vars = [var for var in self.vars if var.find('bnode') is not 0]
    #debug('self.vars',self.vars)
    
    possible_stack = []
    history = []
    
    ## an iterative deepening search
    #self.depth = 1
    #compile_root_node = None
    #while not compile_root_node and self.depth < 8:
      #self.debugp("depth: %d" % self.depth)
      #compile_root_node = self.search(query, possible_stack, history, reqd_bound_vars, query, True)
      #self.depth += 1
    # an iterative deepening search
    self.depth = 10
    compile_root_node = self.search(query, possible_stack, history, reqd_bound_vars, query, True)
    
    # if there were no paths through the search space we are done here
    if not compile_root_node :
      return compile_root_node
    
    #p('compile_root_node', compile_root_node)
    
    def p_cnode(cnode, level = 0) :
      if 'translation' in cnode :
        print '  '*level, cnode['translation'][n.meta.name]
      for g in cnode['guaranteed'] :
        p_cnode(g, level + 1)
    
    #p_cnode(compile_root_node)
    
    # HIGH LEVEL:
    # at this point, we must go through the resulting steps and figure out which
    # are actually necessary.  It is quite possible that there are translations
    # in the resulting path which don't need to be executed.  In some cases
    # executing unneeded translations is just wasted computation, but in others
    # if the translation has side effects, we must avoid executing them to 
    # preserve correctness
    
    which_translations_fulfil_which_query_triple = self.extract_which_translations_fulfil_which_query_triple(compile_root_node)
    
    #p('which_translations_fulfil_which_query_triple', which_translations_fulfil_which_query_triple)
    
    which_translations_fulfil_which_query_triple_dict = {}
    for triple, step, depends in which_translations_fulfil_which_query_triple :
      obj = {'step' : step, 'depends' : depends}
      if triple in which_translations_fulfil_which_query_triple_dict :
        which_translations_fulfil_which_query_triple_dict[triple].append(obj)
      else :
        which_translations_fulfil_which_query_triple_dict[triple] = [obj]
    
    # generate path combinations
    # a combination is a dictionary from triple to translation, which each 
    # triple is from the var_triples set.  A full completion/solution will 
    # have one translation for each var_triple.
    #p('begin combinations')
    combinations = [{}]
    new_combinations = []
    for triple, translations in which_translations_fulfil_which_query_triple_dict.iteritems() :
      for translation in translations :
        for combination in combinations :
          # for each existing combination, if it already depends on a different
          # solution for a triple that this new translation depends on, can
          # not use it in a combination.
          # if none of the existing combinations fits with this one, there is
          # no solution
          # if the dependencies of this
          new_combination = self.permute_combinations(combination, translation)
          if new_combination is not False:
            new_combination[triple] = translation
            new_combinations.append(new_combination)
      if len(new_combinations) > 0 :
        combinations = new_combinations
        new_combinations = []
      else :
        p('not')
    
    def print_combinations(combinations) :
      p('len(combinations)',len(combinations))
      for combination in combinations :
        p('len(combination)',len(combination))
        p('combination',combination.keys())
        for triple, translation in combination.iteritems() :
          p('triple',triple)
          p('translation',translation['step'])
          for dependency in translation['depends'] :
            p('dependency',dependency['translation'][n.meta.name])
            
    #print_combinations(combinations)
    
    # we don't care which translations were for which triple any more
    combinations = [combination.values() for combination in combinations]
    
    # we also don't care about guaranteed steps any more
    for combination in combinations:
      for translation in combination :
        if 'guaranteed' in translation['step'] :
          del translation['step']['guaranteed']
        for depend in translation['depends'] :
          if 'guaranteed' in depend :
            del depend['guaranteed']
    
    # solution_bindings_set is a list of bindings which correspond to the list 
    # of combinations.  Each bindings defines which variables each output 
    # variable will be bound to
    solution_bindings_set = []
    for combination in combinations :
      solution_bindings = {}
      for translation in combination :
        solution_bindings.update(translation['step']['partial_bindings'])
      solution_bindings_set.append(solution_bindings)
    
    # if a translation listed in the root of the combinations is a dependency
    # of another root, dont include it.  It will be computed anyway.
    # so, first make a list of every dependency
    all_depends = []
    all_steps = []
    for combination in combinations :
      for translation in combination :
        for depend in translation['depends'] :
          if depend not in all_depends :
            all_depends.append(depend)
          if depend not in all_steps :
            all_steps.append(depend)
        if translation['step'] not in all_steps :
          all_steps.append(translation['step'])
    
    #p('all_steps',all_steps)
    #p('all_depends',all_depends)
    #p([depend['translation'][n.meta.name] for depend in all_depends])
    
    new_combinations = []
    for combination in combinations :
      new_combination = [translation for translation in combination if translation['step'] not in all_depends]
      new_combinations.append(new_combination)
    combinations = new_combinations
    
    #p('combinations',len(combinations[0]))
    
    # get rid of unnecessary input bindings
    for step in all_steps :
      step['input_bindings'] = dict([(var, binding) for (var, binding) in step['input_bindings'].iteritems() if not is_var(binding)])
      
      step['output_bindings'] = dict([(var, binding) for (var, binding) in step['output_bindings'].iteritems() if not is_var(binding)])
      #p("step['output_bindings']",step['output_bindings'])
    
    ret = {
      'combinations' : combinations,
      'modifiers' : modifiers,
      'solution_bindings_set' : solution_bindings_set
    }
    self.debug_open_block('result')
    self.debugp(ret)
    self.debug_close_block()
    return ret
    
