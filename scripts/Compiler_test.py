#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Compiler testing
# this compiler assumes the translations available in loadTranslator

import unittest

import time, urllib
from SimpleSPARQL import Axpress, loadTranslations
from SimpleSPARQL.Utils import OutLitVar, Var, LitVar, p
from SimpleSPARQL.Triple import Triple

axpress = Axpress()
loadTranslations(axpress)
compiler = axpress.compiler
n = compiler.n

n.bind('foo', 'foo')

# for easy basic stupid matching type instance
class X():pass
type_instance = type(X())

class CompilerTestCase(unittest.TestCase):
  def test_bind_vars(self):
    # standard find_bindings
    query = [
      Triple([Var('image'), n.image.average_color, OutLitVar('color')])
    ]
    output_triples = [
      Triple([Var('image'), n.image.average_color, Var('color')]),
      Triple([Var('image'), n.image.new_property, Var('new_color')]),
    ]
    ret = compiler.bind_vars(output_triples, query, False)
    assert ret == [
      {
        'color' : OutLitVar('color'),
        'image' : Var('image'),
      },
    ]
    ret = compiler.bind_vars(output_triples, query, False, {})
    assert ret == [
      {
        'color' : OutLitVar('color'),
        'image' : Var('image'),
      },
    ]
  
  def test_bind_vars2(self):
    # try to find_bindings where we shouldn't be able to find any (given the 
    # initial_bindings)
    query = [
      [Var('x'), n.foo.a, Var('y')],
      [Var('y'), n.foo.b, Var('z')],
    ]
    output_triples = [
      [Var('r'), n.foo.a, Var('s')],
      [Var('s'), n.foo.b, Var('t')],
    ]
    initial_bindings = {
      u'r' : Var('y')
    }
    ret = compiler.bind_vars(output_triples, query, False, initial_bindings = initial_bindings)
    #p('ret', ret)
    assert ret == False
  
  def test_get_binding(self):
    compiler.prefer_litvars = True
    ret = compiler.get_binding(
      [ Var.t_623, n.dt.time, LitVar.time_out_646, ],
      [ Var.t_623, n.dt.time, Var.time_621, ],
    )
    # make sure that the if there is a lit var bound to a var, the litvar stays
    # and the vars disappear
    # NOTE: We don't always want it to work like this ...
    #p('ret', ret)
    assert ret == [{
      't_623' : Var.t_623,
      'time_621' : LitVar.time_out_646,
    }]
  
  def test_bind_vars_special(self) :
    ret = compiler.bind_vars([
      [ Var.x, n.dt.time, LitVar.time_out_646, ],
      [ Var.x, n.dt.time, Var.time_621, ],
      [ Var.x, n.dt.date, LitVar.date_out_646, ],
    ], [
      [ Var.x, n.dt.date, Var.date_621, ],
    ], False)
    #p('ret', ret)
    assert ret == [{
      'date_out_646' : Var.date_621,
      'x' : Var.x,
    }]
    
  def test_bind_vars(self):
    # try binding vars with extra data that doesn't need binding
    translation = [
      [ Var('x'), n.test.q, Var('bnode1'), ],
      [ Var('bnode1'), n.test.q, Var('y'), ],
      [ Var('x'), n.test.q, Var('bnode2'), ],
      [ Var('bnode2'), n.test.r, 10000, ],
    ]
    facts = [
      [ Var('x'), n.test.p, Var('bnode1'), ],
      [ Var('bnode1'), n.test.p, 1, ],
      [ Var('x'), n.test.q, Var('bnode2'), ],
      [ Var('bnode2'), n.test.q, OutLitVar('one') ],
    ]
    reqd_facts = False
    initial_bindings = {
      'x' : Var('x'),
      'y' : 1,
    }
    ret = compiler.bind_vars(translation, facts, reqd_facts, initial_bindings)
    #p('ret', ret)
    assert ret == [
      {
        'bnode1' : Var('bnode2'),
        'bnode2' : Var('bnode2'),
        'x' : Var('x'),
        'y' : 1,
      },
    ]
  
  def test_find_bindings_for_triple(self):
    ttriple = [ Var('bnode2'), n.test.r, 10000, ]
    facts = [
      [ Var('x'), n.test.p, Var('bnode1'), ],
      [ Var('bnode1'), n.test.p, 1, ],
      [ Var('x'), n.test.q, Var('bnode2'), ],
      [ Var('bnode2'), n.test.q, OutLitVar('one') ],
    ]
    ret = compiler.find_bindings_for_triple(ttriple, facts, False)
    assert ret == []

  def test_bind_vars_multi_triple_catch(self):
    output_triples =[
      [ Var('_'), n.u.inches, LitVar('out'), ],
      [ LitVar('out'), n.axpress.type, n.axpress.float, ],
    ]
    query = [
      [ Var('x'), n.u.feet, LitVar('f_out_1'), ],
      [ n.axpress.float, u'1', LitVar('f_out_1'), ],
      [ Var('x'), n.u.inches, OutLitVar('out'), ],
      [ LitVar('f_out_1'), n.axpress.type, n.axpress.float, ],
    ]
    initial_bindings = {
      '_' : Var('x'),
    }
    ret = compiler.bind_vars(output_triples, query, False, initial_bindings)
    #p('ret', ret)
    assert ret == [{
      '_' : Var('x'),
      'out' : OutLitVar('out'),
    }]

  def test_simple_bind_vars(self):
    output_triples =[
      [ Var('_'), n.u.inches, LitVar('out'), ],
    ]
    query = [
      [ Var('x'), n.u.inches, LitVar('f_out'), ],
    ]
    initial_bindings = {
      '_' : Var('x'),
    }
    ret = compiler.bind_vars(output_triples, query, False, initial_bindings)
    #p('ret', ret)
    assert ret == [{
      '_' : Var('x'),
      'out' : LitVar('f_out'),
    }]
    
  
if __name__ == "__main__" :
  unittest.main()



















