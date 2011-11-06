# -*- coding: utf-8 -*-
from SimpleSPARQL import *
import os
import random
import re
import urllib
import urllib2
import time
import json
import glob

def loadTranslations(axpress, n) :
  n.bind('file', '<http://dwiel.net/express/file/0.1/>')
  n.bind('html', '<http://dwiel.net/express/html/0.1/>')
  n.bind('test', '<http://dwiel.net/express/test/0.1/>')
  
  def _sum(vars) :
    vars['sum'] = vars['x'] + vars['y']
  axpress.register_translation({
    n.meta.name : 'sum',
    n.meta.input : """
      foo[test.x] = _x
      foo[test.y] = _y
    """,
    n.meta.output : [
      'foo[test.sum] = _sum',
    ],
    n.meta.function : _sum,
  })
  
  def _add_one(vars) :
    vars['sum'] = vars['x'] + 1
  axpress.register_translation({
    n.meta.name : 'add_one',
    n.meta.input : """
      foo[test.x] = _x
    """,
    n.meta.output : [
      'foo[test.add_one] = _sum',
    ],
    n.meta.function : _add_one,
  })
  
  def _add_two(vars) :
    vars['sum'] = vars['x'] + 2
  axpress.register_translation({
    n.meta.name : 'add_two',
    n.meta.input : """
      foo[test.x] = _x
    """,
    n.meta.output : [
      'foo[test.add_two] = _sum',
    ],
    n.meta.function : _add_two,
  })
  
  def prod(vars) :
    vars['prod'] = float(vars['sum']) * vars['z']
  axpress.register_translation({
    n.meta.name : 'product',
    n.meta.input : [
      'uri[test.sum] = _sum',
      'uri[test.z] = _z',
    ],
    n.meta.output : [
      'uri[test.prod] = _prod',
    ],
    n.meta.function : prod,
  })
  
  def div(vars) :
    vars['div'] = float(vars['sum']) / vars['z']
  axpress.register_translation({
    n.meta.name : 'division',
    n.meta.input : [
      'uri[test.sum] = _sum',
      'uri[test.z] = _z',
    ],
    n.meta.output : [
      'uri[test.div] = _div',
    ],
    n.meta.function : div,
  })
    
  def html_img(vars):
    web_filename = vars['filename'].replace('/home/dwiel', '/home')
    vars['html'] = '<img src="%s" width="%s" height="%s"/>' % (web_filename, vars['width'], vars['height'])
  axpress.register_translation({
    n.meta.name : 'html img link',
    n.meta.input : """
      image[file.filename] = _filename
      image[html.width] = _width
      image[html.height] = _height
    """,
    n.meta.output : """
      image[html.html] = _html
    """,
    n.meta.function : html_img,
  })

  # used for testing a translation which returns no bindings
  def no_bindings(vars):
    return []
  axpress.register_translation({
    n.meta.name : 'no bindings',
    n.meta.input : """
      foo[test.no_bindings_input] = _input
    """,
    n.meta.output : """
      foo[test.no_bindings_output] = _output
    """,
    n.meta.function : no_bindings,
  })
  
  axpress.register_translation({
    n.meta.name : 'test',
    n.meta.input : """
      x[test.p][test.p] = y
    """,
    n.meta.output : """
      x[test.q][test.q] = y
      x[test.q][test.r] = 10000
    """,
    # note that y isn't a constant var ... right now it is because y in the 
    # input will likely be bound to a different variable than y in the output,
    # so it isn't constant.  The value is constant, 
  })
  
  axpress.register_translation({
    n.meta.name : 'test2',
    n.meta.input : """
      x[test.p] = y
    """,
    n.meta.output : """
      x[test.q] = y
      x[test.r] = z
    """,
    # note that y isn't a constant var ... right now it is because y in the 
    # input will likely be bound to a different variable than y in the output,
    # so it isn't constant.  The value is constant,
    # 2011-10-27: it is constant now ...
  })
