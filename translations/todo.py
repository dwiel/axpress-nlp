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
  
  def get_list(vars) :
    vars['filename'] = filename_from_list_name(vars['list_name'])

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
      x[axpress.list_name] = "%list_name%"
    """,
    'function' : list_add,
  })

  axpress.register_translation({
    'name' : 's list add2',
    'input' : """
      x[axpress.is] = "add %item% (to |)(my |the |)%list_name%( list|)"
    """,
    'output' : """
      f[file.filename] = _filename
      ret = file.append(f, item)
      x[axpress.list_name] = axpress.after(ret, "%list_name%")
    """,
    'function' : get_list,
  })
  
  def after(vars) :
    print 'after', vars
    vars['sum'] = 3
  axpress.register_translation({
    'name' : 'after',
    'input' : """
      out = axpress.after(_ret, _val)
    """,
    'output' : """
      out[axpress.val] = _sum
    """,
    'function' : after,
  })
  
  axpress.register_translation({
    'name' : 'get list 2',
    'input' : """
      x[axpress.list_name] = "%list_name%"
    """,
    'output' : """
      f[file.filename] = _filename
      f[file.lines] = lines
      x[axpress.list] = lines
    """,
    'function' : get_list,
  })

  """
  This rule 
  """
  axpress.register_translation({
    'name' : 'get list',
    'input' : """
      x[axpress.is] = "(what is on |what's on |whats on |show )(my |)%list_name%( list|)"
    """,
    'output' : """
      x[axpress.list_name] = "%list_name%"
    """,
  })
  
  def show_list(vars) :
    print vars
    print 'list', repr(vars['list'])
    vars['html'] = Template(u"""## -*- coding: utf-8 -*-
      <ul>
        % for item in items:
          <li>${item}
        % endfor
      </ul>
    """).render_unicode(items = vars['list'])
  axpress.register_translation({
    'name' : 'show list',
    'input' : """
      x[axpress.list] = _list
    """,
    'output' : """
      x[simple_display.text] = _html
    """,
    'function' : show_list,
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
