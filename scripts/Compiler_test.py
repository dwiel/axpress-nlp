#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Compiler testing
# this compiler assumes the translations available in loadTranslator

import unittest

import time, urllib
from rdflib import *
from SimpleSPARQL import *

# n = Namespaces.globalNamespaces()

sparql = SimpleSPARQL("http://localhost:2020/sparql")
sparql.setGraph("http://dwiel.net/axpress/testing")

n = sparql.n
n.bind('library', '<http://dwiel.net/axpress/library/0.1/>')
n.bind('music', '<http://dwiel.net/axpress/music/0.1/>')
n.bind('music_album', '<http://dwiel.net/axpress/music_album/0.1/>')
n.bind('source', '<http://dwiel.net/axpress/source/0.1/>')
n.bind('lastfm', '<http://dwiel.net/axpress/lastfm/0.1/>')
n.bind('rdfs', '<http://www.w3.org/2000/01/rdf-schema#>')
n.bind('test', '<http://dwiel.net/express/test/0.1/>')
n.bind('bound_var', '<http://dwiel.net/axpress/bound_var/0.1/>')

a = n.rdfs.type

compiler = Compiler(n)

loadTranslations(compiler, n)

# for easy basic stupid matching type instance
class X():pass
type_instance = type(X())

class PassCompleteReadsTestCase(unittest.TestCase):
	#def test1(self) :
		#ret = compiler.read_translations([
			#'test.u[test.x] = 1',
			#'test.u[test.x] = 10',
			#'test.u[test.y] = 2',
			#'test.u[test.y] = 20',
			#'test.u[test.z] = 100',
			#'test.u[test.div] = div',
		#])
		#print prettyquery(ret)
		#assert ret == [
			#[
				#[ n.test.u, n.test.x, 1, ],
				#[ n.test.u, n.test.x, 10, ],
				#[ n.test.u, n.test.y, 2, ],
				#[ n.test.u, n.test.y, 20, ],
				#[ n.test.u, n.test.z, 100, ],
				#[ n.test.u, n.test.div, n.var.div, ],
				#[ n.test.u, n.test.sum, 3, ],
				#[ n.test.u, n.test.prod, 300, ],
				#[ n.test.u, n.test.div, 0.029999999999999999, ],
			#], [
				#[ n.test.u, n.test.x, 1, ],
				#[ n.test.u, n.test.x, 10, ],
				#[ n.test.u, n.test.y, 2, ],
				#[ n.test.u, n.test.y, 20, ],
				#[ n.test.u, n.test.z, 100, ],
				#[ n.test.u, n.test.div, n.var.div, ],
				#[ n.test.u, n.test.sum, 12, ],
				#[ n.test.u, n.test.prod, 1200, ],
				#[ n.test.u, n.test.div, 0.12, ],
			#], [
				#[ n.test.u, n.test.x, 1, ],
				#[ n.test.u, n.test.x, 10, ],
				#[ n.test.u, n.test.y, 2, ],
				#[ n.test.u, n.test.y, 20, ],
				#[ n.test.u, n.test.z, 100, ],
				#[ n.test.u, n.test.div, n.var.div, ],
				#[ n.test.u, n.test.sum, 21, ],
				#[ n.test.u, n.test.prod, 2100, ],
				#[ n.test.u, n.test.div, 0.20999999999999999, ],
			#], [
				#[ n.test.u, n.test.x, 1, ],
				#[ n.test.u, n.test.x, 10, ],
				#[ n.test.u, n.test.y, 2, ],
				#[ n.test.u, n.test.y, 20, ],
				#[ n.test.u, n.test.z, 100, ],
				#[ n.test.u, n.test.div, n.var.div, ],
				#[ n.test.u, n.test.sum, 30, ],
				#[ n.test.u, n.test.prod, 3000, ],
				#[ n.test.u, n.test.div, 0.29999999999999999, ],
			#],
		#]

	#def test2(self):
		#ret = compiler.read_translations([
			#'test.u[test.x] = 1',
			#'test.u[test.x] = 2',
			#'test.u[test.y] = 10',
			#'test.u[test.sum] = sum',
		#])
		#assert ret == [
			#[
				#[ n.test.u, n.test.x, 1, ],
				#[ n.test.u, n.test.x, 2, ],
				#[ n.test.u, n.test.y, 10, ],
				#[ n.test.u, n.test.sum, n.var.sum, ],
				#[ n.test.u, n.test.sum, 11, ],
			#],
			#[
				#[ n.test.u, n.test.x, 1, ],
				#[ n.test.u, n.test.x, 2, ],
				#[ n.test.u, n.test.y, 10, ],
				#[ n.test.u, n.test.sum, n.var.sum, ],
				#[ n.test.u, n.test.sum, 12, ],
			#],
		#]
	
	#def test3(self):
		#ret = compiler.read_translations([
			#'image[file.filename] = "/home/dwiel/AMOSvid/1065/20080821_083129.jpg"',
			#'thumb = image.thumbnail(image, 4, 4)'
		#])
		#print 'retret',prettyquery(ret)
		#ret[0][5][2] = type(ret[0][5][2])
		#ret[0][6][2] = type(ret[0][6][2])
		#assert ret == [
			#[
				#[ n.var.image, n.file.filename, '/home/dwiel/AMOSvid/1065/20080821_083129.jpg', ],
				#[ n.var.bnode1, n.call.arg1, n.var.image, ],
				#[ n.var.bnode1, n.call.arg2, 4, ],
				#[ n.var.bnode1, n.call.arg3, 4, ],
				#[ n.var.bnode1, n.image.thumbnail, n.var.thumb, ],
				#[ n.var.image, n.pil.image, type_instance, ],
				#[ n.var.thumb, n.pil.image, type_instance, ],
			#],
		#]
	
	## this case should be seperated from activity on my hard drive
	#def test_glob_glob(self):
		#ret = compiler.read_translations([
			#'"/home/dwiel/AMOSvid/*.py"[glob.glob] = filename'
		#])
		#assert ret == [
			#[
				#[ '/home/dwiel/AMOSvid/*.py', n.glob.glob, n.var.filename, ],
				#[ '/home/dwiel/AMOSvid/*.py', n.glob.glob, '/home/dwiel/AMOSvid/generate_thumbnail_images.py', ],
			#],
			#[
				#[ '/home/dwiel/AMOSvid/*.py', n.glob.glob, n.var.filename, ],
				#[ '/home/dwiel/AMOSvid/*.py', n.glob.glob, '/home/dwiel/AMOSvid/imagevid.py', ],
			#],
			#[
				#[ '/home/dwiel/AMOSvid/*.py', n.glob.glob, n.var.filename, ],
				#[ '/home/dwiel/AMOSvid/*.py', n.glob.glob, '/home/dwiel/AMOSvid/find_closest_thumnail.py', ],
			#],
		#]
	
	#def test_compile0(self):
		## in this case the compiler should come up with the paths required to 
		## evalutate it, but not actually evaluate it
		#ret = compiler.compile("""
			#test.u[test.x] = 1
			#test.u[test.x] = 2
			#test.u[test.y] = 10
			#test.u[test.sum] = sum
		#""", input = [], output = ['sum'])
		#print 'ret',prettyquery(ret)
	
	#def test_compile1(self):
		## in this case the compiler should come up with the paths required to 
		## evalutate it, but not actually evaluate it
		#ret = compiler.compile("""
			#test.u[test.x] = 1
			#test.u[test.y] = 2
			#test.u[test.sum] = sum
			#test.u[test.z] = 100
			#test.u[test.div] = div
		#""", input = [], output = ['sum', 'div'])
		#print 'ret',prettyquery(ret)
	
	#def test_compile2(self):
		#ret = compiler.compile("""
			#test.u[test.x] = _x
			#test.u[test.x] = 10
			#test.u[test.y] = 2
			#test.u[test.y] = 20
			#test.u[test.z] = 100
			#test.u[test.div] = div
		#""", input = ['x'], output = ['div'])
		#print 'ret',prettyquery(ret)
	
	def test_compile3(self):
		ret = compiler.compile("""
			image[file.filename] = "/home/dwiel/AMOSvid/1065/20080821_083129.jpg"
			thumb = image.thumbnail(image, 4, 4)
			thumb_image = thumb[pil.image]
		""", ['thumb_image'])
		print 'ret',prettyquery(ret)
		assert ret is not False
	
	def test_find_bindings(self):
		query = [
			[n.var.image, n.image.average_color, n.out_lit_var.color]
		]
		output_triples = [
			[n.var.image, n.image.average_color, n.var.color],
			[n.var.image, n.image.new_property, n.var.new_color],
		]
		ret = compiler.find_bindings(query, output_triples, [], [])
		p('ret', ret)
		ret = compiler.bind_vars(output_triples, query, [], {})
		p('ret', ret)
	
	def test_next_steps1(self):
		compiler.reqd_bound_vars = [n.var.color]
		ret = compiler.next_steps([
				[ n.var.image, n.file.pattern, 'pictures/*.jpg', ],
				[ n.var.bnode1, n.call.arg1, n.var.image, ],
				[ n.var.bnode1, n.call.arg2, 1, ],
				[ n.var.bnode1, n.call.arg3, 1, ],
				[ n.var.bnode1, n.image.thumbnail, n.var.thumb, ],
				[ n.var.bnode2, n.call.arg1, n.var.thumb, ],
				[ n.var.bnode2, n.call.arg2, 0, ],
				[ n.var.bnode2, n.call.arg3, 0, ],
				[ n.var.bnode2, n.image.pixel, n.var.pixel, ],
				[ n.var.pixel, n.pil.color, n.out_lit_var.color, ],
				[ n.var.image, n.file.filename, n.lit_var.out_filename_out_1, ],
				[ n.var.image, n.pil.image, n.lit_var.pil_image_out_7, ],
				[ n.var.thumb, n.pil.image, n.lit_var.thumb_image_out_10, ],
			],[],
			[ u'color', ],
			[
				[ n.var.thumb, n.pil.image, n.lit_var.thumb_image_out_10, ],
			],
			False
		)
		p('ret', ret)
		assert len(ret) == 2
		assert ret[1] == []
		assert ret[0][0] == {
			'guaranteed' : [],
			'input_bindings' : {
				u'bnode1' : n.var.bnode2,
				u'image' : n.var.thumb,
				u'pil_image' : n.lit_var.thumb_image_out_10,
				u'pixel' : n.var.pixel,
				u'x' : 0,
				u'y' : 0,
			},
			'new_query' : [
				[ n.var.image, n.file.pattern, 'pictures/*.jpg', ],
				[ n.var.bnode1, n.call.arg1, n.var.image, ],
				[ n.var.bnode1, n.call.arg2, 1, ],
				[ n.var.bnode1, n.call.arg3, 1, ],
				[ n.var.bnode1, n.image.thumbnail, n.var.thumb, ],
				[ n.var.bnode2, n.call.arg1, n.var.thumb, ],
				[ n.var.bnode2, n.call.arg2, 0, ],
				[ n.var.bnode2, n.call.arg3, 0, ],
				[ n.var.bnode2, n.image.pixel, n.var.pixel, ],
				[ n.var.pixel, n.pil.color, n.out_lit_var.color, ],
				[ n.var.image, n.file.filename, n.lit_var.out_filename_out_1, ],
				[ n.var.image, n.pil.image, n.lit_var.pil_image_out_7, ],
				[ n.var.thumb, n.pil.image, n.lit_var.thumb_image_out_10, ],
				[ n.var.pixel, n.pil.color, n.lit_var.color_out_3, ],
			],
			'new_triples' : [
				[ n.var.pixel, n.pil.color, n.lit_var.color_out_3, ],
			],
			'output_bindings' : {
				u'color' : n.lit_var.color_out_3,
				u'pixel' : n.var.pixel,
			},
			'partial_bindings' : {
			},
			'partial_facts_triples' : [],
			'partial_solution_triples' : [],
			'possible' : [],
			'translation' : {
				n.meta.constant_vars : [ 'image', 'pixel', ],
				n.meta.function : compiler.translations_by_name['image pixel'][n.meta.function],
				n.meta.input : [
					[ n.var.image, n.pil.image, n.lit_var.pil_image, ],
					[ n.var.bnode1, n.call.arg1, n.var.image, ],
					[ n.var.bnode1, n.call.arg2, n.lit_var.x, ],
					[ n.var.bnode1, n.call.arg3, n.lit_var.y, ],
					[ n.var.bnode1, n.image.pixel, n.var.pixel, ],
				],
				n.meta.name : 'image pixel',
				n.meta.output : [
					[ n.var.pixel, n.pil.color, n.lit_var.color, ],
				],
			},
		}


if __name__ == "__main__" :
	unittest.main()



















