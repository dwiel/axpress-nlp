
def loadTranslations(axpress, n) :
  import glob
  import os
  import imp
  import md5

  n.bind('a', '<http://dwiel.net/axpress/0.1/>')
  n.bind('axpress', '<http://dwiel.net/axpress/0.1/>')
  n.bind('rdfs', '<http://www.w3.org/2000/01/rdf-schema#>')
  n.bind('type', '<http://dwiel.net/express/type/0.1/>')

  for name in glob.glob('/home/dwiel/axpress/translations/*.py') :
    if os.path.isdir(name) :
      pass
    else :
      module_name = os.path.basename(name[:-3])

      f = open(name, 'rb')
      m = imp.load_source(md5.new(name).hexdigest(), name, f)

      m.loadTranslations(axpress, n)

  axpress.compiler.compile_translations()
