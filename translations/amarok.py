import os

def loadTranslations(axpress) :
  axpress.n.bind('amarok', '<http://dwiel.net/axpress/amarok/0.1/>')
  axpress.n.bind('playlist', '<http://dwiel.net/express/playlist/0.1/>')
  axpress.n.bind('music', '<http://dwiel.net/axpress/music/0.1/>')

  def get_amarok_artist(vars):
    vars['artist_name'] = os.popen('dcop amarok player artist').next()[:-1]
    if vars['artist_name'] == '' :
      return []
  axpress.register_translation({
    'name' : 'get amarok artist',
    'input' : """
      amarok.amarok[amarok.artist] = artist
    """,
    'output' : """
      artist[music.artist_name] = _artist_name
    """,
    'function' : get_amarok_artist,
  })

  def playlist_enuque(vars):
    pass
  axpress.register_translation({
    'name' : 'playlist enqueue',
    'input' : """
      playlist.enqueue(playlist.playlist, track) = True
      track[file.url] = url
    """,
    'output' : [
    ],
    'function' : playlist_enuque,
    'side_effect' : True,
  })
  
