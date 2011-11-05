#import flickrapi

def loadTranslations(axpress, n) :
  def flickr_make_url(photo) :
    # 'http://farm{farm-id}.static.flickr.com/{server-id}/{id}_{secret}.jpg'
    # 'http://farm{farm-id}.static.flickr.com/{server-id}/{id}_{secret}_[mstb].jpg'
    return 'http://farm%s.static.flickr.com/%s/%s_%s_%s.jpg' % \
            (photo.attrib['farm'], photo.attrib['server'], photo.attrib['id'], photo.attrib['secret'], 'b')
  
  def flickr_photos_search(vars) :
    flickr = flickrapi.FlickrAPI('91a5290443e54ec0ff7bcd26328963cd', format='etree')
    photos = flickr.photos_search(tags=[vars['tag']])
    urls = []
    for photo in photos.find('photos').findall('photo') :
      urls.append(flickr_make_url(photo))
    # for now, limit it to 5 urls just to keep it reasonable since there isnt a
    # good query limit atm
    vars['url'] = urls[:5]
    
  axpress.register_translation({
    n.meta.name : 'flickr photos search',
    n.meta.input : [
      'image[flickr.tag] = _tag',
#     'image[flickr.tag] ?= tag', # TODO: ?= means optionally equal to
#     'optional(image[flickr.tag] = tag)',
#     'optional(image[flickr.user_id] = user_id)',
#     ...
    ],
    n.meta.output : [
      'image[file.url] = _url',
    ],
    n.meta.function : flickr_photos_search,
    n.cache.expiration_length : 2678400,
    n.meta.requires : 'flickrapi', # TODO: make this work
  })
  
  axpress.register_translation({
    n.meta.name : 'string: images with tag',
    n.meta.input : """
      image[axpress.is] = "images tagged %tag%"
    """,
    n.meta.output : """
      image[flickr.tag] = tag
    """,
  })
  
  # this terminates a string match and binds it as an output variable
  def string_tag(vars):
    vars['tag_out'] = vars['tag_str']
  axpress.register_translation({
    n.meta.name : 'string: tag?',
    n.meta.input : """
      tag[axpress.is] = "%tag_str%"
    """,
    n.meta.output : """
      tag[axpress.is] = _tag_out
    """,
    n.meta.function : string_tag,
  })
  
