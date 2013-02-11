# -*- coding: utf-8 -*-
from Utils import var_name, is_any_var, is_var, is_lit_var, explode_bindings_set, debug, p, logger, new_explode_bindings_set
from PrettyQuery import prettyquery

import copy
from itertools import izip

class Evaluator :
  """
  evaluates 'programs' compiled by the compiler
  """
  def __init__(self, n = None) :
    if n :
      self.n = n
    else :
      self.n = Namespaces()

  def each_binding_set(self, bindings_set) :
    """
    iterate bindings_set as if it were just a list, even if it is just a single
    thing or a list of lists.
    """
    for item in bindings_set :
      if isinstance(item, list) :
        for sub_item in self.each_binding_set(item) :
          yield sub_item
      else :
        yield item
  
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
    
  def evaluate_step_function(self, step, input_bindings_set) :
    # NOTE that if ret == [] aka. the input binding set is no longer valid
    # we want that to be added to the ret, not the input bindings
    
    #p('input_bindings_set', input_bindings_set)
    if 'function' in step['translation'] :
      result_bindings_set = []
      for input_bindings in input_bindings_set :
        ret = step['translation']['function'](input_bindings)
        if ret != None:
          result_bindings_set.append(ret)
        else :
          result_bindings_set.append(input_bindings)
      return result_bindings_set
    elif 'multi_function' in step['translation'] :
      # a multi_function takes in the entire input_bindings_set and returns
      # an entire new one, rather than the normal function which is fed one
      # at a time (and can return any number of results)
      ret = step['translation']['multi_function'](input_bindings_set)
      if ret != None :
        return ret
      else :
        input_bindings_set
    else :
      raise Exception("translation doesn't have a function ...")
  
  def evaluate_step_with_bindings_set(self, step, incoming_bindings_set) :
    #p()
    #p('incoming_bindings_set', incoming_bindings_set)
    #p('name', step['translation']['name'])
    #p('input_bindings', step['input_bindings'])
    #p('output_bindings', step['output_bindings'])
    incoming_bindings_set = self.flatten(incoming_bindings_set)

    input_bindings  = step['input_bindings']
    output_bindings = step['output_bindings']
    
    # substitute any values in the incoming bindings into the input_bindings
    input_bindings_set = []
    for incoming_bindings in incoming_bindings_set :
      new_input_bindings = {}
      for var, value in input_bindings.iteritems() :
        if is_any_var(value) and value.name in incoming_bindings :
          new_input_bindings[var] = incoming_bindings[value.name]
        else :
          new_input_bindings[var] = input_bindings[var]
      input_bindings_set.append(new_input_bindings)
    
    result_bindings_set = self.evaluate_step_function(step, input_bindings_set)
    #self.ensure_result_bindings_set_is_complete(result_bindings_set)
    
    #p('result_bindings_set',result_bindings_set)
    #p('incoming_bindings_set', incoming_bindings_set)
    #p()
    output_bindings_set = []
    # WARNING: this only really makes sense on functions, not multi_functions
    for result_bindings, incoming_bindings in izip(result_bindings_set, incoming_bindings_set) :
      # bind the values resulting from the function call
      # the translation might return a bindings_set so deal with that case
      if isinstance(result_bindings, list) :
        result_bindings_set = result_bindings
        if not all(isinstance(b, dict) for b in result_bindings) :
          raise Exception("output of %s was a list of something other than dicts" % step['translation']['name'])
      else :
        result_bindings_set = [result_bindings]

      new_bindings_set = []
      for result_bindings in result_bindings_set :
        #p('result_bindings',result_bindings)
        new_bindings = copy.copy(incoming_bindings)
        for var, value in result_bindings.iteritems() :
          if var in output_bindings :
            if is_any_var(output_bindings[var]) :
              new_bindings[output_bindings[var].name] = value
            else :
              assert output_bindings[var] == value
              new_bindings[var] = value
              #print 'hmm should I do something?',var, output_bindings[var],value
        
        # check to make sure everything was bound that was supposed to be
        # could be removed for tiny speed increase, but helps with debuging
        if len(new_bindings) != len(output_bindings) :
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
        
        #p('new_bindings', new_bindings)
        new_bindings_set.append(new_bindings)
      
      #p('new_bindings_set',new_bindings_set)
      new_exploded_bindings_set = []
      for new_bindings in new_bindings_set :
        new_exploded_bindings_set.extend(
          new_explode_bindings_set(new_bindings)
        )

      output_bindings_set.extend(new_exploded_bindings_set)
    
    return self.flatten(output_bindings_set)

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
    
    if len(bindings_set1) == 1 or len(bindings_set2) == 1:
      cp = lambda x:x      
    else :
      cp = copy.copy
    
    # ensure that if one of these sets has more than 1 binding, that set is in
    # bindings_set1.  Otherwise, ret will be filled with many exact copies of
    # the same dict.
    if len(bindings_set1) == 1 and len(bindings_set2) != 1:
      bindings_set1, bindings_set2 = bindings_set2, bindings_set1
    
    ret = []
    for b1 in bindings_set1 :
      for b2 in bindings_set2 :
        b1 = cp(b1)
        b1.update(b2)
        ret.append(b1)
    
    return ret
  
  def evaluate(self, compiled, incoming_bindings_set = [{}]) :
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
      for bindings in self.each_binding_set(combination_bindings_set) :
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











