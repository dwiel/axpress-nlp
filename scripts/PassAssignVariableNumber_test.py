# -*- coding: utf-8 -*-
import unittest

from SimpleSPARQL import *

n = globalNamespaces()
n.bind('sparql', '<http://dwiel.net/express/sparql/0.1/>')
#!/usr/bin/env python

class PassAssignVariableNumberTestCase(unittest.TestCase):
	def setUp(self):
		self.p = PassAssignVariableNumber()
	
	def test1(self):
		q = [{
			'x' : '1'
		}]
		r = [{
			'x' : '1',
			n.sparql.subject : '?autovar1'
		}]
		assert self.p(q) == r
		
	def test2(self):
		q = [{
			'x' : '1',
			'y' : [
				{'a' : '1'},
				{'b' : '2'},
			],
		}]
		r = [{
			'x' : '1',
			'y' : [
				{
					'a' : '1',
					n.sparql.subject : '?autovar2'
				},
				{
					'b' : '2',
					n.sparql.subject : '?autovar3'
				},
			],
			n.sparql.subject : '?autovar1'
		}]
		assert self.p(q) == r, self.p(q)

if __name__ == "__main__" :
	unittest.main()

