import hashlib
import traceback

class Triple(list) :
  def __init__(self, l, optional = False) :
    super(Triple, self).__init__(l)
    self.optional = optional
    
    m = hashlib.md5()
    map(m.update, map(str, l))
    self.hash = m.digest()
  
  def __setitem__(self, i, v) :
    super(Triple, self).__setitem__(i, v)
    
    m = hashlib.md5()
    map(m.update, map(str, self))
    self.hash = m.digest()

