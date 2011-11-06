from mako.template import Template

def loadTranslations(axpress, n) :
  n.bind('todo', '<http://dwiel.net/axpress/todo/0.1/>')
  n.bind('simple_display', '<http://dwiel.net/axpress/simple_display/0.1/>')
  
  def todo_add(vars) :
    f = open('/home/dwiel/axpress/todolist', 'a')
    print >>f, vars['item']
    f.close()
  
  axpress.register_translation({
    n.meta.name : 's todo add',
    n.meta.input : """
      x[axpress.is] = "add %item% (to |)(my |the |)todo( list|)"
    """,
    n.meta.output : """
      x[axpress.is] = "show todo list"
    """,
    n.meta.function : todo_add
  })

  def todo_show(vars) :
    print 'todo show'
    f = open('/home/dwiel/axpress/todolist', 'r')
    lines = [line.strip() for line in f.read().split('\n') if line.strip()]
    f.close()

    vars['html'] = Template(u"""## -*- coding: utf-8 -*-
      <ul>
        % for item in items:
          <li>${item}
        % endfor
      </ul>
    """).render_unicode(items = lines)
    print vars['html']
  axpress.register_translation({
    n.meta.name : 'show todo list',
    n.meta.input : """
      x[axpress.is] = "(show |)(my |)todo( list|)"
    """,
    n.meta.output : """
      x[simple_display.text] = _html
    """,
    n.meta.function : todo_show,
  })

  def remove_todo(vars) :
    f = open('/home/dwiel/axpress/todolist', 'r')
    lines = f.read().split('\n')
    f.close()
    
    print lines, repr(vars['item'])
    if vars['item'] not in lines :
      raise Exception("%s was not in your todo list" % vars['item'])
    else :
      lines = [line for line in lines if line != vars['item']]
    
    f = open('/home/dwiel/axpress/todolist', 'w')
    for line in lines :
      print >>f, line
    f.close()
  axpress.register_translation({
    n.meta.name : 'remove todo',
    n.meta.input : """
      x[axpress.is] = "remove %item% (from |)(my |)todo( list|)"
    """,
    n.meta.output : """
      x[axpress.is] = "show todo list"
    """,
    n.meta.function : remove_todo,
  })








