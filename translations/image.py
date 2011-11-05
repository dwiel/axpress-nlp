from itertools import izip
from PIL import Image

def loadTranslations(axpress, n) :  
  n.bind('pil', '<http://dwiel.net/express/python/pil/0.1/>')
  n.bind('image', '<http://dwiel.net/express/image/0.1/>')
  n.bind('html', '<http://dwiel.net/express/html/0.1/>')

  def load_image(vars) :
    im = Image.open(vars['filename'])
    im.load() # force the data to be loaded (Image.open is lazy)
    vars['pil_image'] = im
  axpress.register_translation({
    n.meta.name : 'load image',
    n.meta.input : """
      image[file.filename] = _filename
    """,
    n.meta.output : """
      image[pil.image] = _pil_image
    """,
    n.meta.function : load_image,
  })
    
  def image_thumbnail(vars) :
    im = vars['pil_image']
    im.thumbnail((int(vars['x']), int(vars['y'])), Image.ANTIALIAS)
    vars['thumb_image'] = im
  axpress.register_translation({
    n.meta.name : 'image thumbnail',
    n.meta.input : """
      image[pil.image] = _pil_image
      thumb = image.thumbnail(image, _x, _y)
    """,
    n.meta.output : """
      thumb[pil.image] = _thumb_image
    """,
    n.meta.function : image_thumbnail,
  })

  def image_pixel(vars) :
    im = vars['pil_image']
    vars['color'] = im.getpixel((int(vars['x']), int(vars['y'])))
  axpress.register_translation({
    n.meta.name : 'image pixel',
    n.meta.input : """
      image[pil.image] = _pil_image
      pixel = image.pixel(image, _x, _y)
    """,
    n.meta.output : """
      pixel[pil.color] = _color
    """,
    n.meta.function : image_pixel,
  })
  
  def html_color(vars) :
    color = vars['pil_color']
    vars['html_color'] = hex(color[0])[2:]+hex(color[1])[2:]+hex(color[2])[2:]
  axpress.register_translation({
    n.meta.name : 'html color',
    n.meta.input : """
      pixel[pil.color] = _pil_color
    """,
    n.meta.output : """
      pixel[html.color] = _html_color
    """,
    n.meta.function : html_color,
  })
  
  axpress.register_translation({
    n.meta.name : 'image average color',
    n.meta.input : """
      image[pil.image] = _pil_image
    """,
    n.meta.output : """
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
    #n.meta.name : 'color distance',
    #n.meta.input : """
      #color1[pil.color] = _pil_color1
      #color2[pil.color] = _pil_color2
      #color.distance(color1, color2) = foo[type.number]
    #""",
    #n.meta.output : """
      #foo[type.number] = distance
    #""",
    #n.meta.function : color_distance,
  #})
  
  def color_distance_red(vars):
    diff = tuple([x-y for x,y in izip((255,0,0), vars['pil_color2'])])
    vars['distance'] = sum([x*x for x in diff])
  axpress.register_translation({
    n.meta.name : 'color distance',
    n.meta.input : """
      color2[pil.color] = _pil_color2
      color.distance(color.red, color2) = foo[type.number]
    """,
    n.meta.output : """
      foo[type.number] = _distance
    """,
    n.meta.function : color_distance_red,
  })
