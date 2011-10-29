# -*- coding: utf-8 -*-
import logging

from pylons import request, response, session, tmpl_context as c, url, app_globals as g
from pylons.controllers.util import abort, redirect

from axpressdebug.lib.base import BaseController, render

from SimpleSPARQL import p, CompilerException

log = logging.getLogger(__name__)

class IndexController(BaseController):

	def debug(self):
		c.query = request.params.get('query') or ""
		c.string_query = request.params.get('string_query') or ""
		c.ret = ""
		c.debug_html = ""
		
		if c.string_query :
			c.query = """
				x[axpress.is] = "%s"
				x[simple_display.text] = _out
			""" % c.string_query
			c.query = '\n'.join(line.strip() for line in c.query.split('\n'))
			
		if c.query :
			try :
				c.raw_ret = g.axpress.read_translate(c.query)
				if c.raw_ret and 'out' in c.raw_ret[0] :
					c.ret = '<ul>%s</ul>' % ''.join('<li>'+o['out'] for o in c.raw_ret)
					c.ret_html = True
				else :
					c.ret = c.raw_ret
					c.ret_html = False
			except CompilerException, e :
				c.ret = str(e)
			c.debug_html = g.axpress.compiler.debug_str
		
		return render('debug.mako')
	
	def s(self):
		pass