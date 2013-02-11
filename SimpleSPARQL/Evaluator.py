# -*- coding: utf-8 -*-
from Utils import var_name, is_any_var, is_var, is_lit_var, explode_bindings_set, debug, p, logger, explode_bindings_set
from PrettyQuery import prettyquery

import copy
from itertools import izip

def unique_copy(o) :
  """ generate an infinite stream of o's where the first item is o and
  the rest are copies"""
  yield o
  while True :
    yield copy.copy(o)

class Evaluator :
  """
  evaluates 'programs' compiled by the compiler
  """
  def __init__(self, n = None) :
    if n :
      self.n = n
    else :
      self.n = Namespaces()
    self.warnings = True

  def flatten(self, l) :
    if isinstance(l, list) :
      new_l = []
      for i in l :
        if isinstance(i, list) :
          new_l += self.flatten(i)
        else :
          new_l.append(i)
      return new_l
    else :
      return [l]
    
  def evaluate_step_function(self, step, t_in_bs) :
    # NOTE that if ret == [] aka. the input binding set is no longer valid
    # we want that to be added to the ret, not the input bindings
    
    #p('t_in_bs', t_in_bs)
    if 'function' in step['translation'] :
      t_out_bs = []
      for t_in_b in t_in_bs :
        t_out_b = step['translation']['function'](t_in_b)
        if t_out_b != None:
          # test for invalid output
          if isinstance(t_out_b, list) :
            if not all(isinstance(b, dict) for b in t_out_b) :
              raise Exception("output of %s was a list of something other"
                              "than dicts" % step['translation']['name'])

          t_out_bs.append(t_out_b)
        else :
          t_out_bs.append(t_in_b)
      return t_out_bs
    elif 'multi_function' in step['translation'] :
      # a multi_function takes in the entire t_in_bs and returns
      # an entire new one, rather than the normal function which is fed one
      # at a time (and can return any number of results)
      t_out_bs = step['translation']['multi_function'](t_in_bs)
      if t_out_bs == None :
        t_out_bs = t_in_bs
      
      return t_out_bs
    else :
      raise Exception("translation doesn't have a function ...")
  
  def check_for_missing_variables(self, result_bindings, output_bindings,
                                  step):
    # check to make sure everything was bound that was supposed to be
    # could be removed for tiny speed increase, but helps with debuging
    missing_variables = set(output_bindings) - set(result_bindings)
    if missing_variables :
      if len(missing_variables) > 1 :
        variables = "variables"
      else :
        variables = "variable"
      raise ValueError(
        "%s %s didn't get bound by translation '%s'" % (
          variables, ', '.join(
            "'"+v+"'" for v in missing_variables
          ), step['translation']['name']
        )
      )

  def map_q_to_t(self, q_in_bs, t_to_q_in_b) :
    """
    given bindings set in query space, and translation->query mapping,
    return bindings in translation_space
    """
    
    t_in_bs = []
    for q_in_b in q_in_bs :
      t_in_b = {}
      for var, value in t_to_q_in_b.iteritems() :
        if is_any_var(value) and value.name in q_in_b :
          t_in_b[var] = q_in_b[value.name]
        else :
          t_in_b[var] = t_to_q_in_b[var]
      t_in_bs.append(t_in_b)
    return t_in_bs

  def map_t_to_q(self, t_out_b, t_to_q_out_b, t_in_b={}) :
    """
    given a bindings in translation space, and a translation->query mapping,
    return bindings in query space
    
    NOTE: t_in_b is only for generating warnings when a variable is in
    t_out_b but there is no bindings
    """
    
    q_out_b = {}
    for var, value in t_out_b.iteritems() :
      if var in t_to_q_out_b :
        if is_any_var(t_to_q_out_b[var]) :
          q_out_b[t_to_q_out_b[var].name] = value
        else :
          assert t_to_q_out_b[var] == value
          q_out_b[var] = value
      else :
        # should there be a way to turn this off?
        if self.warnings :
          if var not in t_in_b :
            print 'warning: unused result', var
    return q_out_b

  def evaluate_step_with_bindings_set(self, step, q_in_bs) :
    """
    !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    !! the trick here I think is that I am trying to reuse code between
    !! function and multifunction cases that aren't the same.  Its hard to
    !! make the code more complex and repetitive at this point, but I think
    !! there are bugs in the code as it is now due to its false simplicity
    !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    """
    # descriptions of variables
    # q_in_bs      : query space to value
    # t_to_q_in_b  : translation to query space
    # t_in_bs      : translation space to value
    # t_out_bs     : translation space to value
    # t_to_q_out_b : translation to query space
    # q_out_bs     : query space to value
    
    # TODO: shouldn't need flatten
    q_in_bs = self.flatten(q_in_bs)

    t_to_q_in_b  = step['input_bindings']
    t_to_q_out_b = step['output_bindings']
    
    t_in_bs = self.map_q_to_t(q_in_bs, t_to_q_in_b)
    t_out_bs = self.evaluate_step_function(step, t_in_bs)

    for t_out_b in t_out_bs :
      for t_out_b in self.flatten(t_out_b) :
        self.check_for_missing_variables(t_out_b, t_to_q_out_b, step)      

    if 'function' in step['translation'] :
      q_out_bs = []
      for t_out_b, q_in_b, t_in_b in izip(t_out_bs, q_in_bs, t_in_bs) :
        # bind the values resulting from the function call
        # the translation might return a bindings_set so deal with that case
        for t_out_b in self.flatten(t_out_b) :
          q_out_b = copy.copy(q_in_b)
          q_out_b.update(self.map_t_to_q(t_out_b, t_to_q_out_b, t_in_b))
          q_out_bs.append(q_out_b)
    if 'multi_function' in step['translation'] :
      q_out_bs = [self.map_t_to_q(t_out_b, t_to_q_out_b)
                  for t_out_b in t_out_bs]

    # handle values which are lists, which were really short hand for many
    # possibilities (see glob.glob)
    q_out_bs = explode_bindings_set(q_out_bs)

    return q_out_bs

  def non_empty(self, b_set) :
    for b in b_set :
      if b :
        return True
    return False

  def permute_bindings(self, bindings_set1, bindings_set2) :
    """
    both final_bindings_set and new_bindings_set are altered in the process
    @returns all valid combinations of the two 'sets'
    """

    bindings_set1 = self.flatten(bindings_set1)
    bindings_set2 = self.flatten(bindings_set2)
    
    #if len(bindings_set1) == 1 or len(bindings_set2) == 1:
    #  cp = lambda x:x      
    #else :
    #  cp = copy.copy
    
    # ensure that if one of these sets has more than 1 binding, that set is in
    # bindings_set1.  Otherwise, ret will be filled with many exact copies of
    # the same dict.
    if len(bindings_set1) == 1 and len(bindings_set2) != 1:
      bindings_set1, bindings_set2 = bindings_set2, bindings_set1
    
    ret = []
    for b1 in bindings_set1 :
      for b1, b2 in izip(unique_copy(b1), bindings_set2) :
        b1.update(b2)
        ret.append(b1)
    
    return ret
  
  def evaluate(self, compiled, incoming_bindings_set = [{}]) :
    # TODO: update with new bindings_set names
    # TODO: general cleanup
    n = self.n
    
    modifiers = {}
    if 'limit' in compiled['modifiers'] :
      modifiers['limit'] = compiled['modifiers']['limit']
    else :
      # TODO: be more smarter
      modifiers['limit'] = 99999999
    
    #p('compiled',compiled)
    
    #p()
    #p('incoming_bindings_set',incoming_bindings_set)
    #p()
    #p('number of combinations',len(compiled['combinations']))
    final_bindings_set = []
    for combination, solution_bindings in izip(compiled['combinations'], compiled['solution_bindings_set']) :
      #p('combination',combination.keys())
      combination_bindings_set = [{}]
      for translation in combination :
        bindings_set = copy.copy(incoming_bindings_set)
        #p('translation',translation['step']['translation']['name'])
        # make sure that all of the dependency translations have been evaluated
        for dependency in translation['depends'] :
          #p('dependency',dependency['translation']['name'])
          if 'output_bindings_set' in dependency :
            #p('depenency already met')
            bindings_set = dependency['output_bindings_set']
          else :
            bindings_set = self.evaluate_step_with_bindings_set(dependency, bindings_set)
            #p('bindings_set',bindings_set)
            dependency['output_bindings_set'] = bindings_set
        # evaluate self (this has not been evaluated because nothing depends on it)
        #p('translation',translation.keys())
        bindings_set = self.evaluate_step_with_bindings_set(translation['step'], bindings_set)
        #p('bindings_set',bindings_set)
      
        # make all possible merges between combination_bindings_set and the new bindings_set
        #p('combination_bindings_set before',combination_bindings_set)
        combination_bindings_set = self.permute_bindings(combination_bindings_set, bindings_set)
        #p('combination_bindings_set after',combination_bindings_set)
        #p('translation[partial_bindings]',translation['step']['partial_bindings'])
      
      #p('combination_bindings_set',combination_bindings_set)
      #p('len(combination)',len(combination))
      #p('solution_bindings',solution_bindings)
      for bindings in combination_bindings_set :
        solution = {}
        for var, binding in solution_bindings.iteritems() :
          if is_var(binding) :
            solution[var] = bindings[binding.name]
          else :
            solution[var] = binding
          #if is_var(binding) :
            #solution[var_name(var)] = binding
          #else :
            #solution[var_name(var)] = incoming_bindings[var_name(binding)]
        final_bindings_set.append(solution)
    
    # TODO: only actually evalute 'limit' #, instead of only returning that many
    if len(final_bindings_set) > modifiers['limit'] :
      return final_bindings_set[:modifiers['limit']]
    else :
      return final_bindings_set
    #return self.evaluate_helper(compiled['combinations'], incoming_bindings_set, modifiers)











