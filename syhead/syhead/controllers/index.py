# -*- coding: utf-8 -*-
import logging

from pylons import request, response, session, tmpl_context as c, url, app_globals as g
from pylons.controllers.util import abort, redirect

from syhead.lib.base import BaseController, render

from SimpleSPARQL import p, CompilerException
from SimpleSPARQL.Exceptions import TranslationResponse

log = logging.getLogger(__name__)

class IndexController(BaseController):

  def debug(self):
    c.query = request.params.get('query') or u""
    c.string_query = request.params.get('string_query', u'')
    c.debug_on = bool(request.params.get('debug'))
    c.ret = u""
    c.debug_html = u""
    
    if c.debug_on :
      c.debug_on_str = 'checked'
    else :
      c.debug_on_str = ''
    
    if not c.debug_on :
      g.axpress.compiler.debug_off()
    
    if c.string_query :
      c.query = u"""
        x[axpress.is] = "%s"
        x[simple_display.text] = _out
      """ % c.string_query
      c.query = '\n'.join(line.strip() for line in c.query.split('\n'))
      
    if c.query :
      try :
        try :
          c.raw_ret = g.axpress.read_translate(c.query)
        except TranslationResponse, e:
          # if there was a known error response, show that.  Example: "can not
          # divide by 0".  Or "Couldn't find a band by the name xyzyxz"
          c.raw_ret = str(e)
        
        c.debug_html = g.axpress.compiler.debug_str
        if c.raw_ret and 'out' in c.raw_ret[0] :
          c.ret = u'<ul>%s</ul>' % u''.join(u'<li>'+unicode(o['out']) for o in c.raw_ret)
          c.ret_html = True
        else :
          c.ret = repr(c.raw_ret)
          c.ret_html = False
      except CompilerException, e :
        c.ret = str(e)
        c.ret_html = False
        c.debug_html = g.axpress.compiler.debug_str
    else :
      c.ret_html = False
      c.debug_html = g.axpress.compiler.debug_str
    
    return render('debug.mako')
  
  def s(self):
    pass
  
  def translation_graph(self):
    c.axpress = g.axpress
    c.n = g.axpress.compiler.n

    filenames = {}
    class lookup_filename_id() :
      def __init__(self) :
        self.next_filename_id = 0
      def __call__(self, filename) :
        id = filenames.get(filename, None)
        if id != None :
          return id
        else :
          filenames[filename] = self.next_filename_id
          self.next_filename_id += 1
          return filenames[filename]
    c.lookup_filename_id = lookup_filename_id()
    
    from subprocess import Popen, PIPE
    p = Popen("dot -Tpng -Goverlap=false", shell=True, stdin=PIPE, stdout=PIPE)
    
    def test(t) :
      fn = t['filename']
      return 'date' in fn or 'time' in fn
    
    p.stdin.write("digraph sdsu {")
    for t in c.axpress.compiler.translations :
      if test(t) :
        p.stdin.write('"%s";' % t['name'])
      #, group:${c.lookup_filename_id(t['filename'])} },
      
    def t_by_id(id) :
      return c.axpress.compiler.translations_by_id[id]
    def name_by_id(id) :
      return c.axpress.compiler.translations_by_id[id]['name']
    
    for id, ts in c.axpress.compiler.translation_matrix.iteritems() :
      for t in ts :
        if test(t) and test(t_by_id(id)) :
          p.stdin.write('"%s" -> "%s";' % (
            name_by_id(id), name_by_id(t['id'])
          ))
    p.stdin.write("}")
    
    #return render('translation_graph.mako')
    p.stdin.close()
    print 'rendering'
    response.headers['Content-Type'] = 'image/png'
    #response.write(p.stdout.read())
    return p.stdout.read()
