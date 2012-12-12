import urllib
import urllib2
import freebase
import json

from SimpleSPARQL.Exceptions import TranslationResponse

def loadTranslations(axpress) :  
  axpress.n.bind('freebase', '<http://dwiel.net/axpress/freebase/0.1/>')
  rule = axpress.rule

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
    'name' : 'author of book',
    'input' : """
      author[axpress.is] = "author of %book_str%"
    """,
    'output' : """
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
    'name' : 'author of book lookup',
    'input' : """
      book[freebase.guid] = _book_guid
      book[freebase.type] = '/book/written_work'
      book[freebase./book/written_work/author] = author
    """,
    'output' : """
      author[freebase.type] = '/book/author'
      author[freebase.guid] = _author_guid
    """,
    'function' : author_of_book
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
    'name' : 'book from title',
    'input' : """
      book[axpress.is] = "%title%"
    """,
    'input_function' : book_from_title_test,
    'output' : """
      book[freebase.guid] = _guid
      book[freebase.type] = '/book/written_work'
    """,
    'function' : book_from_title,
  })
  
  axpress.register_translation({
    'name' : 's albums by musician',
    'input' : """
      album[axpress.is] = "albums by %artist_s%"
    """,
    'output' : """
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
    #print result
    return result['album']
  
  axpress.register_translation({
    'name' : 'lookup albums by musician',
    'input' : """
      artist[freebase.mid] = _artist_mid
      artist[freebase.type] = '/music/artist'
      album[freebase./music/album/artist] = artist
    """,
    'output' : """
      album[freebase.mid] = _mid
      album[freebase.name] = _name
    """,
    'function' : lookup_albums_by_musician,
  })
  
  axpress.register_translation({
    'name' : 's members in musical_group',
    'input' : """
      member[axpress.is] = "(band |)members (in|of) %group_s%"
    """,
    'output' : """
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
    'name' : 'lookup members in group',
    'input' : """
      group[freebase.mid] = _mid
      group[freebase.type] = '/music/musical_group'
      group[freebase./music/group_member] = member
    """,
    'output' : """
      member[freebase.mid] = _mid
      member[freebase.name] = _name
    """,
    'function' : lookup_members_in_group,
  })
  
  #axpress.register_translation({
    #'name' : 's birthday',
    #'input' : """
      #birthday[axpress.is] = "%person_s%'s birthday"
    #""",
    #'output' : """
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
    #'name' : 'lookup birthday',
    #'input' : """
      #person[freebase.mid] = _mid
      #person[freebase.type] = '/people/person'
    #""",
    #'output' : """
      #person[freebase./people/person/date_of_birth] = _birthday
    #""",
    #'function' : lookup_birthday
  #})
  
  axpress.register_translation({
    'name' : 's birthplace',
    'input' : """
      birthplace[axpress.is] = "%person_s% birthplace"
    """,
    'output' : """
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
    #print result
    return result['place_of_birth']
  
  axpress.register_translation({
    'name' : 'lookup birthplace',
    'input' : """
      person[freebase.type] = '/people/person'
      person[freebase.mid] = _person_mid
    """,
    'output' : """
      person[freebase./people/person/place_of_birth] = birthplace
      birthplace[freebase.mid] = _mid
      birthplace[freebase.name] = _name
    """,
    'function' : lookup_birthplace,
  })
  
  # NOTE: this seems to always get matched
  axpress.register_translation({
    'name' : 'remove the',
    'input' : """
      x[axpress.is] = "the %anything%"
    """,
    'output' : """
      x[axpress.is] = "%anything%"
    """
  }, step_size = 0)
  
  def lookup_location_lat_lon(vars) :
    print 'mid', vars['mid']
    result = freebase.mqlread({
      "mid" : vars['mid'],
      "type" : "/location/location",
      "/location/location/geolocation" : {
        "latitude" : None,
        "longitude" : None,
      },
    })
    if result :
      return result['/location/location/geolocation']
    else :
      # the first thing didn't match, maybe see if it is containedby something that has a geolocation
      # this isn't necessarily the best thing to do, but it seems to work for now
      result = freebase.mqlread({
        "mid" : vars['mid'],
        "type" : "/location/location",
        "/location/location/containedby" : [{
          "/location/location/geolocation" : {
            "latitude" : None,
            "longitude" : None,
          },
          "/location/location/area" : None,
          "sort" : "/location/location/area",
          "limit" : 1,
        }],
      })
      if result :
        return result['/location/location/containedby'][0]['/location/location/geolocation']
      else :
        raise Exception('location not found')
  
  axpress.register_translation({
    'name' : 'lookup location lat lon',
    'input' : """
      location[freebase.mid] = _mid
      location[freebase.type] = '/location/location'
    """,
    'output' : """
      location[freebase./location/location/geolocation] = geo
      geo[freebase./location/geocode/latitude] = _latitude
      geo[freebase./location/geocode/longitude] = _longitude
    """,
    'function' : lookup_location_lat_lon,
  })
  
  def curl(url) :
    import subprocess
    p = subprocess.Popen('curl --silent "%s"' % url, shell=True, stdout=subprocess.PIPE)
    return p.stdout.read()
  
  def freebase_search_failure(vars) :
    """ called when the freebase search fails """
    if 'type' in vars :
      t = vars['type']
      if '/' in t :
        typename = t[t.rfind('/')+1:]
      else :
        typename = t
      typename = "a "+typename
    else :
      typename = "anything"
    
    raise TranslationResponse(
      "couldn't find %s by the name %s" % (
        typename, vars['title']
      )
    )
    
  def freebase_search(vars) :
    q = {
      'query' : vars['title'],
      'html_escape' : 'false',
      'html_encode' : 'false',
      'escape' : 'false',
      'limit' : 5
    }
    # not all translations which use freebase_search pass in a type var
    if 'type' in vars :
      q['type'] = vars['type']
    ret = json.loads(curl(
      'https://www.googleapis.com/freebase/v1/search?' + urllib.urlencode(q)
    ))
    
    # look for possible error cases
    if ret['status'] != '200 OK' :
      raise Exception("freebase didn't work ...")
    if 'code' in ret and ret['code'] == '/api/status/error' :
      raise Exception("error in freebase search - %s" % ret['message'])
    if not ret['result'] :
      freebase_search_failure(vars)
    
    result = ret['result'][0]
    if result['score'] < 25 :
      print result
      freebase_search_failure(vars)
    
    # everything worked
    vars['mid'] = result['mid']
    vars['name'] = result['name']
  axpress.register_translation({
    'name' : 'freebase search',
    'input' : """
      book[axpress.is] = "%title%"
      book[freebase.type] = _type
    """,
    'output' : """
      book[freebase.mid] = _mid
    """,
    'function' : freebase_search,
  })


  def freebase_blurb(vars) :
    try :
      vars['blurb'] = freebase.blurb(vars['mid']).decode('<utf-8>')
    except freebase.api.MetawebError :
      vars['blurb'] = u'no blurb'
  axpress.register_translation({
    'name' : 'freebase blurb',
    'input' : """
      o[freebase.mid] = _mid
    """,
    'output' : """
      o[freebase.blurb] = _blurb
    """,
    'function' : freebase_blurb,
  })
  
  rule("what is x", """
    o[axpress.is] = "what is (a |)%title%"
  """, """
    o[freebase.mid] = _mid
    o[freebase.name] = _name
  """, freebase_search)

  rule("what is x", """
    o[axpress.is] = "what is %q%(\?|)"
  """, """
    o[axpress.is] = "%q%"
  """, step_size=0)
