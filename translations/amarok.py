import os

def loadTranslations(axpress, n) :
  n.bind('amarok', '<http://dwiel.net/axpress/amarok/0.1/>')
  n.bind('playlist', '<http://dwiel.net/express/playlist/0.1/>')
  n.bind('music', '<http://dwiel.net/axpress/music/0.1/>')

  def get_amarok_artist(vars):
    vars['artist_name'] = os.popen('dcop amarok player artist').next()[:-1]
    if vars['artist_name'] == '' :
      return []
  axpress.register_translation({
    n.meta.name : 'get amarok artist',
    n.meta.input : """
      amarok.amarok[amarok.artist] = artist
    """,
    n.meta.output : """
      artist[music.artist_name] = _artist_name
    """,
    n.meta.function : get_amarok_artist,
  })

  def playlist_enuque(vars):
    pass
  axpress.register_translation({
    n.meta.name : 'playlist enqueue',
    n.meta.input : """
      playlist.enqueue(playlist.playlist, track) = True
      track[file.url] = url
    """,
    n.meta.output : [
    ],
    n.meta.function : playlist_enuque,
    n.meta.side_effect : True,
  })
  
