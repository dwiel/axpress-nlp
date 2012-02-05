from mako.template import Template

import hashlib

def loadTranslations(axpress) :
  axpress.n.bind('list', '<http://dwiel.net/axpress/list/0.1/>')
  axpress.n.bind('simple_display', '<http://dwiel.net/axpress/simple_display/0.1/>')
  
  def hash(x) :
    m = hashlib.md5()
    m.update(x)
    return m.hexdigest()
  
  def filename_from_list_name(list_name) :
    return '/home/dwiel/axpress/%s_list' % hash(list_name)
  
  def list_add(vars) :
    f = open(filename_from_list_name(vars['list_name']), 'a')
    print >>f, vars['item']
    f.close()
  
  axpress.register_translation({
    'name' : 's list add',
    'input' : """
      x[axpress.is] = "add %item% (to |)(my |the |)%list_name%( list|)"
    """,
    'output' : """
      x[axpress.is] = "show %list_name% list"
    """,
    'function' : list_add
  })

  def list_show(vars) :
    try :
      f = open(filename_from_list_name(vars['list_name']), 'r')
      lines = [line.strip() for line in f.read().split('\n') if line.strip()]
      f.close()
    except IOError :
      lines = []

    vars['html'] = Template(u"""## -*- coding: utf-8 -*-
      <ul>
        % for item in items:
          <li>${item}
        % endfor
      </ul>
    """).render_unicode(items = lines)
  axpress.register_translation({
    'name' : 'show list list',
    'input' : """
      x[axpress.is] = "show (my |)%list_name%( list|)"
    """,
    'output' : """
      x[simple_display.text] = _html
    """,
    'function' : list_show,
  })

  def remove_list(vars) :
    f = open(filename_from_list_name(vars['list_name']), 'r')
    lines = f.read().split('\n')
    f.close()
    
    if vars['item'] not in lines :
      raise Exception("%s was not in your %s list" % (vars['item'], vars['list_name']))
    else :
      lines = [line for line in lines if line != vars['item']]
    
    f = open(filename_from_list_name(vars['list_name']), 'w')
    for line in lines :
      print >>f, line
    f.close()
  axpress.register_translation({
    'name' : 'remove list',
    'input' : """
      x[axpress.is] = "(remove|get rid of) %item% (from |)(my |)%list_name%( list|)"
    """,
    'output' : """
      x[axpress.is] = "show %list_name% list"
    """,
    'function' : remove_list,
  })
