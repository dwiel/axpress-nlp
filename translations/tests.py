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

def loadTranslations(axpress) :
  axpress.n.bind('file', '<http://dwiel.net/express/file/0.1/>')
  axpress.n.bind('html', '<http://dwiel.net/express/html/0.1/>')
  axpress.n.bind('test', '<http://dwiel.net/express/test/0.1/>')
  
  def _sum(vars) :
    vars['sum'] = vars['x'] + vars['y']
  axpress.register_translation({
    'name' : 'sum',
    'input' : """
      foo[test.x] = _x
      foo[test.y] = _y
    """,
    'output' : [
      'foo[test.sum] = _sum',
    ],
    'function' : _sum,
  })
  
  def _add_one(vars) :
    vars['sum'] = vars['x'] + 1
  axpress.register_translation({
    'name' : 'add_one',
    'input' : """
      foo[test.x] = _x
    """,
    'output' : [
      'foo[test.add_one] = _sum',
    ],
    'function' : _add_one,
  })
  
  def _add_two(vars) :
    vars['sum'] = vars['x'] + 2
  axpress.register_translation({
    'name' : 'add_two',
    'input' : """
      foo[test.x] = _x
    """,
    'output' : [
      'foo[test.add_two] = _sum',
    ],
    'function' : _add_two,
  })
  
  def prod(vars) :
    vars['prod'] = float(vars['sum']) * vars['z']
  axpress.register_translation({
    'name' : 'product',
    'input' : [
      'uri[test.sum] = _sum',
      'uri[test.z] = _z',
    ],
    'output' : [
      'uri[test.prod] = _prod',
    ],
    'function' : prod,
  })
  
  def div(vars) :
    vars['div'] = float(vars['sum']) / vars['z']
  axpress.register_translation({
    'name' : 'division',
    'input' : [
      'uri[test.sum] = _sum',
      'uri[test.z] = _z',
    ],
    'output' : [
      'uri[test.div] = _div',
    ],
    'function' : div,
  })
    
  def html_img(vars):
    web_filename = vars['filename'].replace('/home/dwiel', '/home')
    vars['html'] = '<img src="%s" width="%s" height="%s"/>' % (web_filename, vars['width'], vars['height'])
  axpress.register_translation({
    'name' : 'html img link',
    'input' : """
      image[file.filename] = _filename
      image[html.width] = _width
      image[html.height] = _height
    """,
    'output' : """
      image[html.html] = _html
    """,
    'function' : html_img,
  })

  # used for testing a translation which returns no bindings
  def no_bindings(vars):
    return []
  axpress.register_translation({
    'name' : 'no bindings',
    'input' : """
      foo[test.no_bindings_input] = _input
    """,
    'output' : """
      foo[test.no_bindings_output] = _output
    """,
    'function' : no_bindings,
  })
  
  axpress.register_translation({
    'name' : 'test',
    'input' : """
      xxx[test.p][test.p] = yyy
    """,
    'output' : """
      xxx[test.q][test.q] = yyy
      xxx[test.q][test.r] = 10000
    """,
    # note that y isn't a constant var ... right now it is because y in the 
    # input will likely be bound to a different variable than y in the output,
    # so it isn't constant.  The value is constant, 
  })
  
  axpress.register_translation({
    'name' : 'test2',
    'input' : """
      x[test.p] = y
    """,
    'output' : """
      x[test.q] = y
      x[test.r] = z
    """,
    # note that y isn't a constant var ... right now it is because y in the 
    # input will likely be bound to a different variable than y in the output,
    # so it isn't constant.  The value is constant,
    # 2011-10-27: it is constant now ...
  })

  # I guess it is possible here that z and x wind up being unified ... thats
  # not the intention though
  axpress.register_translation({
    'name' : 'test3',
    'input' : """
      x[test.a] = y
    """,
    'output' : """
      x[test.b] = y
      x[test.c] = z
      z[test.d] = z
    """,
  })
  
  axpress.register_translation({
    'name' : 'test4',
    'input' : """
      x[test.b] = _w
    """,
    'output' : """
      x[test.c] = _w
    """,
  })
  
  def f(vars) :
    vars['u'] = 1
  axpress.register_translation({
    'name' : 'test5',
    'input' : """
      t[test.aa] = _s
    """,
    'output' : """
      t[test.ad] = _u
    """,
    'function' : f
  })
  
  axpress.register_translation({
    'name' : 'test6',
    'input' : """
      t[test.ad] = _s
    """,
    'output' : """
      t[test.ae] = _s
    """,
  })
  
  # given xx, ad is equal to x and use the above test to imply that yy is also x
  axpress.register_translation({
    'name' : 'test7',
    'input' : """
      t[test.xx] = x
    """,
    'output' : """
      t[test.ad] = x
      t[test.yy] = t[test.ae]
    """,
  })
  
  axpress.register_translation({
    'name' : 'eq',
    'input' : """
      t[test.p1] = p1
    """,
    'output' : """
      t[test.p2] = p1
    """,
  })

  def t1_t2(vars) :
    vars['t2'] = [vars['t1']] * 3
  axpress.register_translation({
    'name' : 't1 -> t2',
    'input' : """
      t[test.t1] = _t1
    """,
    'output' : """
      t[test.t2] = _t2
    """,
    'function' : t1_t2,
  })

  def t2_t3(vars) :
    vars['t3'] = [vars['t2']] * 3
  axpress.register_translation({
    'name' : 't2 -> t3',
    'input' : """
      t[test.t2] = _t2
    """,
    'output' : """
      t[test.t3] = _t3
    """,
    'function' : t2_t3,
  })

  def t3_t4(vars) :
    vars['t4'] = [vars['t3']] * 3
  axpress.register_translation({
    'name' : 't3 -> t4',
    'input' : """
      t[test.t3] = _t3
    """,
    'output' : """
      t[test.t4] = _t4
    """,
    'function' : t3_t4,
  })

  # for testDiverge
  axpress.rule('a1 -> a2', """
      x[test.a1] = a
  """, """
      x[test.a2] = a
  """)
  axpress.rule('b1 -> b2', """
      x[test.b1] = b
  """, """
      x[test.b2] = b
  """)
  axpress.rule('a1 + b1', """
      x[test.a2] = a
      x[test.b2] = b
  """, """
      x[test.a2b2] = test.add(a, b)
  """)
  def math_add(vars) :
    vars['sum'] = vars['x'] + vars['y']
  #axpress.rule('math.add', """
  #    sum = test.add(_x, _y)
  #""", "", math_add, add_output_vars = ['sum'])
  axpress.rule('math.add', """
      sum = test.add(_x, _y)
  """, """
      _sum = test.add(_x, _y)
  """, math_add)

