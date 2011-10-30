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
		new_l = []
		for i in l :
			if isinstance(i, list) :
				new_l += self.flatten(i)
			else :
				new_l.append(i)
		return new_l
	
	def evaluate_step_with_bindings(self, step, incoming_bindings_set) :
		#p('incoming_bindings_set', incoming_bindings_set)
		
		input_bindings_set = []
		for incoming_bindings in incoming_bindings_set :
			if not isinstance(incoming_bindings, dict) :
				print type(incoming_bindings), incoming_bindings
			input_bindings = step['input_bindings']
			output_bindings = step['output_bindings']
			
			#p('step name', step['translation'][self.n.meta.name])
			#p('input_bindings',input_bindings)
			#p('output_bindings',output_bindings)
			#p('incoming_bindings',incoming_bindings)
			
			# substitute any values in the incoming bindings into the input_bindings
			new_input_bindings = {}
			for var, value in input_bindings.iteritems() :
				if is_any_var(value) and var_name(value) in incoming_bindings :
					new_input_bindings[var] = incoming_bindings[var_name(value)]
				else :
					new_input_bindings[var] = input_bindings[var]
			input_bindings = new_input_bindings
			
			#p('new_input_bindings',input_bindings)
			input_bindings_set.append(input_bindings)
		
		result_bindings_set = []
		for input_bindings in input_bindings_set :
			ret = step['translation'][self.n.meta.function](input_bindings)
			if ret is not None:
				result_bindings_set.append(ret)
			else :
				result_bindings_set.append(input_bindings)
		
		#p('result_bindings_set',result_bindings_set)
		output_bindings_set = []
		for result_bindings, incoming_bindings in zip(result_bindings_set, incoming_bindings_set) :
			# bind the values resulting from the function call
			# the translation might return a bindings_set so deal with that case
			# list_later surrounds the return value with an extra list to represent that
			# it has been exploded
			list_later = False
			if isinstance(result_bindings, list) :
				list_later = True
				result_bindings_set = result_bindings
			else :
				result_bindings_set = [result_bindings]
			new_bindings_set = []
			for result_bindings in result_bindings_set :
				#p('result_bindings',result_bindings)
				new_bindings = copy.copy(incoming_bindings)
				for var, value in result_bindings.iteritems() :
					if var in output_bindings :
						if is_any_var(output_bindings[var]) :
							new_bindings[var_name(output_bindings[var])] = value
						else :
							assert output_bindings[var] == value
							new_bindings[var] = value
							#print 'hmm should I do something?',var, output_bindings[var],value
				
				#check to make sure everything was bound that was supposed to be
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
								), step['translation'][self.n.meta.name]
							)
						)
				
				new_bindings_set.append(new_bindings)
			
			#p('new_bindings_set',new_bindings_set)
			new_exploded_bindings_set = []
			for new_bindings in new_bindings_set :
				new_exploded_bindings_set.extend(new_explode_bindings_set(new_bindings))
			#if len(new_exploded_bindings_set) > 1 :
				#new_exploded_bindings_set = [new_exploded_bindings_set]
			if list_later :
				new_exploded_bindings_set = [new_exploded_bindings_set]
			
			#p('new_exploded_bindings_set',new_exploded_bindings_set)
			#return new_exploded_bindings_set
			output_bindings_set.extend(new_exploded_bindings_set)
		
		return output_bindings_set

	#@logger
	def evaluate_step_with_bindings_set(self, step, incoming_bindings_set) :
		"""
		There was some confusion when I was porting this to allow trasnlation
		functions to take all the bindings at once.
		
		The confusion arises from the distinction between a list of possibilities
		which can happen together:
		translation 1 returns: [{x:1}, {x:2}]
		translation 2 returns; [{y:1}, {y:2}]
		 
		could mean all 4 combinations are possible, or that x1 and x2 can both 
		happen but not simultaneously
		"""
		#p('evaluating',step['translation'][n.meta.name])
		#p('incoming_bindings_set',incoming_bindings_set)
		#new_bindings_set = []
		#for incoming_bindings in incoming_bindings_set :
			#if isinstance(incoming_bindings, list) :
				#new_bindings_set.append(self.evaluate_step_with_bindings_set(step, incoming_bindings))
			#else :
				#new_bindings_set.extend(self.evaluate_step_with_bindings(step, incoming_bindings))
		
		islist = False
		if isinstance(incoming_bindings_set, list) :
			if incoming_bindings_set and isinstance(incoming_bindings_set[0], list) :
				incoming_bindings_set = incoming_bindings_set[0]
				islist = True
		
		new_bindings_set = self.evaluate_step_with_bindings(step, incoming_bindings_set)
		
		if islist :
			new_bindings_set = [new_bindings_set]
		
		if new_bindings_set == [{}] :
			new_bindings_set = []
		
		#p('new_bindings_set',new_bindings_set)
		return new_bindings_set
	
	#@logger
	def permute_bindings(self, final_bindings_set, new_bindings_set) :
		"""
		final_bindings_set is a set (or not) of bindings
			it can either be a set of a set of a set of ... bindings, or bindings
		new_bindings_set is a set (or not) of bindings
			it can either be a set of a set of a set of ... bindings, or bindings
		both final_bindings_set and new_bindings_set are altered in the process
		@returns all valid combinations of the two 'sets'
		"""
		#p('xxx final_bindings_set',final_bindings_set)
		#p('xxx new_bindings_set',new_bindings_set)
		if isinstance(final_bindings_set, dict) :
			if isinstance(new_bindings_set, dict) :
				#p('fd nd')
				final_bindings_set.update(new_bindings_set)
				return final_bindings_set
			else : # new_bindings_set is a list
				#p('fd nl')
				for new_bindings in self.each_binding_set(new_bindings_set) :
					new_bindings.update(final_bindings_set)
				return new_bindings_set
		else : # final_bindings_set is a list
			if isinstance(new_bindings_set, dict) :
				#p('fl nd')
				for final_bindings in self.each_binding_set(final_bindings_set) :
					final_bindings.update(new_bindings_set)
				return final_bindings_set
			else : # both final_bindings_set and new_bindings_set are lists:
				#p('fl nl')
				return [self.permute_bindings(final_bindings, new_bindings) for final_bindings, new_bindings in izip(final_bindings_set, new_bindings_set)]
	
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
			#p('len(combination)',len(combination))
			#p('combination',combination.keys())
			combination_bindings_set = [{}]
			for translation in combination :
				bindings_set = copy.copy(incoming_bindings_set)
				#p('translation',translation['step']['translation'][n.meta.name])
				# make sure that all of the dependency translations have been evaluated
				for dependency in translation['depends'] :
					#p('dependency',dependency['translation'][n.meta.name])
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
			#p('solution_bindings',solution_bindings)
			for bindings in self.each_binding_set(combination_bindings_set) :
				solution = {}
				for var, binding in solution_bindings.iteritems() :
					if is_var(binding) :
						solution[var] = bindings[var_name(binding)]
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











