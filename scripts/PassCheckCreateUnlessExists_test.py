#!/usr/bin/env python
# -*- coding: utf-8 -*-
import unittest

from SimpleSPARQL import *

n = globalNamespaces()
n.bind('sparql', '<http://dwiel.net/express/sparql/0.1/>')
n.bind('test', '<http://dwiel.net/express/test/0.1/>')

class PassCheckCreateUnlessExistsTestCase(unittest.TestCase):
	def setUp(self):
		self.sparql = SimpleSPARQL("http://localhost:2020/sparql")
		self.sparql.setGraph("http://dwiel.net/axpress/testing")
		self.sparql.setNamespaces(n)
		self.p = PassCheckCreateUnlessExists(self.sparql)
	
	# depends on Joseki
	#def test1(self):
		#q = {
			#n.sparql.reads : [
			#],
			#n.sparql.writes : [
				#{
					#n.sparql.create : n.sparql.unless_exists,
					#n.sparql.path : (0,),
					#n.test.x : 1,
				#},
			#],
		#}
		#r = {
			#n.sparql.reads : [ ],
			#n.sparql.writes : [
				#{
					#n.sparql.create : n.sparql.existed,
					#n.sparql.path : (0,),
					#n.sparql.subject : n.test.object1,
					#n.test.x : 1,
				#},
			#],
		#}


		print prettyquery(q)
		self.p(q)

if __name__ == "__main__" :
	unittest.main()





















