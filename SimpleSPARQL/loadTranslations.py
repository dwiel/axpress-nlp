
def loadTranslations(axpress, n = None) :
  import glob
  import os
  import imp
  import md5

  # only allow loading
  if axpress.__dict__.get('loaded_translations') :
    return
  else :
    axpress.loaded_translations = True
  
  if not n :
    n = axpress.n

  n.bind('a', '<http://dwiel.net/axpress/0.1/>')
  n.bind('axpress', '<http://dwiel.net/axpress/0.1/>')
  n.bind('rdfs', '<http://www.w3.org/2000/01/rdf-schema#>')
  n.bind('type', '<http://dwiel.net/express/type/0.1/>')
  n.bind('speech', '<http://dwiel.net/axpress/speech/0.1/>')

  axpress.modules = []
  for name in glob.glob('/home/dwiel/src/axpress-nlp/translations/*.py') :
    if os.path.isdir(name) :
      pass
    else :
      module_name = os.path.basename(name[:-3])

      f = open(name, 'rb')
      m = imp.load_source(md5.new(name).hexdigest(), name, f)
      
      axpress.modules.append(m)

      try :
        loadTranslations = m.loadTranslations
      except AttributeError, e:
        continue
      
      loadTranslations(axpress)

  axpress.compiler.compile_translations()
