import os
import re
import urllib
import time

import xml.etree.ElementTree

from htmlentitydefs import name2codepoint
# for some reason, python 2.5.2 doesn't have this one (apostrophe)
name2codepoint['#39'] = 39

def unescape(s):
  "unescape HTML code refs; c.f. http://wiki.python.org/moin/EscapingHtml"
  return re.sub('&(%s);' % '|'.join(name2codepoint),
          lambda m: unichr(name2codepoint[m.group(1)]), s)

def loadTranslations(axpress) :
  axpress.n.bind('music', '<http://dwiel.net/axpress/music/0.1/>')
  axpress.n.bind('lastfm', '<http://dwiel.net/axpress/lastfm/0.1/>')

  # WARNING: the output of this transformation does not always result in > 1 
  # set of bindings.  (If the artist is not in lastfm - or if there is no inet?)
  re_lastfm_similar = re.compile('(.*?),(.*?),(.+)')
  def lastfm_similar(vars) :
    if not os.path.exists('.lastfmcache') :
      os.mkdir('.lastfmcache')
    filename = '.lastfmcache/artist_%s_similar' % urllib.quote(vars['artist_name'])
    filename = filename.replace('%','_')
    if not os.path.exists(filename) :
      cmd = 'wget http://ws.audioscrobbler.com/2.0/artist/%s/similar.txt -O %s' % (urllib.quote(vars['artist_name']), filename)
      ret = os.system(cmd)
      print cmd, ret
    
      lasttime = time.time()
      while lasttime + 1 < time.time() :
        # sleep a little
        time.sleep(0)
    
    f = open(filename)
    
    #vars['setlasttime'](time.time())
    
    outputs = []
    for line in f :
      line = unescape(line.strip())
      g = re_lastfm_similar.match(line)
      outputs.append({
        'similarity_measure' : float(g.group(1)),
        'mbid' : g.group(2),
        'name' : g.group(3),
      })
    ret = outputs[:10]
    #print 'vars', prettyquery(ret)
    return ret

  axpress.register_translation({
    'name' : 'last.fm similar artists',
    'input' : """
      artist[music.artist_name] = _artist_name
      artist[lastfm.similar_to] = similar_artist
    """,
    'output' : """
      artist[lastfm.similar_to] = similar_artist
      similar_artist[lastfm.similarity_measure] = _similarity_measure
      similar_artist[lastfm.mbid] = _mbid
      similar_artist[lastfm.artist_name] = _name
    """,
    'function' : lastfm_similar,
    'scale' : 100,
    'expected_time' : 1,
    'cache_expiration_length' : 2678400, # 1 month in seconds
  })
  
  def lastfm_user_recent_tracks(vars) :
    filename = '/home/dwiel/.lastfmcache/user_%s_recent_tracks' % urllib.quote(vars['user_name'])
    filename = filename.replace('%','_')
    # use the cached version if it exists and is no more than 10 mins old
    if not os.path.exists(filename) or (time.time() - os.stat(filename)[8] > 2000):
      os.system('wget "http://ws.audioscrobbler.com/2.0/?method=user.getrecenttracks&user=%s&api_key=41f38f5e3d328f6ff186835d06780989" -O %s' % (urllib.quote(vars['user_name']), filename))
      
      lasttime = time.time()
      while lasttime + 1 < time.time() :
        # sleep a little
        time.sleep(0)
    
    print time.time() - os.stat(filename)[8]
    
    f = open(filename)
    etree = xml.etree.ElementTree.parse(f)
    results = []
    #for track in etree.findall('*/track') :
    track = etree.find('*/track')
    #result = {}
    result = vars
    artist = track.find('artist')
    result['artist_mbid'] = artist.attrib['mbid']
    result['artist_name'] = artist.text
    result['track_name'] = track.find('name').text
    album = track.find('album')
    result['album_mbid'] = album.attrib['mbid']
    result['album_name'] = album.text
    result['date_uts'] = track.find('date').attrib['uts']
    #results.append(result)
    
    
    #print result
    #return result
    #print(results)
    #return results
    
  #axpress.register_translation({
    #'name' : "last.fm user's recent tracks",
    #'input' : """
      #user[lastfm.user_name] = _user_name
      #user[lastfm.recent_track] = track
      #track[lastfm.album] = album
      #track[lastfm.artist] = artist
    #""",
    #'output' : """
      #artist[lastfm.mbid] = _artist_mbid
      #artist[lastfm.artist_name] = _artist_name
      #track[lastfm.track_name] = _track_name
      #album[lastfm.mbid] = _album_mbid
      #album[lastfm.album_name] = _album_name
      #track[lastfm.date_uts] = _date_uts
    #""",
    #'function' : lastfm_user_recent_tracks,
  #})
  axpress.register_translation({
    'name' : "last.fm user's recent tracks",
    'input' : """
      user[lastfm.user_name] = _user_name
      user[lastfm.recent_track] = track
      track[lastfm.artist] = artist
    """,
    'output' : """
      artist[lastfm.mbid] = _artist_mbid
      artist[lastfm.artist_name] = _artist_name
      track[lastfm.track_name] = _track_name
      track[lastfm.date_uts] = _date_uts
    """,
    'function' : lastfm_user_recent_tracks,
  })
  
  axpress.register_translation({
    'name' : "last.fm shorthand artist name",
    'input' : """
      track[lastfm.artist] = artist
      artist[lastfm.artist_name] = _artist_name
    """,
    'output' : """
      track[lastfm.artist_name] = _artist_name
    """,
  })
  
  axpress.register_translation({
    'name' : "lastfm.artist_name -> music.artist_name",
    'input' : """
      x[lastfm.artist_name] = _name
    """,
    'output' : """
      x[music.artist_name] = _name
    """,
  })
  
  axpress.register_translation({
    'name' : 'rdfs.label => music.artist_name',
    'input' : [
      'artist[rdfs.label] = artist_name',
    ],
    'output' : [
      'artist[music.artist_name] = artist_name',
    ],
    'function' : lambda x : None,
    'reversable' : True,
    'scale' : 1,
    'expected_time' : 0,
  })
  
  #axpress.register_translation({
    #'name' : "last.fm shorthand artist mbid",
    #'input' : """
      #track[lastfm.artist] = artist
      #artist[lastfm.mbid] = _artist_mbid
    #""",
    #'output' : """
      #track[lastfm.artist_mbid] = _artist_mbid
    #""",
  #})
  
  #axpress.register_translation({
    #'name' : "last.fm shorthand album mbid",
    #'input' : """
      #track[lastfm.album] = album
      #album[lastfm.mbid] = _album_mbid
    #""",
    #'output' : """
      #track[lastfm.album_mbid] = _album_mbid
    #""",
  #})

"(listen to|play) %artist% on last.fm"
