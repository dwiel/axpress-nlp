# -*- coding: utf-8 -*-
from SimpleSPARQL import *
import os, random, re
from itertools import izip

def loadTranslations(axpress, n) :
	n.bind('rdfs', '<http://www.w3.org/2000/01/rdf-schema#>')
	n.bind('math', '<http://dwiel.net/express/math/0.1/>')
	n.bind('type', '<http://dwiel.net/express/type/0.1/>')
	n.bind('flickr', '<http://dwiel.net/express/flickr/0.1/>')
	n.bind('file', '<http://dwiel.net/express/file/0.1/>')
	n.bind('playlist', '<http://dwiel.net/express/playlist/0.1/>')
	n.bind('image', '<http://dwiel.net/express/image/0.1/>')
	n.bind('color', '<http://dwiel.net/express/color/0.1/>')
	n.bind('html', '<http://dwiel.net/express/html/0.1/>')
	n.bind('pil', '<http://dwiel.net/express/python/pil/0.1/>')
	n.bind('glob', '<http://dwiel.net/express/python/glob/0.1/>')
	n.bind('call', '<http://dwiel.net/express/call/0.1/>')
	n.bind('test', '<http://dwiel.net/express/test/0.1/>')
	
	n.bind('axpress', '<http://dwiel.net/axpress/0.1/>')
	n.bind('music', '<http://dwiel.net/axpress/music/0.1/>')
	n.bind('lastfm', '<http://dwiel.net/axpress/lastfm/0.1/>')
	n.bind('yahoo', '<http://dwiel.net/axpress/yahoo/0.1/>')
	n.bind('amarok', '<http://dwiel.net/axpress/amarok/0.1/>')
	n.bind('reference', '<http://dwiel.net/axpress/reference/0.1/>')
	n.bind('display', '<http://dwiel.net/axpress/display/0.1/>')
	n.bind('freebase', '<http://dwiel.net/axpress/freebase/0.1/>')
		#n.bind('test', '<http://dwiel.net/axpress/test/0.1/>')
	
## TODO: allow a 'function' to accept a variable number of arguments?
	#def sum(vars) :
		#if type(vars[n.var.number1]) == int and type(vars[n.var.number2]) == int :
			#vars[n.var.sum] = vars[n.var.number1] + vars[n.var.number2]
		#else :
			#raise Exception('cant add things that arent numbers .........')
	#axpress.register_translation({
		#n.meta.name : 'sum',
		#n.meta.input : [
			#[n.var.uri, n.var.any, n.var.number1],
			#[n.var.uri, n.var.any, n.var.number2],
		#],
		#n.meta.output : [
			#[n.var.uri, n.math.sum, n.var.sum]
		#],
