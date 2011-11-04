
def loadTranslations(axpress, n) :
  import glob
  import os
  import imp
  import md5

  for name in glob.glob('/home/dwiel/axpress/translations/*.py') :
    if os.path.isdir(name) :
      pass
    else :
      module_name = os.path.basename(name[:-3])
      #if module_name in ['__init__', 'translation'] :
        #continue
      
      print "loading (%s)" % module_name

      f = open(name, 'rb')
      m = imp.load_source(md5.new(name).hexdigest(), name, f)

      m.loadTranslations(axpress, n)

