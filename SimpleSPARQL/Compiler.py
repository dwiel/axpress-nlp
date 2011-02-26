# -*- coding: utf-8 -*-
from SimpleSPARQL import SimpleSPARQL
from Namespaces import Namespaces
from PrettyQuery import prettyquery
from Parser import Parser
from Utils import *

from Bindings import Bindings

from rdflib import URIRef

from itertools import izip
import copy, time, random

def isstr(v) :
	return isinstance(v, basestring) and not isinstance(v, URIRef)

class Compiler :
	MAYBE = 'maybe'
	
	def __init__(self, n = None, debug = False) :
		if n :
			self.n = n
		else :
			self.n = Namespaces()
		self.n.bind('out_lit_var', '<http://dwiel.net/axpress/out_lit_var/0.1/>')
		self.n.bind('out_var', '<http://dwiel.net/axpress/out_var/0.1/>')
		#self.n.bind('tvar', '<http://dwiel.net/axpress/translation/var/0.1/>')
		#self.n.bind('bnode', '<http://dwiel.net/axpress/bnode/0.1/>')
		#self.n.bind('meta', '<http://dwiel.net/axpress/meta/0.1/>')
		
		self.parser = Parser(self.n)

		self.translations = []
		#self.sparql = sparql
		self._next_num = 0
		
		self.log_debug = debug
		self.debug_reset()
	
	def debug_reset(self) :
		self.debug_str = ""
		self.debug_block_id = 0
	
	def debug(self, str) :
		self.debug_str += str + '<br>'

	def debugp(self, *args) :
		
		self.debug('<xmp>' + ' '.join([prettyquery(arg) for arg in args]) + '</xmp>')
		
	def debug_open_block(self, title) :
		self.debug_str += """
			<div class="logblock">
			<div class="logblock-title" id="block-title-%d">%s</div>
			<div class="logblock-body" style="display:none" id="block-body-%d">
		""" % (self.debug_block_id, title, self.debug_block_id)
		self.debug_block_id += 1
	
	def debug_close_block(self) :
		self.debug_str += """</div></div>"""

	def register_translation(self, translation) :
		n = self.n
		
		# make sure all of the required keys are present
		required = [n.meta.input, n.meta.output, n.meta.name]
		missing = [key for key in required if key not in translation]
		if missing :
			raise Exception('translation is missing keys: %s' % prettyquery(missing))
		
		if n.meta.function not in translation :
			translation[n.meta.function] = lambda x:x
		
		if n.meta.constant_vars not in translation :
			translation[n.meta.constant_vars] = []
		
		# parse any string expressions
		translation[n.meta.input] = self.parser.parse_query(translation[n.meta.input])
		translation[n.meta.output] = self.parser.parse_query(translation[n.meta.output])
		
		#print 'registering'
		#print translation[n.meta.name]
		#print prettyquery(translation[n.meta.input])
		#print prettyquery(translation[n.meta.output])
		#print
		
		self.translations.append(translation)
	
	def get_used_uris(self) :
		uris = []
		
		def extract_uris(triples_list) :
			for triple in triples_list :
				for v in triple :
					if isinstance(v, URIRef) and not is_any_var(v):
						uris.append(v)
		
		for translation in self.translations :
			extract_uris(translation[n.meta.input])
			extract_uris(translation[n.meta.output])
		
		return set(uris)
		
	def find_matches(self, value, qvalue) :
		import lua
		lua.require('matching')
		find_matches = lua.globals()['find_matches']
		ret = find_matches(qvalue, value)
		return ret
	
	def string_matches(self, value, qvalue) :
		import lua
		lua.require('matching')
		find_matches = lua.globals()['find_matches']
		ret = find_matches(qvalue, value)
		return ret[1] != None
	
	#@logger
	def values_match(self, value, qvalue) :
		self.debugp('values_match', value, qvalue)
		if type(value) == URIRef :
			#if is_out_var(value) or is_out_var(qvalue) :
				#print '???',prettyquery(value),prettyquery(qvalue)
			
			if is_var(value) :
				return True
			elif is_meta_var(value) :
				if type(qvalue) == URIRef :
					return is_any_var(qvalue) and not is_lit_var(qvalue)
					# return is_any_var(qvalue) and not is_meta_var(qvalue)
				else :
					return False
			elif is_lit_var(value) :
				if type(qvalue) == URIRef :
					return is_lit_var(qvalue) or not is_any_var(qvalue)
					# return qvalue.find(self.n.var) != 0 and qvalue.find(self.n.lit_var) != 0
				else :
					return True
			elif is_out_lit_var(value) :
				#print 'does this happen?',prettyquery(value),prettyquery(qvalue)
				self.debugp('out_lit_var', value, qvalue)
				# not often ... probably only in the if matches(q,v) or (v,q) ...
				if is_lit_var(qvalue) :
					return True
				elif is_any_var(qvalue) :
					return False
				else :
					return True
		#if isstr(value) and isstr(qvalue) :
			#if self.string_matches(value, qvalue) :
				#return True
		if value == qvalue :
			return True
		#return False
	
	def triples_match(self, triple, qtriple) :
		for tv, qv in izip(triple, qtriple) :
			#print 'v',prettyquery(tv),'q',prettyquery(qv)
			if not self.values_match(tv, qv) :
				return False
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
			elif isstr(t) and isstr(q) :
				# BUG: if there is more than one way to match the string with the 
				# pattern this will only return the first
				ret = self.find_matches(str(t), str(q))
				for i in range(len(ret[1])) :
					j = i + 1
					binding[ret['matchtypes'][j]] = ret[1][j]
			elif t != q :
				return Bindings()
		return binding
	
	def find_bindings_for_triple(self, triple, facts, reqd_facts) :
		bindings = []
		for ftriple in facts :
			binding = self.get_binding(triple, ftriple)
			if ftriple in reqd_facts or not reqd_facts :
				binding.matches_reqd_fact = True
			if binding and binding not in bindings :
				bindings.append(binding)
		
		return bindings
	
	def conflicting_bindings(self, a, b) :
		"""
		a and b are dictionaries.  Returns True if there are keys which are in 
		both a and b, but have different values.  Used in unification
		"""
		for k, v in a.iteritems() :
			if k in b and b[k] != v :
				if self.values_match(b[k], v) or self.values_match(v, b[k]):
					#print 'maybe',prettyquery(b[k]), prettyquery(v)
					#return self.MAYBE
					return True
				return True
		return False
	
	def has_already_executed(self, history, translation, binding) :
		return [translation, binding] in history
	
	def register_executed(self, history, translation, binding) :
		history.append([translation, copy.copy(binding)])
		
	def bind_vars(self, translation, facts, reqd_facts) :
		"""
		@arg translation is a list of triples (the translation)
		@arg facts is a list of triples (the currently known facts)
		@arg reqd_facts is a list of triples of which one must be used in the binding
		@returns matches, bindings
			matches is True if the query matches the translation
			bindings is a list of bindings for var to value
		"""
		#p('facts',facts)
		#p('reqd_facts',reqd_facts)
		bindings = []
		matches = True
		#debug('translation',translation)
		#print 'q',prettyquery(query)
		bindings = [Bindings()]
		for ttriple in translation :
			#p('ttriple',ttriple)
			
			possible_bindings = self.find_bindings_for_triple(ttriple, facts, reqd_facts)
			new_bindings = []
			# see if any of the next_bindings fit with the existing bindings
			found_binding = False
			for pbinding in possible_bindings :
				#p('matches',pbinding.matches_reqd_fact)
				# if there are no values in bindings that already have some other 
				# value in bindings 
				for binding in bindings :
					#debug('ttriple',ttriple)
					conflicting = self.conflicting_bindings(binding, pbinding)
					#debug('binding',binding)
					#debug('pbinding',pbinding)
					#debug('conflicting',conflicting)
					if not conflicting :
						# WARNING: this isn't going to copy the values of the bindings!!!
						new_binding = copy.copy(binding)
						#print prettyquery(new_binding)
						#print prettyquery(pbinding)
						#print
						new_binding.update(pbinding)
						if new_binding not in new_bindings :
							#debug('new_binding',new_binding)
							new_bindings.append(new_binding)
							found_binding = True
					elif conflicting == self.MAYBE :
						# WARNING: this isn't going to copy the values of the bindings!!!
						new_binding = Bindings(binding, possible = True)
						#print prettyquery(new_binding)
						#print prettyquery(pbinding)
						#print
						new_binding.update(pbinding)
						if new_binding not in new_bindings :
							#debug('maybe_new_binding',new_binding)
							new_bindings.append(new_binding)
							found_binding = True
						#debug('maybe ... this will work')
						matches = self.MAYBE
			#debug('found_binding',found_binding)
			if not found_binding :
				return False, []
			if len(new_bindings) > 0 :
				bindings = new_bindings
		
		#debug('bindings',bindings)
		
		# get a set of all vars
		vars = find_vars(translation)
		
		# if there are no vars, this does still match, but there are no bindings
		if len(vars) == 0 :
			return matches, []
		
		#p('bindings',bindings)
		# keep only the bindings which contain bindings for all of the vars and 
		# match a reqd_triple
		bindings = [binding for binding in bindings if len(binding) == len(vars) and binding.matches_reqd_fact]
		
		# if there are no bindings (and there are vars), failed to find a match
		if len(bindings) == 0 :
			return False, []
		
		#debug('matches',matches)
		#debug('bindings',bindings)
		
		return matches, bindings
		
	def contains(self, triples, value) :
		for triple in triples :
			for v in triple :
				if v == value :
					return True
		return False
	
	def find_bindings(self, facts, pattern, output_vars, reqd_triples, root = False) :
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
		# TODO: UNIFICATION use unification here, not just basic pattern matching
		# NOTE: actually I think this already is unification.  Its the 
		#       output_bindings which need to start using unification - and this 
		#       function will probably be used
		
		if len(pattern) == 0 and root:
			return True, [Bindings()]
		
		self.debugp('here')
		# check that all of the translation inputs match part of the query
		for triple in pattern :
			self.debugp('find_triple_match', triple, facts)
			if not self.find_triple_match(triple, facts) :
				return False, None
		
		self.debugp('here')
		# find all possible bindings for the vars if any exist
		matches, bindings_set = self.bind_vars(pattern, facts, reqd_triples)
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
		
		# make sure that the translation's input matches part of the reqd_triples
		# otherwise, not a new path
		if not self.partial_match_exists(translation[self.n.meta.input], reqd_triples) :
			return False, None
		
		matches, bindings = self.find_bindings(query, translation[self.n.meta.input], output_vars, reqd_triples, root)
		
		def filter_bindings(bindings) :
			if matches :
				for binding in bindings :
					# sometimes binding to an output variable is ok.  It is only ok if
					# they have already been bound to some value.  If they haven't the 
					# translation doesn't pass the test
					# TODO: this doesn't do anything ... what should it do?
					for var, value in binding.iteritems() :
						if (is_lit_var(value) or is_out_lit_var(value)) and var_name(value) in output_vars :
							continue
					
					yield binding
			
		return matches, filter_bindings(bindings)
	
	def next_bnode(self) :
		return self.n.bnode[str(time.time()).replace('.','') + '_' +  str(random.random()).replace('.','')]
	
	def find_paths(self, query, find_vars) :
		for possible_translation in possible_translations :
			something = find_paths(possible_translation, find_vars)
	
	# return all triples which have at least one var
	def find_var_triples(self, query, is_a_var = is_any_var) :
		return [triple for triple in query if any(map(lambda x:is_a_var(x), triple))]
	
	# return all triples which have at least one var in vars
	def find_specific_var_triples(self, query, vars) :
		return [triple for triple in query if any(map(lambda x:is_any_var(x) and var_name(x) in vars, triple))]

	def next_num(self) :
		self._next_num += 1
		return self._next_num
	
	def find_unified_bindings_triple(self, otriple, ntriple) :
		bindings = {}
		for ov, nv in izip(otriple, ntriple) :
			if ov != nv :
				return {}
			elif is_var(ov) and is_var(nv) :
				bindings[nv] = var_name(ov)
		return bindings
	
	def find_unified_bindings(self, old, new) :
		bindings = {}
		for otriple in old :
			for ntriple in new :
				bindings.update(self.find_unified_bindings_triple(otriple, ntriple))
		return bindings

	#@logger
	def next_translations(self, query, history, output_vars, reqd_triples, root = False) :
		"""
		@arg query the query in triples set form
		@arg history the history of steps already followed
		@arg output_vars is a set of variables which are not allowed to be bound as
			an input to a translation
		@returns the set of next guaranteed_steps and possible_steps.
			Ensures that this set of translation and bindings haven't already been 
			searched.....
		"""
		n = self.n
		
		guaranteed_steps = []
		possible_steps = []
		
		for translation in self.translations :
			matches, bindings_set = self.testtranslation(translation, query, output_vars, reqd_triples, root)
			if matches :
				self.debug('found match ' + translation[n.meta.name])
				for bindings in bindings_set :

					# keep the possible property
					new_bindings = Bindings(possible = bindings.possible)
					# replace the bindings which the translation defines as constant with
					# the exact binding value
					# replace the other bindings which are variables, with variables with
					# the name from the query and the type from the translation ...
					# TODO?: keep the state of each of the variables in the triple set
					# rather than as the namespace so it can be changed and checked 
					# easily.  Also, it should be consistant throughout the query anyway
					new_lit_vars = {}
					for var, value in bindings.iteritems() :
						if var in translation[n.meta.constant_vars] :
							new_bindings[var] = value
						elif is_any_var(value) :
							new_var = n.lit_var[var_name(value)+'_'+str(self.next_num())]
							new_lit_vars[var_name(value)] = new_var
							new_bindings[var] = new_var
					
					# input_bindings map from translation space to query space
					input_bindings = bindings
					# output_bindings map from translation space to query space
					output_bindings = {}
					
					###### TODO: resurect something like this.  UNIFICATION
					###### 			though it should probably wind up in/replacing find_bindings 
					######       rather than glued on here
					###### look through each of the output triples to see if they match any of 
					###### the already known facts.  By match, I mean everything the same 
					###### except for a lit_var in the output where a var is in the facts.  If
					###### one of these are found, replace the lit var with the var
					######for ttriple in translation[n.meta.output] :
						######for qtriple in query :
							######self.find_triple_match
							######for tv, qv in izip(ttriple, qtriple) :
								######if tv == qv :
									######p('tv',tv)
									######p('qv',qv)
								######else :
									######break
					######tmp_out = sub_var_bindings(translation[n.meta.output], input_bindings)
					######unified_bindings = self.find_unified_bindings(query, tmp_out)
					
					######constant_vars = unified_bindings.values()
					
					# TODO
					# this is where unification isn't happening right.
					# don't just automatically bind a new lit_var for everything.
					# instead, try to unify the output triples with the query and see if
					# any of the output triples match the existing triples.  If so, 
					# replace them:
					# ex:
					#	output: [n.var.x n.test.p, n.lit_var.x_out_1]
					# existing triples: [n.var.x, n.test.p, n.var.y]
					#
					# in this should bind to n.var.y instead of lit_var.x_out_1
					
					# first replace some vars with lit_vars (the ones which will be bound
					# eventually.
					
					# TODO: make sure that lit_var will work - make sure it matches 
					#       correctly
					
					
							
					# find bindings between the output and the query
					self.debugp('query', query)
					self.debugp('translation[n.meta.output]', translation[n.meta.output])
					# TODO: might be a good idea to clean up find_bindings first ...
					#tmp_output_bindings = self.find_bindings(translation[n.meta.output], query, output_vars, translation[n.meta.output])
					tmp_output_bindings = self.find_bindings(query, translation[n.meta.output], output_vars, query)
					self.debugp('tmp_output_bindings', tmp_output_bindings)
					
					# make sure output_bindings is setup like this old code has been doing
					# before
					
					# TODO: the guaranteed_steps stuff is going to have to look a little
					# different too ... if we want to replace (delete) triples that were
					# in the query something will need to change.
					# will just need to break the current assumption that:
					#   query + new_triples = new_query
					# instead we will know that :
					#   new_query - query = new_triples
					#     though note that there may be triples in query that are not in 
					#     new_query
					
					# find output_bindings
					# for each variable in the output triples
					for var in find_vars(translation[n.meta.output]) :
						# if this is a constant_var, bind it to whatever it was bound to
						# in the input part of the translation
						if var in translation[n.meta.constant_vars] :
							output_bindings[var] = input_bindings[var]
						#elif var in constant_vars :
							#output_bindings[var] = n.var[var]
						# otherwise, create a new lit_var to bind to
						else :
							output_bindings[var] = n.lit_var[var+'_out_'+str(self.next_num())]
					
					new_triples = sub_var_bindings(translation[n.meta.output], output_bindings)
					new_query = copy.copy(query)
					
					new_query.extend(new_triples)
					
					partial_bindings, partial_solution_triples, partial_facts_triples = self.find_partial_solution(self.var_triples, new_query, new_triples)
					#partial_triples = [triple for triple in partial_triples if triple in new_triples]
											
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
		
		#p('steps:',[step['translation'][n.meta.name] for step in guaranteed_steps])
		return guaranteed_steps, possible_steps
	
	def contains_all_bindings(self, required, obtained) :
		for key in required :
			if key not in obtained :
				return False
			elif not self.values_match(self.n.lit_var[key], obtained[key]) :
				return False
		return True
		
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
			#p(bindings)
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
			new_bindings, ftriple = self.find_solution_triple(triple, facts)
			if new_bindings :
				bindings.update(new_bindings)
				if ftriple in interesting_facts :
					found_var_triples.append(triple)
					fact_triples.append(ftriple)
		
		# make bindings just to the variable name not the full URI
		bindings = dict([(var_name(var), var_name(value)) for var, value in bindings.iteritems()])
		return bindings, found_var_triples, fact_triples
	
	#@logger
	def follow_guaranteed(self, query, possible_stack, history, output_vars, new_triples, root = False) :
		"""
		follow guaranteed translations and add possible translations to the 
			possible_stack
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
		
		self.debug_open_block('follow guaranteed')
		
		compile_node = {
			'guaranteed' : [],
			'possible' : [],
		}
		compile_node_found_solution = False
		
		# see what the guaranteed and possible next steps are
		guaranteed_steps, possible_steps = self.next_translations(query, history, output_vars, new_triples, root)
		if len(guaranteed_steps) == 0 :
			#partial_solution = self.find_partial_solution(self.var_triples, query, [])
			self.debug_close_block()
			return compile_node
		
		self.debug_open_block('guaranteed_steps')
		self.debugp(guaranteed_steps)
		self.debug_close_block()
		
		# look through all guarenteed steps recursively to see if they terminate and
		# should be added to the compile_node, the finished 'program'
		for step in guaranteed_steps :
			# if we've already made this translation, skip it
			if [step['translation'], step['input_bindings']] not in history :
				self.debug_open_block(step['translation'][n.meta.name] or '<unnamed>')
				# if there is only one next step, don't worry about copying the history
				# otherwise, we need a deep copy of the history.  This is so that other
				# paths can alter it without effecting other paths.
				if len(guaranteed_steps) > 1 :
					new_history = copy.copy(history)
				else :
					new_history = history
				
				# add this step to the history
				new_history.append([step['translation'], copy.copy(step['input_bindings'])])
				
				# if the new information at this point is enough to fulfil the query, done
				# otherwise, recursively continue searching
				found_solution = self.find_solution(self.var_triples, step['new_query'])
				if found_solution :
					step['solution'] = found_solution
				else :
					child_steps = self.follow_guaranteed(step['new_query'], possible_stack, new_history, output_vars, step['new_triples'])
					if child_steps :
						found_solution = True
						# TODO: what exactly is going on here?
						step['guaranteed'].extend(child_steps['guaranteed'])
						step['possible'].extend(child_steps['possible'])
					
				self.debug_close_block()
				
				if found_solution :
					compile_node['guaranteed'].append(step)
					compile_node_found_solution = True
		
		# don't follow the possible translations yet, just add then to a stack to
		# follow once all guaranteed translations have been found
		# NOTE: this will need to change
		for step in possible_steps:
			possible_stack.append({
				'root' : compile_node,
				'step' : step,
				'query' : query,
			})
		
		self.debug_close_block()
		
		if compile_node_found_solution == False :
			return False
		else :
			return compile_node
	
	def follow_possible(self, query, possible_stack) :
		"""
		
		"""
		#for translation in possible_stack :
			#compile_node = 
			## next_query, input_bindings, output_bindings
			#translation_step = self.follow_translation(query, translation)
			#compile_node['guaranteed'].append(translation_step)
		# TODO
		
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
		
		var_triples = self.find_specific_var_triples(query, reqd_bound_vars)
		if var_triples == [] :
			raise Exception("Waring, required bound triples were provided, but not found in the query")
		
		self.original_query = query
		self.var_triples = var_triples
		#p('var_triples',var_triples)
		self.vars = reqd_bound_vars
		self.vars = [var for var in self.vars if var.find('bnode') is not 0]
		#debug('self.vars',self.vars)
		
		possible_stack = []
		history = []
		
		compile_root_node = self.follow_guaranteed(query, possible_stack, history, reqd_bound_vars, query, True)
		
		if not compile_root_node :
			return compile_root_node
		
		#p('compile_root_node',compile_root_node)
		
		which_translations_fulfil_which_query_triple = self.extract_which_translations_fulfil_which_query_triple(compile_root_node)
		
		#p('which_translations_fulfil_which_query_triple',which_translations_fulfil_which_query_triple)
		
		which_translations_fulfil_which_query_triple_dict = {}
		for triple, step, depends in which_translations_fulfil_which_query_triple :
			obj = {'step' : step, 'depends' : depends}
			if triple in which_translations_fulfil_which_query_triple_dict :
				which_translations_fulfil_which_query_triple_dict[triple].append(obj)
			else :
				which_translations_fulfil_which_query_triple_dict[triple] = [obj]
		
		#p('which_translations_fulfil_which_query_triple_dict',which_translations_fulfil_which_query_triple_dict)
		
		# generate path combinations
		# a combination is a dictionary from triple to translation, which each 
		# triple is from the self.var_triples set.  A full completion/solution will 
		# have one translation for each var_triple.
		#p('begin combinations')
		combinations = [{}]
		new_combinations = []
		for triple, translations in which_translations_fulfil_which_query_triple_dict.iteritems() :
			for translation in translations :
				#p('triple',triple)
				#p('translation',translation['step'])
				#p('combinations',combinations.keys())
				for combination in combinations :
					# for each existing combination, if it already depends on a different
					# solution for a triple that this new translation depends on, can
					# not use it in a combination.
					# if none of the existing combinations fits with this one, there is
					# no solution
					# if the dependencies of this
					#p('combination',combination)
					#p('translation',translation)
					new_combination = self.permute_combinations(combination, translation)
					#p('new_combination',new_combination)
					if new_combination is not False:
						new_combination[triple] = translation
						new_combinations.append(new_combination)
			if len(new_combinations) > 0 :
				combinations = new_combinations
				new_combinations = []
			else :
				p('not')
		
		def print_combinations(combinations) :
			p()
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
		
		
		
		
		##p('compile_root_node',compile_root_node)
		##@logger
		#def print_compiled(node, l = []) :
			#for step in node['guaranteed'] :
				##p('\\',step['translation'][n.meta.name])
				#instruction = [
					#step['translation'][n.meta.name], {
						#'input_bindings' : step['input_bindings'],
						#'output_bindings' : step['output_bindings'],
					#}
				#]
				#print_compiled(step, l + [instruction])
				##p('/',step['translation'][n.meta.name])
			#if not node['guaranteed'] :
				#p(l+[node['solution']])
		##print_compiled(compile_root_node)
		
		
		## prune any paths which are not necessary:
		#def mark_unnecessary_translations_helper(node) :
			#"""
			#returns variables which need to be bound for the children (next) 
			#translations to be able to work.  If a translation doesn't provide any of
			#those variables as output, than it is unecessary.
			#correlary: if a translation provides an output binding that is never used
			#remove it.
			#"""
			#if 'solution' in node :
				#required_variables = set(node['solution'].values())
			#else :
				#required_variables = set()
			
			#for step in node['guaranteed'] :
				#required_variables.update(mark_unnecessary_translations_helper(step))
			
			#for var, binding in node['output_bindings'].items() :
				#if binding not in required_variables :
					#del node['output_bindings'][var]
			
			#if node['output_bindings'] :
				#node['input_bindings'] = dict([(var, binding) for (var, binding) in node['input_bindings'].iteritems() if not is_var(binding)])
				#required_variables.update(node['input_bindings'].values())
			
			#return required_variables
		
		#for node in compile_root_node['guaranteed'] :
			##p('---')
			#mark_unnecessary_translations_helper(node)
			
		##p('///')
		##print_compiled(compile_root_node)
		
		#def remove_unnecessary_translations(node) :
			#"""
			#returns a list to replace
			#"""
			#node['guaranteed'] = [step for step in node['guaranteed'] if step['output_bindings']]
			#for step in node['guaranteed'] :
				#remove_unnecessary_translations(step)
			
		#remove_unnecessary_translations(compile_root_node)
		
		##print_compiled(compile_root_node)
		
		##p(compile_root_node['guaranteed'][0]['translation'][n.meta.name])
		
		## TODO: make this work
		## self.follow_possible(query, possible_stack)
		
		#compile_root_node['modifiers'] = modifiers
		
		##debug('modifiers',modifiers)
		
		#p('compile_root_node',compile_root_node)
			
		#return compile_root_node
















