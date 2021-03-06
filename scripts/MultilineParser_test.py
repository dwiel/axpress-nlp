#!/usr/bin/env python
# -*- coding: utf-8 -*-
import unittest

import time, urllib
from rdflib import *
from SimpleSPARQL import *

sparql = SimpleSPARQL("http://localhost:2020/sparql")
sparql.setGraph("http://dwiel.net/axpress/testing")

n = sparql.n
n.bind('string', '<http://dwiel.net/express/string/0.1/>')
n.bind('math', '<http://dwiel.net/express/math/0.1/>')
n.bind('file', '<http://dwiel.net/express/file/0.1/>')
n.bind('glob', '<http://dwiel.net/express/glob/0.1/>')
n.bind('color', '<http://dwiel.net/express/color/0.1/>')
n.bind('sparql', '<http://dwiel.net/express/sparql/0.1/>')
n.bind('call', '<http://dwiel.net/express/call/0.1/>')
n.bind('test', '<http://dwiel.net/express/test/0.1/>')
n.bind('library', '<http://dwiel.net/axpress/library/0.1/>')
n.bind('music', '<http://dwiel.net/axpress/music/0.1/>')
n.bind('music_album', '<http://dwiel.net/axpress/music_album/0.1/>')
n.bind('source', '<http://dwiel.net/axpress/source/0.1/>')
n.bind('lastfm', '<http://dwiel.net/axpress/lastfm/0.1/>')
n.bind('rdfs', '<http://www.w3.org/2000/01/rdf-schema#>')
n.bind('test', '<http://dwiel.net/express/test/0.1/>')
n.bind('bound_var', '<http://dwiel.net/axpress/bound_var/0.1/>')
a = n.rdfs.type

#cache_sparql = SimpleSPARQL("http://localhost:2020/sparql", graph = "http://dwiel.net/axpress/cache")
#cache = Cache(cache_sparql)
#translator = Translator(cache)

#loadTranslations(translator, n)

#compiler = Compiler(n)
#loadTranslations(compiler, n)

#axpress = Axpress(sparql = sparql, compiler = compiler, evaluator = Evaluator(n))

compiler = Compiler(n)
evaluator = Evaluator(n)

axpress = Axpress(
	sparql = sparql,
	compiler = compiler,
	evaluator = evaluator
)
loadTranslations(axpress, n)

class PassCompleteReadsTestCase(unittest.TestCase):
	def setUp(self):
		self.parser = MultilineParser(n, axpress = axpress)
		n.bind('flickr', '<http://dwiel.net/axpress/flickr/0.1/>')
		n.bind('amos', '<http://dwiel.net/axpress/amos/0.1/>')
	
	#def test1(self):
		#assert self.parser.parse("""
			#read sparql
				#test.object2[test.x] = _x
				#test.object2[test.y] = _y
			#write sparql unless exists
				#test.object2[test.yyy] = y
		#""") == 'hello'
	
	#def test2(self):
		#assert self.parser.parse("""
			#read translate
				#image[glob.glob] = "/home/dwiel/pictures/stitt blanket/*.jpg"
				#image[file.filename] = _filename
				#thumb = image.thumbnail(image, 4, 4, image.antialias)
				#thumb[pil.image] = _thumb_image
			#write sparql
				#image[file.filename] = filename
				#image[amos.thumb] = thumb
				#thumb[pil.image] = thumb_image
		#""") == 'hello'
	
	#def test3(self):
		#ret = self.parser.parse("""
			#read translate
					#image[glob.glob] = "/home/dwiel/pictures/stitt blanket/*.jpg"
					#image[file.filename] = _filename
			#write sparql unless exists
					#_image[file.filename] = _filename
			#write sparql unless exists
					#image[meta.tag] = 'stitt'
		#""")
		#print 'ret',prettyquery(ret)
	
	"""
"""
	
if __name__ == "__main__" :
	unittest.main()