##		n.meta.function : sum
	#})

	def _sum(vars) :
		vars['sum'] = vars['x'] + vars['y']
	axpress.register_translation({
		n.meta.name : 'sum',
		n.meta.input : """
			foo[test.x] = _x
			foo[test.y] = _y
		""",
		n.meta.output : [
			'foo[test.sum] = _sum',
		],
		n.meta.function : _sum,
	})
	
	def _add_one(vars) :
		vars['sum'] = vars['x'] + 1
	axpress.register_translation({
		n.meta.name : 'add_one',
		n.meta.input : """
			foo[test.x] = _x
		""",
		n.meta.output : [
			'foo[test.add_one] = _sum',
		],
		n.meta.function : _add_one,
	})
	
	def _add_two(vars) :
		vars['sum'] = vars['x'] + 2
	axpress.register_translation({
		n.meta.name : 'add_two',
		n.meta.input : """
			foo[test.x] = _x
		""",
		n.meta.output : [
			'foo[test.add_two] = _sum',
		],
		n.meta.function : _add_two,
	})
	
	"""
	uri[test.sum] = x + y
	uri[test.x] = x
	uri[test.y] = y
	"""
	
	def prod(vars) :
		vars['prod'] = float(vars['sum']) * vars['z']
	axpress.register_translation({
		n.meta.name : 'product',
		n.meta.input : [
			'uri[test.sum] = _sum',
			'uri[test.z] = _z',
		],
		n.meta.output : [
			'uri[test.prod] = _prod',
		],
		n.meta.function : prod,
	})
	
	def div(vars) :
		vars['div'] = float(vars['sum']) / vars['z']
	axpress.register_translation({
		n.meta.name : 'division',
		n.meta.input : [
			'uri[test.sum] = _sum',
			'uri[test.z] = _z',
		],
		n.meta.output : [
			'uri[test.div] = _div',
		],
		n.meta.function : div,
	})

	axpress.register_translation({
		n.meta.name : 'rdfs.label => music.artist_name',
		n.meta.input : [
			'artist[rdfs.label] = artist_name',
		],
		n.meta.output : [
			'artist[music.artist_name] = artist_name',
		],
		n.meta.function : lambda x : None,
		n.meta.reversable : True,
		n.meta.scale : 1,
		n.meta.expected_time : 0,
	})
	
	## note: this doesn't actually work ...
	## how could it?
	#def is_num(vars) :
		#vars['is_num'] = isinstance(vars['x'], (int, long, float))
		#print 'is_num:',vars['is_num']
	#axpress.register_translation({
		#n.meta.name : 'is_num',
		#n.meta.input : """
			#type.is_num(_x) = ?is_num
		#""",
		#n.meta.output : """
			#type.is_num(_x) = _is_num
		#""",
		#n.meta.function : is_num,
	#})
	
		
	## these compilations could translate into direct hashes writen to memory/disk
	## these should basically be able to act like globally (or not) referencable
	## garbage collected variables.
	##   garbage collection would require some way to define when somethign expires
	#def pre(vars) :
		#vars['getlastime'] = sparql.compile_single_number([
			#{
				#n.hash.namespace : n.lastfm,
				#n.hash.key : 'lastfm-lasttime',
				#n.hash.value : None
			#}
		#])
		
		#vars['setlasttime'] = sparql.compile_write([
			#{
				#n.hash.namespace : n.lastfm,
				#n.hash.key : 'lastfm-lasttime',
				#n.hash.value : None,
			#}
		#])
	
	from htmlentitydefs import name2codepoint
	# for some reason, python 2.5.2 doesn't have this one (apostrophe)
	name2codepoint['#39'] = 39
	
	def unescape(s):
			"unescape HTML code refs; c.f. http://wiki.python.org/moin/EscapingHtml"
			return re.sub('&(%s);' % '|'.join(name2codepoint),
								lambda m: unichr(name2codepoint[m.group(1)]), s)

	# WARNING: the output of this transformation does not always result in > 1 
	# set of bindings.  (If the artist is not in lastfm - or if there is no inet?)
	re_lastfm_similar = re.compile('(.*?),(.*?),(.+)')
	def lastfm_similar(vars) :
		import os, urllib, time
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
		n.meta.name : 'last.fm similar artists',
		n.meta.input : """
			artist[music.artist_name] = _artist_name
			artist[lastfm.similar_to] = similar_artist
		""",
		n.meta.output : """
			artist[lastfm.similar_to] = similar_artist
			similar_artist[lastfm.similarity_measure] = _similarity_measure
			similar_artist[lastfm.mbid] = _mbid
			similar_artist[lastfm.artist_name] = _name
		""",
		n.meta.function : lastfm_similar,
		n.meta.scale : 100,
		n.meta.expected_time : 1,
		n.cache.expiration_length : 2678400, # 1 month in seconds
	})
	
	def lastfm_user_recent_tracks(vars) :
		import urllib2, urllib
		import xml.etree.ElementTree
		
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
		#n.meta.name : "last.fm user's recent tracks",
		#n.meta.input : """
			#user[lastfm.user_name] = _user_name
			#user[lastfm.recent_track] = track
			#track[lastfm.album] = album
			#track[lastfm.artist] = artist
		#""",
		#n.meta.output : """
			#artist[lastfm.mbid] = _artist_mbid
			#artist[lastfm.artist_name] = _artist_name
			#track[lastfm.track_name] = _track_name
			#album[lastfm.mbid] = _album_mbid
			#album[lastfm.album_name] = _album_name
			#track[lastfm.date_uts] = _date_uts
		#""",
		#n.meta.function : lastfm_user_recent_tracks,
	#})
	axpress.register_translation({
		n.meta.name : "last.fm user's recent tracks",
		n.meta.input : """
			user[lastfm.user_name] = _user_name
			user[lastfm.recent_track] = track
			track[lastfm.artist] = artist
		""",
		n.meta.output : """
			artist[lastfm.mbid] = _artist_mbid
			artist[lastfm.artist_name] = _artist_name
			track[lastfm.track_name] = _track_name
			track[lastfm.date_uts] = _date_uts
		""",
		n.meta.function : lastfm_user_recent_tracks,
	})
	
	axpress.register_translation({
		n.meta.name : "last.fm shorthand artist name",
		n.meta.input : """
			track[lastfm.artist] = artist
			artist[lastfm.artist_name] = _artist_name
		""",
		n.meta.output : """
			track[lastfm.artist_name] = _artist_name
		""",
	})
	
	axpress.register_translation({
		n.meta.name : "lastfm.artist_name -> music.artist_name",
		n.meta.input : """
			x[lastfm.artist_name] = _name
		""",
		n.meta.output : """
			x[music.artist_name] = _name
		""",
	})
	
	#axpress.register_translation({
		#n.meta.name : "last.fm shorthand artist mbid",
		#n.meta.input : """
			#track[lastfm.artist] = artist
			#artist[lastfm.mbid] = _artist_mbid
		#""",
		#n.meta.output : """
			#track[lastfm.artist_mbid] = _artist_mbid
		#""",
	#})
	
	#axpress.register_translation({
		#n.meta.name : "last.fm shorthand album mbid",
		#n.meta.input : """
			#track[lastfm.album] = album
			#album[lastfm.mbid] = _album_mbid
		#""",
		#n.meta.output : """
			#track[lastfm.album_mbid] = _album_mbid
		#""",
	#})
	
	
	
	
	
	
	"""
	artist[music.artist_name] = artist_name
	artist[lastfm.similar_to] = similar_artist
	similar_artist = #lastfmsimilar
	"""
	# could be compiled to:
	"""
	music.artist_name(artist) :- artist_name
	lastfm.similar_to(artist) :- similar_artist
	python_call(lastfmsimilar, artist_name, similar_artist)
	"""
	# and a query which uses it like this:
	"""
	music.artist_name(artist) = 'Lavender Diamond'
	music.artist(album) = lastfm.similar_to(artist)
	music.playable(album) = True
	"""
	
	def flickr_make_url(photo) :
		# 'http://farm{farm-id}.static.flickr.com/{server-id}/{id}_{secret}.jpg'
		# 'http://farm{farm-id}.static.flickr.com/{server-id}/{id}_{secret}_[mstb].jpg'
		return 'http://farm%s.static.flickr.com/%s/%s_%s_%s.jpg' % \
						(photo.attrib['farm'], photo.attrib['server'], photo.attrib['id'], photo.attrib['secret'], 'b')
	
	def flickr_photos_search(vars) :
		import flickrapi
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
#			'image[flickr.tag] ?= tag', # TODO: ?= means optionally equal to
#			'optional(image[flickr.tag] = tag)',
#			'optional(image[flickr.user_id] = user_id)',
#			...
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
	
	axpress.register_translation({
		n.meta.name : 'string: files matching %pattern%',
		n.meta.input : """
			file[axpress.is] = "files matching %pattern%"
		""",
		n.meta.output : """
			file[glob.glob] = "%pattern%"
		""",
	})
	
	def display_html_filenames(vars) :
		str = "<ul>"
		for filename in vars['filenames'] :
			str += "<li>" + filename
		str += "</ul>"
		return str
	axpress.register_translation({
		n.meta.name : 'filename as html',
		n.meta.input : """
			file[file.filename] = _filename
		""",
		n.meta.output : """
			file[display.html] = _html
		""",
		n.meta.function : display_html_filenames,
	})

	def load_image(vars) :
		from PIL import Image
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
	
	#def load_image2(vars) :
		#from PIL import Image
		#im = Image.open(vars['filename'])
		#im.load() # force the data to be loaded (Image.open is lazy)
		#vars['pil_image'] = im
	#axpress.register_translation({
		#n.meta.name : 'load image2',
		#n.meta.input : """
			#image[file.filename] = _filename
		#""",
		#n.meta.output : """
			#image[pil.image2] = _pil_image
		#""",
		#n.meta.function : load_image2,
	#})
		
	def image_thumbnail(vars) :
		from PIL import Image
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
		from PIL import Image
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
	






	def playlist_enuque(vars):
		pass
	axpress.register_translation({
		n.meta.name : 'playlist enqueue',
		n.meta.input : """
			playlist.enqueue(playlist.playlist, album) = True
			album[music.track] = track
			track[file.url] = url
			track[music.title] = title
			track[music.track_number] = track_number
		""",
		n.meta.output : [
		],
		n.meta.function : playlist_enuque,
		n.meta.side_effect : True,
	})
	
	
	
	
	
	## how to express a SQL query in this language?
	## this is going to require more thinking ...
	## the SQL query schema might be useful here
	## so might some kind of macros ... wow
	#def foo(vars):
		#pass
	#axpress.register_translation({
		#n.meta.name : 'sql_where',
		#n.meta.input : [
			#'sql[sql.connection] = connection',
			#'sql[sql.select] = col_name',
			#'sql[sql.select_from] = table_name',
			#'sql[sql.where] = col_name'
		#],
		#n.meta.output : [
		#],
		#n.meta.function : foo,
	#})
	
	
	
	
	
	"""
	"/home/dwiel/*.jpg[glob.glob] = "/home/dwiel/abc.jpg"
	
	if the input pattern is *anything* (var or literal) then the above is actually
	a query to finish out that list of globs.  Is that what we want?
	
	what if _ only matches a variable or missing value
	
	then the above just makes a statement, its not a query
	
	but then you also sometime want a literal or a variable, anything will do
		as in a uri/object name you don't care about
	
	types of variables:
		literal or variable  name   =>  var.name
		only a literal       _name  =>  lit_var.name   (this just means bound - could be a bnode)
		only a variable      ?name  =>  meta_var.name
	
	will we inevitably find more types of variables we want?
		maybe only accepts a literal of type string
		could be done with:
	
	isupper(var) = bool =>
	isupper(var) = bool
	def foo(vars) :
		if vars['var'].isupper() :
			vars['bool'] = True
		else :
			vars['bool'] = False
	
	
	how else could this kind of matching be done?
	
	The 'type' information could also be infered from the function and the variables it uses.
	That might be [impossibly] hard to detect...
	
	The 'type' information could also just be another meta data line:
		n.meta.input_variable_type : {
			'filename' : 'variable',
			'pattern' : 'literal'
		},
		n.meta.output_variable_type : {
			'filename' : 'literal',
			'pattern' : 'literal'
		},
	
	for now, the prefix on the variable name makes sense.  It would be easy to add
	a meta-data like above to the translation syntax
	"""
	
	
	def glob_glob(vars):
		import glob
		#vars['out_filename'] = glob.glob(vars['pattern'])
		ret = [{'out_filename' : filename} for filename in glob.glob(vars['pattern'])]
		#print(vars['pattern'],ret)
		return ret
	axpress.register_translation({
		n.meta.name : 'glob glob',
		n.meta.input : """
			glob[glob.glob] = _pattern
		""",
		n.meta.output : """
			glob[file.filename] = _out_filename
		""",
		n.meta.function : glob_glob,
	})
	
	# TODO: allow define uriX == uriY or in this case glob.glob == file.pattern
	axpress.register_translation({
		n.meta.name : 'file pattern (glob)',
		n.meta.input : """
			glob[file.pattern] = _pattern
		""",
		n.meta.output : """
			glob[file.filename] = _out_filename
		""",
		n.meta.function : glob_glob,
	})
	
	def glob_glob(vars):
		import glob
		vars['out_filename'] = glob.glob(vars['pattern'])
	axpress.register_translation({
		n.meta.name : 'glob glob',
		n.meta.input : """
			glob.glob(_pattern) = foo[file.filename]
		""",
		n.meta.output : """
			foo[file.filename] = _out_filename
		""",
		n.meta.function : glob_glob,
	})



	def download_tmp_file(vars):
		#TODO don't depend on wget ...
		vars['filename'] = 'axpress.tmp%s' % str(random.random()).replace('.','')
		os.system('wget %s -O %s' % (vars['url'], vars['filename']))
	axpress.register_translation({
		n.meta.name : 'download_tmp_file',
		n.meta.input : """
			file[file.url] = _url
		""",
		n.meta.output : """
			file[file.filename] = _filename
		""",
		n.meta.function : download_tmp_file,
	})
	

	#def filename_to_url(vars):
		#vars['url'] = vars['filename'].replace('/home/dwiel', '/home')
	#axpress.register_translation({
		#n.meta.name : 'filename to url',
		#n.meta.input : """
			#file[file.filename] = _filename
		#""",
		#n.meta.output : """
			#file[file.url] = _url
		#""",
		#n.meta.function : filename_to_url,
	#})


	def html_img(vars):
		web_filename = vars['filename'].replace('/home/dwiel', '/home')
		
		#if 'width' in vars :
			#width = 'width="%s" ' % vars['width']
		#else :
			#width = ''
		
		#if 'height' in vars :
			#height = 'height="%s" ' % vars['height']
		#else :
			#height = ''
		
		#vars['html'] = '<img src="%s" %s%s/>' % (web_filename, width, height)
		
		vars['html'] = '<img src="%s" width="%s" height="%s"/>' % (web_filename, vars['width'], vars['height'])
	axpress.register_translation({
		n.meta.name : 'html img link',
		n.meta.input : """
			image[file.filename] = _filename
			image[html.width] = _width
			image[html.height] = _height
		""",
		n.meta.output : """
			image[html.html] = _html
		""",
		n.meta.function : html_img,
	})

	## this is starting to get silly.  I vote for a python/js code block in MultilineParser
	#def div(vars):
		#pass
	#axpress.register_translation({
		#n.meta.name : 'div',
		#n.meta.input : """
			#div[html.background_color] = _color
			#object[html.html] = _object_html
			#div[html.contains] = object
		#""",
		#n.meta.output : """
			#div[html.html] _div_html
		#""",
		#n.meta.function : foo,
	#})



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
	
	
	
	# used for testing a translation which returns no bindings
	def no_bindings(vars):
		return []
	axpress.register_translation({
		n.meta.name : 'no bindings',
		n.meta.input : """
			foo[test.no_bindings_input] = _input
		""",
		n.meta.output : """
			foo[test.no_bindings_output] = _output
		""",
		n.meta.function : no_bindings,
	})
	
	
	
	
	# http://lethain.com/entry/2008/jul/11/search-recipes-for-yahoo-s-boss-in-python/
	# yahoo search bindings
	def yahoo_search(vars):
		from yos.boss import ysearch
		from yos.yql import db
		data = ysearch.search(vars['query'],count=10)
		table = db.create(data=data)
		return table.rows

	axpress.register_translation({
		n.meta.name : '',
		n.meta.input : """
			search[yahoo.query] = _query
		""",
		n.meta.output : """
			search[yahoo.dispurl] = _dispurl
			search[yahoo.title] = _title
			search[yahoo.url] = _url
			search[yahoo.abstract] = _abstract
			search[yahoo.clickurl] = _clickurl
			search[yahoo.date] = _date
			search[yahoo.size] = _size
		""",
		n.meta.function : yahoo_search,
	})
	
	def red(vars) :
		vars['c'] = "FF0000"
	axpress.register_translation({
		n.meta.name : 'is red',
		n.meta.input : """
			color[axpress.is] = "red"
		""",
		n.meta.output : """
			color[html.color] = _c
		""",
		n.meta.function : red,
	})
	
	"""
	sum of %number% and %number%
	fn : number + number
	
	x[axpress.is] = "sum of %number% and %number%"
	=>
	x[axpress.is] = _sum
	
	x[
	
	# there is how the strings percolate down through the translations
	# and
	# there is how the string is input from the user
	"""
	
	def green(vars) :
		vars['c'] = "00FF00"
	axpress.register_translation({
		n.meta.name : 'is green',
		n.meta.input : """
			color[axpress.is] = "green"
		""",
		n.meta.output : """
			color[html.color] = _c
		""",
		n.meta.function : green,
	})
	
	def invert_color(vars) :
		vars['rout'] = 255 - vars['rin']
		vars['gout'] = 255 - vars['gin']
		vars['bout'] = 255 - vars['bin']
	axpress.register_translation({
		n.meta.name : 'invert',
		n.meta.input : """
			color[html.color_red]   = _rin
			color[html.color_green] = _gin
			color[html.color_blue]  = _bin
			color[color.invert] = inverted_color
		""",
		n.meta.output : """
			inverted_color[html.color_red]   = _rout
			inverted_color[html.color_green] = _gout
			inverted_color[html.color_blue]  = _bout
		""",
		n.meta.function : invert_color,
	})
	
	def html_color_rgb(vars) :
		# hex to rgb
		vars['red']  = int(vars['c'][0:2], 16)
		vars['green'] = int(vars['c'][2:4], 16)
		vars['blue'] = int(vars['c'][4:6], 16)
	axpress.register_translation({
		n.meta.name : 'html color to rgb',
		n.meta.input : """
			color[html.color] = _c
		""",
		n.meta.output : """
			color[html.color_red] = _red
			color[html.color_green] = _green
			color[html.color_blue] = _blue
		""",
		n.meta.function : html_color_rgb,
		n.meta.inverse_function : 'html rgb to color',
	})
	
	def html_rgb_color(vars) :
		# rgb_to_hex
		vars['c'] = "%0.2X%0.2X%0.2X" % (
			vars['red'], vars['green'], vars['blue']
		)
	axpress.register_translation({
		n.meta.name : 'html rgb to color',
		n.meta.input : """
			color[html.color_red] = _red
			color[html.color_green] = _green
			color[html.color_blue] = _blue
		""",
		n.meta.output : """
			color[html.color] = _c
		""",
		n.meta.function : html_rgb_color,
		n.meta.inverse_function : 'html color to rgb',
	})
	
	axpress.register_translation({
		n.meta.name : 'is inverse of color',
		n.meta.input : """
			icolor[axpress.is] = "inverse of %color%"
		""",
		n.meta.output : """
			color[html.color] = _c
			color[color.invert] = icolor
			icolor[html.color] = _ic
		""",
		n.meta.function : red,
	})

	#axpress.register_translation({
		#n.meta.name : '',
		#n.meta.input : """
			
		#""",
		#n.meta.output : """
		#""",
	#})
	
	#axpress.register_translation({
		#n.meta.name : '',
		#n.meta.input : """
			## short hand
			#author[axpress.is] = "author of %book%"
			## long hand
			#author[axpress.is] = "author of %s"
			#author[axpress.arg0] = book
			## both require some kind of regexp ... the regexp will need to be testable
			## through both the compiler and evaluator
			#book[freebase.mid] = _mid
			#book[freebase.type] = '/book/written_work'
		#""",
		#n.meta.output : """
			#book[freebase./book/written_work/author] = author
		#""",
	#})
	
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
			artist[freebase.type] = '/music/musical_group'
		""",
	})
	
	def lookup_albums_by_musician(vars) :
		import freebase
		result = freebase.mqlread({
			"mid" : vars['mid'],
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
			artist[freebase.mid] = _mid
			artist[freebase.type] = '/music/musical_group'
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
		import freebase
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
		#import freebase
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
		import freebase
		result = freebase.mqlread({
			"mid" : vars['mid'],
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
			person[freebase.mid] = _mid
			person[freebase.type] = '/people/person'
		""",
		n.meta.output : """
			person[freebase./people/person/place_of_birth] = birthplace
			birthplace[freebase.mid] = _mid
			birthplace[freebase.name] = _name
		""",
		n.meta.function : lookup_birthplace,
	})
	
	
	axpress.register_translation({
		n.meta.name : 's current weather',
		n.meta.input : """
			weather[axpress.is] = "current weather in %location_s%"
		""",
		n.meta.output : """
			location[axpress.is] = "%location_s%"
			location[freebase.type] = '/location/location'
			location[wunderground.weather] = weather
		""",
	})
	
	def lookup_current_weather(vars) :
		# TODO
	axpress.register_translation({
		n.meta.name : 'lookup current weather',
		n.meta.input : """
			location[wunderground.weather] = weather
			location[freebase.type] = '/location/location'
			location[freebase./location/location/geolocation] = geo
			geo[freebase./location/geocode/latitude] = _lat
			geo[freebase./location/geocode/longitude] = _lon
		""",
		n.meta.output : """
			weather[wunderground.current_temperature] = _current_temperature
		""",
		n.meta.function = lookup_current_weather,
	})
	
	# TODO: /location/location -> geo lat/lon
	
	def freebase_search(vars) :
		import json
		import urllib2, urllib
		
		ret = urllib2.urlopen("https://www.googleapis.com/freebase/v1/search", urllib.urlencode({
			'query' : vars['title'],
			'type' : vars['type'],
			'html_escape' : 'false',
			'html_encode' : 'false',
			'limit' : 1})).read()
		print ret
		ret = json.loads(ret)
		
		if ret['status'] != '200 OK' :
			raise Exception("freebase didn't work ...")
		result = ret['result'][0]
		if result['score'] > 30 :
			vars['mid'] = result['mid']
		
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
	
	axpress.register_translation({
		n.meta.name : '',
		n.meta.input : """
			date_of_first_publication[axpress.is] = "first published %book_str%"
			book[freebase.mid] = _mid
			book[freebase.type] = '/book/written_work'
		""",
		n.meta.output : """
			book[axpress.is] = "%book_str"
			book[freebase./book/written_work/date_of_first_publication] = date_of_first_publication
			# this next line might be implied by a more general rule (see following)
			date_of_first_publication[freebase.type] = freebase.type/datetime
		""",
	})
	
	# this translation shows only that properties of type freebase./book/wri...
	# must have values which have the freebase.type freebase.type/datetime
	# this kind of rule should be automatically generated/translated from the 
	# freebase database of properties soon, perhpas using axpress
	axpress.register_translation({
		n.meta.name : '',
		n.meta.input : """
			book[freebase./book/written_work/date_of_first_publication] = date_of_first_publication
		""",
		n.meta.output : """
			date_of_first_publication[freebase.type] = freebase.type/datetime
			# and maybe even something like :
			date_of_first_publication[axpress.constraint] = axpress.unique
		""",
	})
	
	#axpress.register_translation({
		#n.meta.name : '',
		#n.meta.input : """
		#""",
		#n.meta.output : """
		#""",
	#})
	
	#axpress.register_translation({
		#n.meta.name : 'sql test',
		#n.meta.input : """
			#query[sql.host] = _host
			#query[sql.database] = _database
			#query[sql.table] = _table
			#query[sql.
		#""",
		#n.meta.output : """
		#""",
		#n.meta.function : foo,
	#})

	#def foo(vars):
		#pass
	#axpress.register_translation({
		#n.meta.name : '',
		#n.meta.input : """
		#""",
		#n.meta.output : """
		#""",
		#n.meta.function : foo,
	#})

	axpress.register_translation({
		n.meta.name : 'test',
		n.meta.input : """
			x[test.p][test.p] = y
		""",
		n.meta.output : """
			x[test.q][test.q] = y
			x[test.q][test.r] = 10000
		""",
		# note that y isn't a constant var ... right now it is because y in the 
		# input will likely be bound to a different variable than y in the output,
		# so it isn't constant.  The value is constant, 
	})

	axpress.register_translation({
		n.meta.name : 'test2',
		n.meta.input : """
			x[test.p] = y
		""",
		n.meta.output : """
			x[test.q] = y
			x[test.r] = z
		""",
		# note that y isn't a constant var ... right now it is because y in the 
		# input will likely be bound to a different variable than y in the output,
		# so it isn't constant.  The value is constant,
		# 2011-10-27: it is constant now ...
	})

"""

x[foo.foo][foo.foo] = 1
x[foo.bar][foo.bar] = _one

new_final_bindings [
  [
    [ n.var.image, n.file.filename, '/home/dwiel/AMOSvid/1065/20080821_083129.jpg', ],
    [ n.var.bnode1, n.call.arg1, n.var.image, ],
    [ n.var.bnode1, n.call.arg2, 4, ],
    [ n.var.bnode1, n.call.arg3, 4, ],
    [ n.var.bnode1, n.image.thumbnail, n.var.thumb, ],
    [ n.var.image, n.pil.image, <PIL.JpegImagePlugin.JpegImageFile instance at 0x837d8cc>, ],
    [ n.var.thumb, n.pil.image, <PIL.JpegImagePlugin.JpegImageFile instance at 0x837d8cc>, ],
  ],
]

applying image thumbnail
binding {
  n.var._ : n.var.thumb,
  n.var.bnode1 : n.var.bnode1,
  n.var.image : <PIL.JpegImagePlugin.JpegImageFile instance at 0x837d8cc>,
  n.var.thumb : n.var.thumb,
  n.var.x : 4,
  n.var.y : 4,
}





"""
