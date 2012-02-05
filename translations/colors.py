def loadTranslations(axpress, n) :
  n.bind('color', '<http://dwiel.net/express/color/0.1/>')
  n.bind('html', '<http://dwiel.net/express/html/0.1/>')

  def red(vars) :
    vars['c'] = "FF0000"
  axpress.register_translation({
    'name' : 'is red',
    'input' : """
      color[axpress.is] = "red"
    """,
    'output' : """
      color[html.color] = _c
    """,
    'function' : red,
  })
  
  """
  sum of %number1% and %number2%
  fn : number1 + number2
    
  # there is how the strings percolate down through the translations
  # and
  # there is how the string is input from the user
  """
  
  def green(vars) :
    vars['c'] = "00FF00"
  axpress.register_translation({
    'name' : 'is green',
    'input' : """
      color[axpress.is] = "green"
    """,
    'output' : """
      color[html.color] = _c
    """,
    'function' : green,
  })
  
  def invert_color(vars) :
    vars['rout'] = 255 - vars['rin']
    vars['gout'] = 255 - vars['gin']
    vars['bout'] = 255 - vars['bin']
  axpress.register_translation({
    'name' : 'invert',
    'input' : """
      color[html.color_red]   = _rin
      color[html.color_green] = _gin
      color[html.color_blue]  = _bin
      color[color.invert] = inverted_color
    """,
    'output' : """
      inverted_color[html.color_red]   = _rout
      inverted_color[html.color_green] = _gout
      inverted_color[html.color_blue]  = _bout
    """,
    'function' : invert_color,
  })
  
  def html_color_rgb(vars) :
    # hex to rgb
    vars['red']  = int(vars['c'][0:2], 16)
    vars['green'] = int(vars['c'][2:4], 16)
    vars['blue'] = int(vars['c'][4:6], 16)
  axpress.register_translation({
    'name' : 'html color to rgb',
    'input' : """
      color[html.color] = _c
    """,
    'output' : """
      color[html.color_red] = _red
      color[html.color_green] = _green
      color[html.color_blue] = _blue
    """,
    'function' : html_color_rgb,
    'inverse_function' : 'html rgb to color',
  })
  
  def html_rgb_color(vars) :
    # rgb_to_hex
    vars['c'] = "%0.2X%0.2X%0.2X" % (
      vars['red'], vars['green'], vars['blue']
    )
  axpress.register_translation({
    'name' : 'html rgb to color',
    'input' : """
      color[html.color_red] = _red
      color[html.color_green] = _green
      color[html.color_blue] = _blue
    """,
    'output' : """
      color[html.color] = _c
    """,
    'function' : html_rgb_color,
    'inverse_function' : 'html color to rgb',
  })
  
  axpress.register_translation({
    'name' : 'is inverse of color',
    'input' : """
      icolor[axpress.is] = "inverse of %color%"
    """,
    'output' : """
      color[html.color] = _c
      color[color.invert] = icolor
      icolor[html.color] = _ic
    """,
    'function' : red,
  })