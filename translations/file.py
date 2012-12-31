import glob

def loadTranslations(axpress) :
  axpress.n.bind('glob', '<http://dwiel.net/express/python/glob/0.1/>')

  axpress.register_translation({
    'name' : 'string: files matching %pattern%',
    'input' : """
      file[axpress.is] = "files matching %pattern%"
    """,
    'output' : """
      file[glob.glob] = "%pattern%"
    """,
  })
  
  def glob_glob(vars):
    #vars['out_filename'] = glob.glob(vars['pattern'])
    ret = [{'out_filename' : filename} for filename in glob.glob(vars['pattern'])]
    #print(vars['pattern'],ret)
    return ret
  axpress.register_translation({
    'name' : 'glob glob',
    'input' : """
      glob[glob.glob] = _pattern
    """,
    'output' : """
      glob[file.filename] = _out_filename
    """,
    'function' : glob_glob,
  })
  
  # TODO: allow define uriX == uriY or in this case glob.glob == file.pattern
  axpress.register_translation({
    'name' : 'file pattern (glob)',
    'input' : """
      glob[file.pattern] = _pattern
    """,
    'output' : """
      glob[file.filename] = _out_filename
    """,
    'function' : glob_glob,
  })
  
  # I don't think this is any different than the other glob glob
  #def glob_glob(vars):
    #vars['out_filename'] = glob.glob(vars['pattern'])
  #axpress.register_translation({
    #'name' : 'glob glob',
    #'input' : """
      #glob.glob(_pattern) = foo[file.filename]
    #""",
    #'output' : """
      #foo[file.filename] = _out_filename
    #""",
    #'function' : glob_glob,
  #})
  
  def download_tmp_file(vars):
    # TODO don't depend on wget ...
    import random
    import os
    
    vars['filename'] = 'axpress.tmp%s' % str(random.random()).replace('.','')
    os.system('wget %s -O %s' % (vars['url'], vars['filename']))
  axpress.register_translation({
    'name' : 'download_tmp_file',
    'input' : """
      file[file.url] = _url
    """,
    'output' : """
      file[file.filename] = _filename
    """,
    'function' : download_tmp_file,
  })
  
  def file_to_lines(vars):
    # NOTE: using a set out here instead of a list since axpress will currently
    # interpret a list value as a set of possibile values rather than a python
    # list object
    try :
      f = open(vars['filename'], 'r')
      vars['lines'] = set(line.strip() for line in f.read().split('\n') if line.strip())
      f.close()
    except IOError :
      vars['lines'] = set()
  axpress.register_translation({
    'name' : 'file as set of lines',
    'input' : """
      file[file.filename] = _filename
    """,
    'output' : """
      file[file.lines] = _lines
    """,
    'function' : file_to_lines,
  })

  #def filename_to_url(vars):
    #vars['url'] = vars['filename'].replace('/home/dwiel', '/home')
  #axpress.register_translation({
    #'name' : 'filename to url',
    #'input' : """
      #file[file.filename] = _filename
    #""",
    #'output' : """
      #file[file.url] = _url
    #""",
    #'function' : filename_to_url,
  #})

