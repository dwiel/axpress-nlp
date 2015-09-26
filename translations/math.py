

def loadTranslations(axpress) :
  axpress.n.bind('math',    '<http://dwiel.net/express/math/0.1/>')
  
  #def parse_number(vars) :
    #vars['number'] = float(vars['x'])
  #axpress.register_translation({
    #'name' : 'number',
    #'input' : """
      #x[axpress.is] = "%x%"
    #""",
    #'output' : """
      #x[math.number] = _number
    #""",
    #'function' : parse_number,
  #})

  #axpress.register_translation({
    #'name' : 's sum',
    #'input' : """
      #sum[axpress.is] = "%x_str%( |)+( |)%y_str%"
    #""",
    #'output' : """
      #x[axpress.is] = "%x_str%"
      #y[axpress.is] = "%y_str%"
      #sum[math.number] = math.sum(x, y)
    #""",
  #})
  
  #def do_sum(vars) :
    #vars['sum'] = vars['x'] + vars['y']
  #axpress.register_translation({
    #'name' : 'sum',
    #'input' : """
      #xt[math.number] = _x
      #yt[math.number] = _y
    #""",
    #'output' : """
      #math.sum(xt, yt) = _sum
    #""",
    #'function' : do_sum,
  #})
