

def loadTranslations(axpress, n) :
  pass
  #def parse_number(vars) :
    #vars['number'] = float(vars['x'])
  #axpress.register_translation({
    #n.meta.name : 'number',
    #n.meta.input : """
      #x[axpress.is] = "%x%"
    #""",
    #n.meta.output : """
      #x[math.number] = _number
    #""",
    #n.meta.function : parse_number,
  #})

  #axpress.register_translation({
    #n.meta.name : 's sum',
    #n.meta.input : """
      #sum[axpress.is] = "%x_str%( |)+( |)%y_str%"
    #""",
    #n.meta.output : """
      #x[axpress.is] = "%x_str%"
      #y[axpress.is] = "%y_str%"
      #sum[math.number] = math.sum(x, y)
    #""",
  #})
  
  #def do_sum(vars) :
    #vars['sum'] = vars['x'] + vars['y']
  #axpress.register_translation({
    #n.meta.name : 'sum',
    #n.meta.input : """
      #xt[math.number] = _x
      #yt[math.number] = _y
    #""",
    #n.meta.output : """
      #math.sum(xt, yt) = _sum
    #""",
    #n.meta.function : do_sum,
  #})
