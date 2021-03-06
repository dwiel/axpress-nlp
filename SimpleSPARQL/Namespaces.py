# -*- coding: utf-8 -*-
import re

from URIRef import URIRef

def uri_could_be_from_namespace(self, uri, namespace) :
	if re.match(namespace+"([^ .\}]+)", uri) :
		return True
	return False

class Namespace(URIRef):
	def term(self, name):
		return URIRef(self + name)
	
	def __getitem__(self, key, default=None):
		return self.term(key)
	
	def __getattr__(self, name):
		if name.startswith("__"): # ignore any special Python names!
			raise AttributeError
		else:
			return self.term(name)

class Namespaces() :
	namespaces = {}

	def bind(self, prefix, namespace) :
		if not isinstance(namespace, Namespace) :
			if type(namespace) == str or type(namespace) == unicode :
				if namespace[:1] == '<' and namespace[-1:] == '>' :
					namespace = namespace[1:-1]
			namespace = Namespace(namespace)
		if isinstance(namespace, Namespace) :
			self.namespaces[prefix] = namespace

	def SPARQL_PREFIX(self) :
		str = ''
		for prefix, namespace in self.namespaces.iteritems() :
			str += 'PREFIX %s: <%s> ' % (prefix, namespace)
		return str

	def n3_prefix(self) :
		s = ''
		for prefix, namespace in self.namespaces.iteritems() :
			s += '@prefix %s: <%s> .\n' % (prefix, namespace)
		return str(s)
	n3 = n3_prefix
	
	def matches(self, uri) :
		for prefix in self.namespaces.keys() :
			if re.match(prefix+":([^ .\}]+)", uri) :
				return True
		return False
	
	def shorten(self, uri, seperator = ':') :
		for prefix, namespace in self.namespaces.iteritems() :
			g = re.match(namespace+"([^ .\}]+)", uri)
			if g :
				return prefix+seperator+g.group(1)
		return '<'+uri+'>'
	
	def shorten_pairs(self, uri) :
		for prefix, namespace in self.namespaces.iteritems() :
			g = re.match(namespace+"([^ .\}]+)", uri)
			if g :
				return prefix, g.group(1)
		return (None, None)
	
	def shortenForN(self, uri) :
		for prefix, namespace in self.namespaces.iteritems() :
			g = re.match(namespace+"([^ .\}]+)", uri)
			if g :
				return 'n.'+prefix+'.'+g.group(1)
		return '<'+uri+'>'
	
	def __getitem__(self, key) :
		return self.namespaces[key]
	
	def __setitem__(self, key, value) :
		self.bind(key, value)
	
	def __getattr__(self, key) :
		return self[key]

	def __iter__(self) :
		return self.namespaces.__iter__()
	
	def iteritems(self) :
		return self.namespaces.iteritems()
	
	def __eq__(self, obj) :
		if isinstance(obj, Namespaces) :
			return self.namespaces == obj.namespaces
		else :
			return False
	
	def __nonzero__(self) :
		return True



n = Namespaces()	

def globalNamespaces() :
	return n


















