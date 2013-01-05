import unittest

from SimpleSPARQL.StringMatch import match

class StringMatchTestCase(unittest.TestCase):
  def test1(self):
    ret = match("%x%o%y%", "dogod")
    #print ret
    assert ret == [
      {'x' : 'd', 'y' : 'god'},
      {'x' : 'dog', 'y' : 'd'},
    ]
  
  def test2(self):
    assert match("%a%XY%b%YZ%c%", "abcXYdefXYghYZijYZkl") == [
      {'a' : 'abc', 'b' : 'defXYgh', 'c' : 'ijYZkl'},
      {'a' : 'abc', 'b' : 'defXYghYZij', 'c' : 'kl'},
      {'a' : 'abcXYdef', 'b' : 'gh', 'c' : 'ijYZkl'},
      {'a' : 'abcXYdef', 'b' : 'ghYZij', 'c' : 'kl'},
    ]

  def test3(self):
    ret = match("%a%XY%b%YZ%c%", "XYdefXYghYZijYZkl")
    #print 'ret', json.dumps(ret, indent=4)
    assert ret == [
      {'a' : 'XYdef', 'b' : 'gh', 'c' : 'ijYZkl'},
      {'a' : 'XYdef', 'b' : 'ghYZij', 'c' : 'kl'},
    ]
  
  def test4(self):
    assert match("%a%%b%", "abc") == [
      {'a' : 'a', 'b' : 'bc'},
      {'a' : 'ab', 'b' : 'c'},
    ]
    #assert match('abc', 'abc') == []
    #assert match('abcdef', 'abc') == False
    #assert match("%x%o%y%", "digid") == False
    #assert match('%x%', 'abc') == [{'x' : 'abc'}]

  def test5(self):
    # the constant part of a pattern can be arbitrary regexp:
    assert match("%time_s% (on |in |)%date_s%", "5 on friday") == [
      {'time_s' : '5', 'date_s' : 'friday'},
    ]
    assert match("%time_s% (on |in |)%date_s%", "5 friday") == [
      {'time_s' : '5', 'date_s' : 'friday'},
    ]

  def test6(self):
    ret = match("x %a%", "x y z")
    #print ret
    assert ret == [
      {'a' : 'y z'},
    ]

  def test7(self):
    assert match("x %a% %b%", "x y z w") == [
      {'a' : 'y', 'b' : 'z w'},
      {'a' : 'y z', 'b' : 'w'},
    ]

  def test8(self):
    assert match("remind me to %msg% %dt%", "remind me to go to keleinforfers tomorrow at 5 pm") == [
      {'msg': 'go', 'dt': 'to keleinforfers tomorrow at 5 pm'},
      {'msg': 'go to', 'dt': 'keleinforfers tomorrow at 5 pm'},
      {'msg': 'go to keleinforfers', 'dt': 'tomorrow at 5 pm'},
      {'msg': 'go to keleinforfers tomorrow', 'dt': 'at 5 pm'},
      {'msg': 'go to keleinforfers tomorrow at', 'dt': '5 pm'},
      {'msg': 'go to keleinforfers tomorrow at 5', 'dt': 'pm'}
    ]
    
    ret = match("remind me to %msg% (at |)%dt%", "remind me to go to keleinforfers tomorrow at 5 pm")
    #print 'ret', json.dumps(ret, indent=4)
    assert ret == [
      {'msg': 'go', 'dt': 'to keleinforfers tomorrow at 5 pm'},
      {'msg': 'go to', 'dt': 'keleinforfers tomorrow at 5 pm'},
      {'msg': 'go to keleinforfers', 'dt': 'tomorrow at 5 pm'},
      {'msg': 'go to keleinforfers tomorrow', 'dt': '5 pm'},
      {'msg': 'go to keleinforfers tomorrow at 5', 'dt': 'pm'}
    ]

  def test9(self):
    ret = match('xyz %x%', 'abcdefg')
    assert ret == False
  
  def test10(self):
    ret = match(u'%x% %y%', u'a b')
    assert type(ret[0]['x']) == unicode
    assert type(ret[0].keys()[0]) == unicode
    assert ret == [{'x' : 'a', 'y' : 'b'}]
  
  def test11(self):
    assert match("%dow%", "3") == [{'dow' : '3'}]
  
  def test12(self):
    assert match('%i%(|x)','today at 3') == [
      {'i' : 'today at 3'},
    ]
    assert match('%i%(|x)','today at x') == [
      {'i' : 'today at '},
      {'i' : 'today at x'},
    ]
    assert match('%i%(3|x)','today at 3') == [
      {'i' : 'today at '}
    ]

  def test13(self):
    assert match("%x%-%y%", "1-3") == [{'x' : '1', 'y' : '3'}]

  def test14(self):
    ret = match("%x%-%y%%z%", "1-345")
    #print 'ret', ret
    assert ret == [
      {'x' : '1', 'y' : '3', 'z' : '45'},
      {'x' : '1', 'y' : '34', 'z' : '5'},
    ]

if __name__ == "__main__" :
    unittest.main()
