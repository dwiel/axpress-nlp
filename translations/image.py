from itertools import izip

def loadTranslations(axpress) :  
  axpress.n.bind('pil', '<http://dwiel.net/express/python/pil/0.1/>')
  axpress.n.bind('image', '<http://dwiel.net/express/image/0.1/>')
  axpress.n.bind('html', '<http://dwiel.net/express/html/0.1/>')
  axpress.n.bind('color', '<http://dwiel.net/express/color/0.1/>')

  def load_image(vars) :
    from PIL import Image
    im = Image.open(vars['filename'])
    im.load() # force the data to be loaded (Image.open is lazy)
    vars['pil_image'] = im
  axpress.register_translation({
    'name' : 'load image',
    'input' : """
      image[file.filename] = _filename
    """,
    'output' : """
      image[pil.image] = _pil_image
    """,
    'function' : load_image,
  })
    
  def image_thumbnail(vars) :
    from PIL import Image
    im = vars['pil_image']
    im.thumbnail((int(vars['x']), int(vars['y'])), Image.ANTIALIAS)
    vars['thumb_image'] = im
  axpress.register_translation({
    'name' : 'image thumbnail',
    'input' : """
      image[pil.image] = _pil_image
      thumb = image.thumbnail(image, _x, _y)
    """,
    'output' : """
      thumb[pil.image] = _thumb_image
    """,
    'function' : image_thumbnail,
  })

  def image_pixel(vars) :
    im = vars['pil_image']
    vars['color'] = im.getpixel((int(vars['x']), int(vars['y'])))
  axpress.register_translation({
    'name' : 'image pixel',
    'input' : """
      image[pil.image] = _pil_image
      pixel = image.pixel(image, _x, _y)
    """,
    'output' : """
      pixel[pil.color] = _color
    """,
    'function' : image_pixel,
  })
  
  def html_color(vars) :
    color = vars['pil_color']
    vars['html_color'] = hex(color[0])[2:]+hex(color[1])[2:]+hex(color[2])[2:]
  axpress.register_translation({
    'name' : 'html color',
    'input' : """
      pixel[pil.color] = _pil_color
    """,
    'output' : """
      pixel[html.color] = _html_color
    """,
    'function' : html_color,
  })
  
  axpress.register_translation({
    'name' : 'image average color',
    'input' : """
      image[pil.image] = _pil_image
    """,
    'output' : """
      image[image.average_color] = color
      image.thumbnail(image, 1, 1) = thumb
      image.pixel(thumb, 0, 0) = pixel
      pixel[pil.color] = color
    """,
  })
  
  
  
  #def color_distance(vars):
    #vars['color_diff'] = vars['pil_color1'] - vars['pil_color2']
    #print 'color_diff',prettyquery(vars['color_diff'])
  #axpress.register_translation({
    #'name' : 'color distance',
    #'input' : """
      #color1[pil.color] = _pil_color1
      #color2[pil.color] = _pil_color2
      #color.distance(color1, color2) = foo[type.number]
    #""",
    #'output' : """
      #foo[type.number] = distance
    #""",
    #'function' : color_distance,
  #})
  
  def color_distance_red(vars):
    diff = tuple([x-y for x,y in izip((255,0,0), vars['pil_color2'])])
    vars['distance'] = sum([x*x for x in diff])
  axpress.register_translation({
    'name' : 'color distance',
    'input' : """
      color2[pil.color] = _pil_color2
      color.distance(color.red, color2) = foo[type.number]
    """,
    'output' : """
      foo[type.number] = _distance
    """,
    'function' : color_distance_red,
  })
