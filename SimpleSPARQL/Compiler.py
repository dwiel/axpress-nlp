# -*- coding: utf-8 -*-
from SimpleSPARQL import SimpleSPARQL
from Namespaces import Namespaces
from PrettyQuery import prettyquery
from Parser import Parser
from Triple import Triple
from Utils import *
import StringMatch

from Bindings import Bindings

from URIRef import URIRef

from itertools import izip, imap
import copy, time, random
from collections import defaultdict

# for catching re errors
import sre_constants

def logger(fn) :
  def new_fn(*args, **kwargs) :
    ret = fn(*args, **kwargs)
    if args[1].get('depends') :
      p('log-fn', fn.__name__)
      p('args', args)
      p('kwargs', kwargs)
      p('ret', ret)
    return ret
  return new_fn

def isstr(v) :
  return isinstance(v, basestring) and not isinstance(v, URIRef)

def hash(inbindings, outbindings) :
  import hashlib
  m = hashlib.md5()
  for k, v in sorted(inbindings.items()) :
    m.update(str(k)+str(v))
  for k, v in sorted(outbindings.items()) :
    m.update(str(k)+str(v))
  return m.hexdigest()[0:6]

def color(hex) :
  return """<span style="color:#%s">%s</span>""" % (hex, hex)

class Compiler :
  MAYBE = 'maybe'
  
  def __init__(self, n = None, debug = False) :
    if n :
      self.n = n
    else :
      self.n = Namespaces()
      
    self.n.bind('query',  '<http://dwiel.net/axpress/query/0.1/>')
    self.n.bind('var',     '<http://dwiel.net/axpress/var/0.1/>')
    self.n.bind('tvar',    '<http://dwiel.net/axpress/translation/var/0.1/>')
    self.n.bind('bnode',   '<http://dwiel.net/simplesparql/bnode/0.1/>')
    self.n.bind('lit_var', '<http://dwiel.net/express/lit_var/0.1/>')
    
    self.parser = Parser(self.n)
    
    self.translations = []
    self.translations_by_name = {}
    self.translations_by_id = {}
    self._next_num = 0
    self._next_translation_id = 0
    
    self.match_strings_both_ways = False
    
    self._debug = self.debug
    self._debugp = self.debugp
    self._debugps = self.debugps
    self._debug_open_block = self.debug_open_block
    self._debug_close_block = self.debug_close_block

    self.show_dead_ends = True
    
    self.block_depth = 0
    self.log_debug = debug
    self.debug_reset()

  def next_num(self) :
    """ for generating unique lit_var name """
    self._next_num += 1
    return self._next_num
    
  def nop(*args, **kwargs) :
    pass

  def debug_on(self) :
    self.debug = self._debug
    self.debugp = self._debugp
    self.debugps = self._debugps
    self.debug_open_block = self._debug_open_block
    self.debug_close_block = self._debug_close_block
      
  def debug_off(self) :
    self.debug = self.nop
    self.debugp = self.nop
    self.debugps = self.nop
    self.debug_open_block = self.nop
    self.debug_close_block = self.nop

  def debug_reset(self) :
    self.debug_str = ""
    self.debug_block_id = 0
  
  def debug(self, str, endline='<br>') :
    self.debug_str += str + endline

  def debugp(self, *args) :
    self.debug('<xmp>' + ' '.join([prettyquery(arg) for arg in args]) + '</xmp>', '')
    
  def debugps(self, *args) :
    self.debug(' '.join([prettyquery(arg) for arg in args]))
  
  def debug_open_block(self, title) :
    """ this is used to generate HTML debug output.  Reset the output first by
    calling debug_reset, then make the compile call, then get the output by 
    calling debugp """
    
    self.debug_str += """
      <div class="logblock">
      <div class="logblock-title" id="block-title-%d">%s</div>
      <div class="logblock-body" id="block-body-%d" style="display:none">
    """ % (self.debug_block_id, title, self.debug_block_id)
    self.debug_block_id += 1
    self.block_depth += 1
  
  def debug_close_block(self) :
    self.debug_str += """</div></div>"""
    self.block_depth -= 1
  
  def rule(self, name, input, output, fn=None, input_function=None, **kwargs) :
    """ shorthand for full length register_translation """
    assert isinstance(name, basestring)
    options = {
      'name'   : name,
      'input'  : input,
      'output' : output,
      'function' : fn,
      'input_function' : input_function,
    }
    options.update(kwargs)
    self.register_translation(options)

  def register_translation(self, translation) :
    # make sure all of the required keys are present
    required = ['input', 'output', 'name']
    missing = [key for key in required if key not in translation]
    if missing :
      raise Exception('translation is missing keys: %s' % prettyquery(missing))
    
    if 'function' not in translation or translation['function'] == None :
      if 'multi_function' not in translation :
        translation['function'] = lambda x:x
    
    if 'input_function' in translation and translation['input_function'] == None :
      del translation['input_function']
      
    translation['step_size'] = translation.get('step_size', 1)
    
    # parse any string expressions
    translation['input'] = self.parser.parse_query(translation['input'], reset_bnodes=False)
    translation['output'] = self.parser.parse_query(translation['output'], reset_bnodes=False)
    #p(translation['name'], translation['input'], translation['output'])
    
    ## hash the triples
    #translation['input']  = self.hash_triples(translation['input'])
    #translation['output'] = self.hash_triples(translation['output'])
    
    # figure out which variables are in both the input and output of the 
    # translation
    invars = find_vars(translation['input'], find_string_vars = True)
    outvars = find_vars(translation['output'], find_string_vars = True)
    outvars = outvars.union(set(translation.get('output_vars', [])))
    #p(translation['name'])
    #p('invars', invars)
    #p('outvars', outvars)
    translation['constant_vars'] = list(
      invars.intersection(outvars)
    )
    
    translation['in_lit_vars'] = find_vars(
      translation['input'], is_lit_var, find_string_vars = True
    )
    
    import inspect
    filename = inspect.currentframe().f_back.f_back.f_code.co_filename
    
    translation['filename'] = filename
    translation['id'] = self.next_translation_id()
    self.translations.append(translation)
    self.translations_by_name[translation['name']] = translation
    self.translations_by_id[  translation['id'  ]] = translation
    
  #def hash_triple(self, triple) :
    #return Triple(triple)
  
  #def hash_triples(self, triples) :
    #return map(self.hash_triple, triples)
  
  def next_translation_id(self) :
    self._next_translation_id += 1
    return self._next_translation_id
  
  def translation_can_follow(self, this, next) :
    """ a translation can follow if any of the output triples of this match
    with any of the input triples from next """
    for triple in this['output'] :
      for ntriple in next['input'] :
        if self.triples_match(ntriple, triple) :
          return True
    
    return False
  
  def compile_translations(self) :
    self.match_strings_both_ways = True
    self.translation_matrix = {}
    for id, translation in self.translations_by_id.iteritems() :
      self.translation_matrix[id] = [
        t for t in self.translations if self.translation_can_follow(translation, t)
      ]
      #p('t', translation['name'], [t['name'] for t in self.translation_matrix[id] ])
    #print 'avg', sum(len(ts) for ts in self.translation_matrix.values())/float(len(self.translation_matrix))
    #print [len(ts) for ts in self.translation_matrix.values()]
    #print [t['name'] for t in self.translations if len(t['input']) != 1]
    self.match_strings_both_ways = False
  
  
  #############################################################################
  # MATCHING
  
  def find_matches(self, value, qvalue) :
    return StringMatch.match(value, qvalue)
    
  def string_matches(self, value, qvalue) :
    # boolean version of find_matches
    # note that [] denotes a successful basic string match, just without any
    # variables to match against
    return self.find_matches(value, qvalue) not in [None, False]
  
  def values_match(self, value, qvalue) :
    #self.debugp('values_match', value, qvalue)
    if is_any_var(value) :
      if is_var(value) :
        return True
      elif is_meta_var(value) :
        if is_any_var(qvalue) :
          return is_any_var(qvalue) and not is_lit_var(qvalue)
        else :
          return False
      elif is_lit_var(value) :
        if is_any_var(qvalue) :
          return is_lit_var(qvalue) or not is_any_var(qvalue)
        else :
          return True
      elif is_out_lit_var(value) :
        # not often ... probably only in the if matches(q,v) or (v,q) ...
        if is_lit_var(qvalue) :
          return True
        #elif is_out_lit_var(qvalue) :
          #return True
        elif is_any_var(qvalue) :
          return False
        else :
          return True
      else :
        raise Exception('shouldnt get here')
    elif is_out_lit_var(qvalue) :
      return True
    elif isinstance(value, list) :
      ret = any(imap(lambda v : self.values_match(v, qvalue), value))
      return ret
    
    if isstr(value) and isstr(qvalue) :
      if self.match_strings_both_ways :
        return self.string_matches(value, qvalue) or self.string_matches(qvalue, value)
      else :
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
        #print 'v',prettyquery(tv),'q',prettyquery(qv), False
        return False
    #print 'v',prettyquery(tv),'q',prettyquery(qv), True
    self._triples_hash[key] = True
    return True
  
  def find_triple_match(self, triple, query) :
    for qtriple in query :
      if self.triples_match(triple, qtriple) :
        return True
    return False
  
  def partial_match_exists(self, pattern, reqd_triples) :
    # check that one of the reqd_triples match part of the query
    for triple in pattern :
      if self.find_triple_match(triple, reqd_triples) :
        return True
    return False
    
  #############################################################################
  # BINDINGS
  def mul_bindings_set(self, bs1, bs2) :
    new_bs = []
    for b1 in bs1 :
      for b2 in bs2 :
        #b2 = copy.copy(b2)
        for name, value in b1.iteritems() :
          b2[name] = value
        new_bs.append(b2)
    return new_bs
  
  def get_binding(self, triple, ftriple) :
    bindings = [Bindings()]
    for t, q in izip(triple, ftriple) :
      if is_any_var(t) and self.values_match(t, q):
        # if the same var is trying to be bound to two different values, 
        # not a valid binding
        if t in bindings[0] and bindings[0][t.name] != q :
          return []
        bindings = self.mul_bindings_set(bindings, [Bindings({t.name : q})])
        #binding[t.name] = q
      elif (is_lit_var(t) or is_var(t)) and is_var(q) :
        # prefer_litvars is set in bind_vars.  In some cases we never want to 
        # bind a litvar to a var because it means we would be loosing 
        # information
        if self.prefer_litvars and is_lit_var(t) :
          assert q.name not in bindings[0]
          bindings = self.mul_bindings_set(bindings, [Bindings({q.name : t})])
          #binding[q.name] = t
        else :
          assert t.name not in bindings[0]
          bindings = self.mul_bindings_set(bindings, [Bindings({t.name : q})])
          #binding[t.name] = q
      elif isstr(t) and isstr(q) :
        # BUG: if there is more than one way to match the string with the 
        # pattern this will only return the first
        # I believe that this bug is fixed in 0647dad1 and nearby commits
        ret = self.find_matches(str(t), str(q))
          
        if ret not in [None, False, []] :
          for name, value in ret[0].iteritems() :
            assert unicode(name) not in bindings[0]
          
          #p('pre', bindings)
          bindings = self.mul_bindings_set(bindings, map(Bindings, ret))
          #p('post', bindings)
        #p('')
        #binding[unicode(name)] = unicode(value)
      elif isinstance(t, list) :
        # NOTE: copy and paste from above ...
        for ti in t :
          #p('qi',str(ti), '-', str(q))
          ret = self.find_matches(str(ti), str(q))
          if ret not in [None, False, []] :
            for name, value in ret[0].iteritems() :
              assert unicode(name) not in bindings[0]
            
            #p('pre', bindings)
            bindings = self.mul_bindings_set(bindings, map(Bindings, ret))
            #p('post', bindings)
            #binding[unicode(name)] = unicode(value)
          #p('')
      elif t != q :
        return []
      elif is_lit_var(t) and is_out_lit_var(q) :
        bindings = self.mul_bindings_set(bindings, [Bindings({t.name : q})])
    if len(bindings) == 1 and not bindings[0] :
      return []
    return bindings
  
  def find_bindings_for_triple(self, triple, facts, reqd_facts) :
    ret_bindings = []
    for ftriple in facts :
      bindings = self.get_binding(triple, ftriple)
      #self.debugp('ftriple', triple, ftriple, reqd_facts)
      if not reqd_facts or ftriple in reqd_facts :
        #self.debugp(True)
        for binding in bindings :
          binding.matches_reqd_fact = True
      #self.debugp('binding', binding, bindings)
      if bindings :
        for binding in bindings :
          if binding in ret_bindings :
            for b in bindings :
              if b == binding :
                b.matches_reqd_fact = b.matches_reqd_fact or binding.matches_reqd_fact
          else :
            ret_bindings.append(binding)
    
    #for b in bindings :
      #self.debugp('b', b, b.matches_reqd_fact)
    return ret_bindings
  
  def merge_bindings(self, a, b) :
    """
    a and b are dictionaries.  Returns True if there are keys which are in 
    both a and b, but have different values.  Used in unification
    """
    # WARNING: this should probably return the new binding so that
    # is_out_lit_var never clobbers not is_any_var
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

  def bind_vars(self, translation, facts, reqd_facts, initial_bindings = {}, prefer_litvars = False) :
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
    
    #self.debugp('translation', translation)
    #self.debugp('facts', facts)
    #self.debugp('reqd_facts', reqd_facts)
    #self.debugp('initial_bindings', initial_bindings)
    
    self.prefer_litvars = prefer_litvars
    
    # loop through each triple.  find possible bindings for each triple.  If 
    # this triple's bindings conflict with previous triple's bindings then 
    # return false.  It does not bind, unless we are only looking for partial
    # matches like for output unification.  In that case however, I think that
    # technically, there should be a split there so that we return both sets
    # of possible bindings rather than just the first one.
    # WARNING: likely bug,  See above comment
    # check that all of the translation inputs match part of the query

    if reqd_facts != False:
      for triple in translation :
        if not self.find_triple_match(triple, facts) :
          return False
    
    bindings = [Bindings()]
    for ttriple in translation :
      possible_bindings = self.find_bindings_for_triple(ttriple, facts, reqd_facts)
      
      #for pbinding in possible_bindings :
        #p('pbinding', pbinding, pbinding.matches_reqd_fact)
      #p('bindings', bindings)
      
      new_bindings = self.merge_bindings_sets(bindings, possible_bindings)
      
      #new_bindings = list(new_bindings)
      #p('nbind', new_bindings)
      #for nbinding in new_bindings :
        #p('nbinding', nbinding, nbinding.matches_reqd_fact)
      
      if len(new_bindings) > 0 :
        bindings = new_bindings
      else :
        # in output unification reqd_facts will be False - in that
        # case, we don't care if every triple binds
        if reqd_facts != False :
          return False
    
    #p('bindings', bindings)
    
    # merge with initial_bindings after collecting bindings from the facts.  It
    # is more complex to start with the initial_bindings than to end with them
    if initial_bindings :
      bindings = self.merge_bindings_sets(bindings, [initial_bindings])
    
    # get a set of all vars used in the translation
    vars = find_vars(translation, find_string_vars = True)

    #if(translation == []) :
    #  p('t', bindings)
    
    # if there are no vars, this does still match, but there are no bindings
    if len(vars) == 0 :
      #self.debugp('len(vars)==0')
      return bindings

    #self.debugp('vars', vars)
    #for binding in bindings :
      #self.debugp('binding', binding, binding.matches_reqd_fact)
    
    # keep only the bindings which contain bindings for all of the vars and 
    # match a reqd_triple.  In output unification reqd_facts is False and we 
    # only need partial bindings so this step isn't necessary
    if reqd_facts != False:
      bindings = [binding for binding in bindings
                  if len(binding) == len(vars) and binding.matches_reqd_fact]
    
    # if there are no bindings, failed to find a match
    if len(bindings) == 0 :
      #self.debugp('len(bindings)==0')
      return False
    
    #self.debugp('matches', matches, bindings)
    return bindings

  #############################################################################
  # testtranslation and next_steps

  def testtranslation(self, translation, query, reqd_triples) :
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
    # right now, this is also a required step because this is the only way that
    # testtranslation will return False
    
    if reqd_triples and not self.partial_match_exists(translation['input'], reqd_triples) :
      return False, None
    ret = self.bind_vars(
      translation['input'], query, reqd_triples
    )
    # if a partial match did exist, but no bindings could be found, then this 
    # was a partial match
    if ret == False :
      # look for any triples that matched.  If there are any, than a partial 
      # match has been found.  Partial matches are recorded because we might
      # want to merge this partial match with another to get a full match
      matched_triples = set()
      for i, triple in enumerate(translation['input']) :
        if self.find_triple_match(triple, query) :
          matched_triples.add(i)

      return "partial", matched_triples
    else :
      return True, ret
  
  # return all triples which have at least one var in vars
  def find_specific_var_triples(self, query, vars) :
    return [triple for triple in query if any(map(lambda x:is_out_lit_var(x) and x.name in vars, triple))]

  #@logger
  def next_steps(self, orig_query, lineage, reqd_triples) :
    """
    @arg orig_query the origional query in triples set form
    @arg lineage the lineage of steps already followed
    @returns the set of next guaranteed_steps and possible_steps.
      Ensures that this set of translation and bindings haven't already been 
      searched.....
    """
    #self.debugp('orig_query', orig_query)
    guaranteed_steps = []
    
    # the translation_queue is a list of translations that will be searched.  
    # TODO if there is a lineage, translation_queue should be a 
    # combination of the tq from the end of both merged paths
    if lineage and 'new_lineage' not in lineage[-1] :
      translation_queue = self.translation_matrix[lineage[-1]['translation'].get('id')]
    else :
      translation_queue = list(self.translations)
    # NOTE setting translation_queue to all translations all the time causes
    # errors.  This is because we can go in all kinds of weird directions ...
    
    # NOTE: this is a definite hack.  The problem is that the 
    # translation_matrix can't account for situations where a variable gets
    # turned into a litvar.  That variable can be in many triples and all of
    # those triples must be used as initial pruning instead of just the output
    # triples.
    # WARNING: Here, I am only using the middle value of the triple as a test.
    # It will fail when the above situation happens and variables are used in
    # the 2nd position (property) of a triple.
    for triple in reqd_triples :
      for trans in self.translations :
        if triple[1] in [t[1] for t in trans['input']] :
          if trans not in translation_queue :
            translation_queue.append(trans)
      
    # HEURISTIC: stop DFS search at self.depth
    if lineage :
      lineage_depth = sum(s['translation']['step_size'] for s in lineage)
      self.debugp('lineage_depth', lineage_depth)
      if lineage_depth >= self.depth :
        translation_queue = []
    
    # OPTIMIZATION: skip this translation if it is the inverse of the last translation
    # WARNING: not 100% sure this is always going to work, but it does for now ...
    def test_for_inverse(translation) :
      inverse_function = lineage[-1]['translation'].get('inverse_function') 
      if inverse_function :
        if inverse_function == translation['name'] :
          return False
      return True
    if lineage :
      translation_queue = filter(test_for_inverse, translation_queue)
    
    # show the list of translations that show up in the queue
    #self.debugp('tq', [t['name'] for t in translation_queue])
    
    def merge_partial(translation, matched_triples) :
      # this function gets called if this translation was partially matched
      
      found_merge = False
      
      # all of the search paths that have partially matched this translation
      past_partials = self.partials[translation['id']]
      # NOTE: use heuristics to pick which past_partial to try first:
      #     *** keep stats about p of tip of branch1 combining with tip of 
      #         branch2 to fulfil this translation
      #     * comparing how recently the two paths diverged might correlate
      #     * prefer combined_bindings_set with more litvars
      # TODO: n-way merges instead of just 2-way merges ... ouch!
      #self.debugp('past_partials', len(past_partials))
      for past_lineage, past_query, past_matched_triples in past_partials :
        # make sure that the triples that these two partials atleast cover
        # all input triples
        if len(past_matched_triples.union(matched_triples)) == len(translation['input']) :
          # OPTIMIZATION make sure that past_query isn't a subset of orig_query
          # NOTE: might be faster to compare lineages instead of queries
          if all(triple in orig_query for triple in past_query) :
            continue
          
          # merge past_query and orig_query:
          # as we merge past_query and orig_query, if a litvar and a var bind,
          # keep the litvar, it has a known computation, where the var does not
          # NOTE: there may be problems binding litvars to other litvars.  The
          # two could have different values, but we won't know until runtime.
          merged_bindings_set = self.bind_vars(
            orig_query, past_query, False, {}, prefer_litvars = True
          )
          
          # all the ways orig_query and past_query can be merged
          for merged_bindings in merged_bindings_set :
            # see if any variables are mapped to twice ... this may be a big hack
            if len(merged_bindings.values()) != len(set(merged_bindings.values())) :
              continue
            
            new_query, new_triples = sub_var_bindings_track_changes(
              orig_query + past_query, merged_bindings
            )
            
            new_query = remove_duplicate_triples(new_query)
            
            # test to see if this new merged query has enough information to
            # trigger this translation
            ret, more = self.testtranslation(translation, new_query, new_triples)
            if ret == True :
              found_merge = True
              self.debug_open_block('merge for ' + translation['name'])
              self.debugp('orig_query', orig_query)
              self.debugp('past_query', past_query)
              self.debugp('merged_bindings_set', merged_bindings_set)
              yield new_query, translation, more, past_lineage
              self.debug_close_block()
      
      # add this instance to past partials
      #p('storing partial', translation['name'], matched_triples)
      self.partials[translation['id']].append((lineage, orig_query, matched_triples))
    
    def test_and_merge() :
      """ test each translation against the current query.  If there is a 
      partial match, also yield all possible merges """
      for translation in translation_queue :
        #self.debug('testing ' + translation['name'])
        ret, more = self.testtranslation(translation, orig_query, reqd_triples)
        if ret == "partial" :
          # in this case more is a list of the triples that matched
          for x in merge_partial(translation, more) :
            yield x
        elif ret == False :
          continue 
        else :
          # in this case more is a bindings_set
          yield orig_query, translation, more, False
    
    # main loop
    for query, translation, bindings_set, new_lineage in test_and_merge() :
      # the 2nd value from testtranslation is bindings_set if we've gotten here
      
      # we've found a match, now we just need to find the bindings.  This is
      # the step where we unify the new information (generated by output 
      # triples) with existing information.
      #self.debugp('found match ' + translation['name'])
      #p('translation['name']', translation['name'])
      for bindings in bindings_set :
        # input_bindings map from translation space to query space
        input_bindings = bindings
        # output_bindings map from translation space to query space
        output_bindings = {}
        
        input_bindings_vars = [var for (var, binding) in input_bindings.iteritems() if not is_var(binding)]
        missing_vars = translation['in_lit_vars'] - set(input_bindings_vars)
        if len(missing_vars) :
          continue
        
        # initial_bindings are the bindings that we already know from the 
        # input unification that must also hold true for output unification
        # some of the initial_binding vars don't appear in the output triples
        # so we can get rid of them
        if not translation['output'] :
          output_triple_vars = translation['constant_vars']
        else :
          output_triple_vars = find_vars(translation['output'], find_string_vars = True)
        output_triples = translation['output']
        #self.debugp('constant_vars', translation['constant_vars'])
        initial_bindings = dict(
          (unicode(name), bindings[name]) for name in translation['constant_vars']
            if name in bindings and 
              name in output_triple_vars
        )
        
        # used in a couple places later on
        output_lit_vars = find_vars(translation['output'], is_lit_var).union(
          set(translation.get('output_vars', [])))
        #self.debugp('input_bindings', input_bindings)
        #self.debugp('initial_bindings', initial_bindings)
        
        # if the translation has an input_function, run it here to see if these
        # input_bindings pass the test
        if 'input_function' in translation :
          if not translation['input_function'](input_bindings) :
            continue
        
        # unify output_triples with query
        if not translation['output'] :
          # if there is not output, simply replace input vars with litvars
          # since after the translation is applied they will have values
          output_bindings_set = [
            {unicode(name) : LitVar(input_bindings[name].name)}
            for name in translation['output_vars']]
        else :
          output_bindings_set = self.bind_vars(output_triples, query, False, initial_bindings = initial_bindings)
        # if no unification is found, just use the initial_bindings
        if output_bindings_set == False :
          output_bindings_set = [initial_bindings]
        
        for output_bindings in output_bindings_set :
          # if var is a lit var in the output_triples, then its output bindings
          # must bind it to a new variable since it will be computed and set by
          # the translation function and may not have the same value any more
          # WARNING: I think this means that bind_vars might not do the 
          # right thing if it thinks that it can bind whatever it wants to 
          # lit_vars.  lit_vars for example shouldn't bind to literal values
          # this might also have to do with a schema, some things can be bound
          # again (a.is), whereas some can not (u.inches)
          
          #self.debugp('output_bindings', output_bindings)
          
          # if get_bindings found variable to variable matches, we will need
          # to alter the triples in the existing query (not just add triples)
          # unified_bindings maps old query variables to new query variables
          unified_bindings = {}
          for var in output_lit_vars :
            new_lit_var = LitVar(var+'_out_'+str(self.next_num()))
            if var in output_bindings :
              if is_any_var(output_bindings[var]) :
                if not is_out_lit_var(output_bindings[var]) :
                  unified_bindings[output_bindings[var].name] = new_lit_var
            output_bindings[var] = new_lit_var
          
          #self.debugp('unified_bindings', unified_bindings)
          #self.debugp('output_bindings', output_bindings)
          
          # make sure all vanila vars have unique names
          for var in find_vars(translation['output'], is_var) :
            if var not in output_bindings :
              output_bindings[var] = Var(var+'_'+str(self.next_num()))
          
          # generate the new query by adding the output triples with 
          # output bindings substituted in
          new_triples = sub_var_bindings(translation['output'], output_bindings)

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
          output_bindings = dict(
            (var, binding) for var, binding in output_bindings.iteritems()
            if var in output_lit_vars or
              var in translation['constant_vars']
          )
          
          new_query = remove_duplicate_triples(new_query)
          
          #self.debugp('new_triples', new_triples)
          #self.debugp('new_query', new_query)
          #self.debugp('input_bindings', input_bindings)
          #self.debugp('output_bindings', output_bindings)
          
          step = {
            'input_bindings' : input_bindings,
            'output_bindings' : output_bindings,
            'translation' : translation,
            'new_triples' : new_triples,
            'new_query' : new_query,
          }
          if new_lineage :
            step['new_lineage'] = new_lineage
          #p('step', step)
          yield step
  
  ##############################################################################
  # find solution
  
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
          if tv.name == qv.name :
            return {tv : qv}
        return False
      elif is_out_lit_var(qv) :
        # This happens when a query is looking for a literal variable and a 
        # translation is willing to provide a variable, just not a literal one.
        # (see lastfm similar artist output variable similar_artist) and a query
        # wanting it to be literal
        return False
      elif is_lit_var(tv) and is_lit_var(qv) :
        return True
      elif is_any_var(qv) :
        return tv.name == qv.name
      return False
    else :
      return tv == qv
  
  def find_solution_triples_match(self, triple, qtriple) :
    """
    does the pattern in triple match the qtriple?
    """
    bindings = {}
    for tv, qv in izip(triple, qtriple) :
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
  
  def find_partial_solution(self, var_triples, facts) :
    """
    returns a list of triples from var_triples which have matches in facts
    """
    bindings = {}
    for triple in var_triples :
      new_bindings, ftriple = self.find_solution_triple(triple, facts)
      if new_bindings :
        if new_bindings == True :
          pass
        else :
          bindings.update(new_bindings)
    
    # make bindings just to the variable name not the full URI (if the value of
    # the binding is a varialbe, make sure it is in the n.var namespace)
    # at one point, just the variable name was used, but sometimes the compiler
    # can actually find hard values for the bindings (no evaluation required)
    # and so we must use a full uri
    def normalize(value) :
      if is_any_var(value) :
        return Var(value.name)
      else :
        return value
    bindings = dict([(var.name, normalize(value)) for var, value in bindings.iteritems()])
    return bindings
  
  def found_solution(self, new_query) :
    # NOTE: it is quite possible that the output unification step has enough 
    # information to know if a solution has been found too, which could make
    # this step unecessary.
    
    # var_triples are the triples which contain the variables which we are 
    # looking to bind
    var_triples = self.find_specific_var_triples(new_query, self.reqd_bound_vars)
    initial_bindings = dict((var, Var(var)) for var in find_vars(var_triples, lambda x:is_var(x) or is_lit_var(x)))
    
    # see if the triples which contain the variables can bind to any of the 
    # other triples in the query
    bindings_set = self.bind_vars(var_triples, new_query, False, initial_bindings = initial_bindings)
    if bindings_set != False :
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
          return dict((Var(name), v) for name, v in bindings.iteritems())
    
    return False

  #############################################################################
  # SEARCH
  
  def remove_steps_already_taken(self, steps, lineage) :
    """ remove any steps that we've already taken """
    def eq(s1, s2) :
      """ True iff step1 and step2 are equal """
      return ((s1['translation']['id'] == s2['translation']['id'])
                and
              (s1['input_bindings'] == s2['input_bindings']))
    
    for step in steps :
      # if we've already made this translation once before, skip it
      if any(eq(step, lstep) for lstep in lineage) :
        continue
      
      yield step
  
  def log_root(fn) :
    def log_root_wrapper(self, *args, **kwargs) :
      if 'root' in kwargs and kwargs['root'] :
        self.debug_open_block('search')
        ret = fn(self, *args, **kwargs)
        self.debug_close_block()
        return ret
      else :
        return fn(self,  *args, **kwargs)
    return log_root_wrapper
  
  @log_root
  def search(self, query, new_triples, lineage = [], root = False) :
    """
    follow guaranteed translations and add possible translations to the 
      possible_stack
    this is somewhat of an evaluator ...
    @arg query is the query to start from
    @new_triples is a set of triples which are new as of the previous 
      translation.  This next translation must take them into account.  If they
      are not needed, then an earlier step could have gotten there already and
      the most recent step was unnecessary
    @lineage is a list of the steps we've taken to get here
    @return the compiled guaranteed path
    """
    
    self.debugp('query', query)
    
    # find the possible next steps
    steps = self.next_steps(query, lineage, new_triples)
    
    # remove any steps we've already taken
    steps = self.remove_steps_already_taken(steps, lineage)
    
    if self.show_dead_ends :
      steps = list(steps)
      if not steps :
        p('dead_end', query)
        p('lineage', [step['translation']['name'] for step in lineage])
        p()
    
    #steps = list(steps)
    #self.debug_open_block('steps')
    #self.debugp(steps)
    #self.debug_close_block()
    
    # look through all steps recursively to see if they result in a 
    # solution and should be added to the compile_node, the finished 'program'
    for step in steps :
      self.debug_open_block((step['translation']['name'] or '<unnamed>') + ' ' + color(hash(step['input_bindings'], step['output_bindings'])) + ' ' + prettyquery(step['input_bindings']) + str(time.time() - self.start_time))
      
      # add this step to the lineage, but before that, add any new steps that
      # were injected by the step itself (in the case of a merged path)
      new_lineage = copy.copy(lineage)
      if 'new_lineage' in step :
        for s in step['new_lineage'] :
          if s not in lineage :
            new_lineage.append(s)
      new_lineage += [step]
      
      # if the new information at this point is enough to fulfil the query, done
      # otherwise, recursively continue searching.
      # found_solution is filled with the bindings which bind out_lit_vars from 
      # the query to literal values (strings, numbers, uris, etc)
      # TODO: found_solution might be able to return enough information to 
      # completely remove the partial solution step at the end of compilation
      found_solution = self.found_solution(step['new_query'])
      if found_solution :
        self.debugp('last_step', step)
        self.debugp('input', step['translation']['input'])
        self.debugp('output', step['translation']['output'])
        self.debug_close_block()
        return new_lineage
      else :
        # recur
        ret = self.search(step['new_query'], step['new_triples'], new_lineage)
        self.debug_close_block()
        if ret :
          return ret
  
  ##############################################################################
  # compile
  
  def make_vars_out_vars(self, query, reqd_bound_vars) :
    """
    replaces all instances of variables in query whose name is in the 
    reqd_bound_vars list with self.n.out_lit_var variables of the same name
    @arg query is a query to change
    @arg reqd_bound_vars is a list which the function will change
    """
    for triple in query :
      for j, value in enumerate(triple) :
        if is_lit_var(value) and value.name in reqd_bound_vars :
          triple[j] = OutLitVar(value.name)
        elif is_any_var(value) and value.name in reqd_bound_vars :
          triple[j] = OutVar(value.name)
  
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
  
  def compile(self, query, reqd_bound_vars, input = [], output = []) :
    self.debug_reset()
    self.start_time = time.time()
    
    if isinstance(query, basestring) :
      query = [line.strip() for line in query.split('\n')]
      query = [line for line in query if line is not ""]
    query = self.parser.parse(query)
    
    query, modifiers = self.extract_query_modifiers(query)
    
    # TODO: change axpress to parse _vars as outlitvars in the first place
    # this replaces all litvars with outlitvars in query
    # that said, this isn't a costly function in the grand scheme of things
    # replaces all vars in reqd_bound_vars not already litvars with outvars ...
    self.make_vars_out_vars(query, reqd_bound_vars)
    
    #p('query',query)
    
    self.reqd_bound_vars = reqd_bound_vars
    var_triples = self.find_specific_var_triples(query, reqd_bound_vars)
    if var_triples == [] :
      raise Exception("Waring, required bound triples were provided, but not found in the query")
    
    # an iterative deepening search
    self.depth = 6
    steps = None
    max_depth = 12
    while not steps and self.depth < max_depth:
      self.debugp("depth: %d" % self.depth)
      #self.show_dead_end = self.show_dead_ends and self.depth == max_depth - 1
      self.show_dead_ends = False
      self.partials = defaultdict(list)
      steps = self.search(query, query, lineage = [], root = True)
      self.depth += 1
    
    # if there were no paths through the search space we are done here
    if not steps :
      return False

    #p('steps', steps)
    
    """
    at one point, steps was allowed to return many paths through the 
    translation space and the rest of this code would make sure that the 
    interleaving paths didn't wind up causing translations to be run twice
    or run when they were not necessary, etc.  With DFS, this is no longer an
    issue, and we have moved away from attempting to run every guaranteed path
    and instead run just one of them, or the first few.  I've prooven that 
    finding all paths is much more difficult because there are many ways which
    translations can be combined into infite loops that are hard to detect
    """
    #p('steps', [(id(s), s['translation']['name']) for s in steps])
    
    solution_bindings_set = {}
    for step in steps :
      step['input_bindings'] = dict([(var, binding) for (var, binding) in step['input_bindings'].iteritems() if not is_var(binding)])
      
      step['output_bindings'] = dict([(var, binding) for (var, binding) in step['output_bindings'].iteritems() if not is_var(binding)])
      
      # figure out if any parts of the output of this step satisfy part of 
      # the solution
      var_triples = self.find_specific_var_triples(step['new_query'], self.reqd_bound_vars)
      partial_bindings = self.find_partial_solution(
        var_triples, step['new_query']
      )

      # keep track of which variables will end up holding the solution
      solution_bindings_set.update(partial_bindings)
      
      # get rid of extra stuff in steps
      del step['new_query']
      del step['new_triples']
      if 'new_lineage' in step :
        del step['new_lineage']

    ret = {
      'combinations' : [[{
        'depends' : steps[:-1],
        'step' : steps[-1]
      }]],
      'modifiers' : modifiers,
      'solution_bindings_set' : [solution_bindings_set],
    }
    #p('ret', ret)
    return ret
