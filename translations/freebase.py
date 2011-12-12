import urllib
import urllib2
import freebase
import json

def loadTranslations(axpress, n) :  
  n.bind('freebase', '<http://dwiel.net/axpress/freebase/0.1/>')

  # STRING MUSINGS
  """
  with this method, the output isn't so much an assertion that the output is
  true given the input, but that it could be true and we should continue 
  exploring with some new information to see if it is.
  
  it is possible that this kind of search will require that the compiler is more
  precise than it currently is.  It might need to do possible cases, or it might
  need to support quick fns, which are cheaper to evaluate during compilation 
  than registering as possible and dealing with later.  These will obviously
  need to also be free of side-effects
  """
  axpress.register_translation({
    n.meta.name : 'author of book',
    n.meta.input : """
      author[axpress.is] = "author of %book_str%"
    """,
    n.meta.output : """
      # boilerplate
      book[axpress.is] = "%book_str%"
      
      # think of this as a query rather than a set of facts (even though both
      # are true)
      book[freebase.type] = '/book/written_work'
      book[freebase./book/written_work/author] = author
      author[freebase.type] = '/book/author'
    """,
  })
  
  def author_of_book(vars) :
    vars['author_guid'] = "author" + vars['book_guid']
  axpress.register_translation({
    n.meta.name : 'author of book lookup',
    n.meta.input : """
      book[freebase.guid] = _book_guid
      book[freebase.type] = '/book/written_work'
      book[freebase./book/written_work/author] = author
    """,
    n.meta.output : """
      author[freebase.type] = '/book/author'
      author[freebase.guid] = _author_guid
    """,
    n.meta.function : author_of_book
  })
  
  def book_from_title(vars) :
    if vars['title'] == 'Gaviotas' :
      vars['guid'] = '9202a8c04000641f800000000c770bee'
    else :
      vars['guid'] = ''
  def book_from_title_test(vars) :
    if vars['title'] == 'Gaviotas' :
      return True
  axpress.register_translation({
    n.meta.name : 'book from title',
    n.meta.input : """
      book[axpress.is] = "%title%"
    """,
    n.meta.input_function : book_from_title_test,
    n.meta.output : """
      book[freebase.guid] = _guid
      book[freebase.type] = '/book/written_work'
    """,
    n.meta.function : book_from_title,
  })
  
  axpress.register_translation({
    n.meta.name : 's albums by musician',
    n.meta.input : """
      album[axpress.is] = "albums by %artist_s%"
    """,
    n.meta.output : """
      artist[axpress.is] = "%artist_s%"
      album[freebase./music/album/artist] = artist
      artist[freebase.type] = '/music/artist'
    """,
  })
  
  def lookup_albums_by_musician(vars) :
    result = freebase.mqlread({
      "mid" : vars['artist_mid'],
      "type" : "/music/artist",
      "album" : [{
        "name" : None,
        "mid" : None,
      }]
    })
    print result
    return result['album']
  
  axpress.register_translation({
    n.meta.name : 'lookup albums by musician',
    n.meta.input : """
      artist[freebase.mid] = _artist_mid
      artist[freebase.type] = '/music/artist'
      album[freebase./music/album/artist] = artist
    """,
    n.meta.output : """
      album[freebase.mid] = _mid
      album[freebase.name] = _name
    """,
    n.meta.function : lookup_albums_by_musician,
  })
  
  axpress.register_translation({
    n.meta.name : 's members in musical_group',
    n.meta.input : """
      member[axpress.is] = "members in %group_s%"
    """,
    n.meta.output : """
      group[axpress.is] = "%group_s%"
      group[freebase.type] = '/music/musical_group'
      group[freebase./music/group_member] = member
    """,
  })
  
  def lookup_members_in_group(vars) :
    # TODO: /music/musical_group/member doesn't have a name
    result = freebase.mqlread({
      "mid" : vars['mid'],
      "type" : '/music/musical_group',
      "member" : [{
        "/music/group_membership/member" : {
          "mid" : None,
          "name" : None,
        }
      }]
    })
    return [member[u'/music/group_membership/member'] for member in result['member']]
  
  axpress.register_translation({
    n.meta.name : 'lookup members in group',
    n.meta.input : """
      group[freebase.mid] = _mid
      group[freebase.type] = '/music/musical_group'
      group[freebase./music/group_member] = member
    """,
    n.meta.output : """
      member[freebase.mid] = _mid
      member[freebase.name] = _name
    """,
    n.meta.function : lookup_members_in_group,
  })
  
  #axpress.register_translation({
    #n.meta.name : 's birthday',
    #n.meta.input : """
      #birthday[axpress.is] = "%person_s%'s birthday"
    #""",
    #n.meta.output : """
      #person[axpress.is] = "%person_s%"
      #person[freebase.type] = '/people/person'
      #person[freebase./people/person/date_of_birth] = birthday
    #""",
  #})
  
  #def lookup_birthday(vars) :
    #result = freebase.mqlread({
      #"mid" : vars['mid'],
      #"type" : "/people/person",
      #"birthday" : None,
    #})
    #print result
    #return result['birthday']
  
  #axpress.register_translation({
    #n.meta.name : 'lookup birthday',
    #n.meta.input : """
      #person[freebase.mid] = _mid
      #person[freebase.type] = '/people/person'
    #""",
    #n.meta.output : """
      #person[freebase./people/person/date_of_birth] = _birthday
    #""",
    #n.meta.function : lookup_birthday
  #})
  
  axpress.register_translation({
    n.meta.name : 's birthplace',
    n.meta.input : """
      birthplace[axpress.is] = "%person_s% birthplace"
    """,
    n.meta.output : """
      person[axpress.is] = "%person_s%"
      person[freebase.type] = '/people/person'
      person[freebase./people/person/place_of_birth] = birthplace
      birthplace[freebase.type] = '/location/location'
    """,
  })
  
  def lookup_birthplace(vars) :
    result = freebase.mqlread({
      "mid" : vars['person_mid'],
      "type" : "/people/person",
      "place_of_birth" : {
        "mid" : None,
        "name" : None,
      },
    })
    print result
    return result['place_of_birth']
  
  axpress.register_translation({
    n.meta.name : 'lookup birthplace',
    n.meta.input : """
      person[freebase.mid] = _person_mid
      person[freebase.type] = '/people/person'
    """,
    n.meta.output : """
      person[freebase./people/person/place_of_birth] = birthplace
      birthplace[freebase.mid] = _mid
      birthplace[freebase.name] = _name
    """,
    n.meta.function : lookup_birthplace,
  })
  
  # NOTE: this seems to always get matched
  axpress.register_translation({
    n.meta.name : 'remove the',
    n.meta.input : """
      x[axpress.is] = "the %anything%"
    """,
    n.meta.output : """
      x[axpress.is] = "%anything%"
    """
  })
  
  def lookup_location_lat_lon(vars) :
    result = freebase.mqlread({
      "mid" : vars['mid'],
      "type" : "/location/location",
      "/location/location/geolocation" : {
        "latitude" : None,
        "longitude" : None,
      },
    })
    return result['/location/location/geolocation']
  
  axpress.register_translation({
    n.meta.name : 'lookup location lat lon',
    n.meta.input : """
      location[freebase.mid] = _mid
      location[freebase.type] = '/location/location'
    """,
    n.meta.output : """
      location[freebase./location/location/geolocation] = geo
      geo[freebase./location/geocode/latitude] = _latitude
      geo[freebase./location/geocode/longitude] = _longitude
    """,
    n.meta.function : lookup_location_lat_lon,
  })
  
  def freebase_search(vars) :
    print('vars', vars)
    req = urllib2.urlopen("https://www.googleapis.com/freebase/v1/search", urllib.urlencode({
      'query' : vars['title'],
      'type' : vars['type'],
      'html_escape' : 'false',
      'html_encode' : 'false',
      'escape' : 'false',
      'limit' : 1}))
    ret = req.read().decode('<utf-8>')
    ret = json.loads(ret)
    
    if ret['status'] != '200 OK' :
      raise Exception("freebase didn't work ...")
    result = ret['result'][0]
    if result['score'] > 25 :
      vars['mid'] = result['mid']
    else :
      print('ret', ret['result'])
      raise Exception("couldn't find something by that name")
    
    #.encode("<utf-8>")
  axpress.register_translation({
    n.meta.name : 'freebase search',
    n.meta.input : """
      book[axpress.is] = "%title%"
      book[freebase.type] = _type
    """,
    n.meta.output : """
      book[freebase.mid] = _mid
    """,
    n.meta.function : freebase_search,
  })


  def freebase_blurb(vars) :
    try :
      return freebase.blurb(vars['mid']).decode('<utf-8>')
    except freebase.api.MetawebError :
      return u'no blurb'
  axpress.register_translation({
    n.meta.name : 'freebase blurb',
    n.meta.input : """
      o[freebase.mid] = _mid
    """,
    n.meta.output : """
      o[freebase.blurb] = _blurb
    """,
    n.meta.function : freebase_blurb,
  })
