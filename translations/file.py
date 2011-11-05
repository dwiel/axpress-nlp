import glob

def loadTranslations(axpress, n) :
  n.bind('glob', '<http://dwiel.net/express/python/glob/0.1/>')

  axpress.register_translation({
    n.meta.name : 'string: files matching %pattern%',
    n.meta.input : """
      file[axpress.is] = "files matching %pattern%"
    """,
    n.meta.output : """
      file[glob.glob] = "%pattern%"
    """,
  })
  
  def glob_glob(vars):
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

