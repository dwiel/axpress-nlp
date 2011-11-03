# -*- coding: utf-8 -*-
import logging

from pylons import request, response, session, tmpl_context as c, url, app_globals as g
from pylons.controllers.util import abort, redirect

from axpressdebug.lib.base import BaseController, render

from SimpleSPARQL import p, CompilerException

log = logging.getLogger(__name__)

class IndexController(BaseController):

	def debug(self):
		c.query = request.params.get('query') or u""
		c.string_query = request.params.get('string_query') or u""
		c.ret = u""
		c.debug_html = u""
		
		if c.string_query :
			c.query = u"""
				x[axpress.is] = "%s"
				x[simple_display.text] = _out
			""" % c.string_query
			c.query = '\n'.join(line.strip() for line in c.query.split('\n'))
			
		if c.query :
			try :
				c.raw_ret = g.axpress.read_translate(c.query)
				if c.raw_ret and 'out' in c.raw_ret[0] :
					c.ret = u'<ul>%s</ul>' % u''.join(u'<li>'+unicode(o['out']) for o in c.raw_ret)
					c.ret_html = True
				else :
					c.ret = c.raw_ret
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