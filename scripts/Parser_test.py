#!/usr/bin/env python
# -*- coding: utf-8 -*-
import unittest

from SimpleSPARQL import *

n = globalNamespaces()
n.bind('',        '<http://dwiel.net/express//0.1/>')
n.bind('axpress', '<http://dwiel.net/axpress/0.1/>')
n.bind('string',  '<http://dwiel.net/express/string/0.1/>')
n.bind('math',    '<http://dwiel.net/express/math/0.1/>')
n.bind('file',    '<http://dwiel.net/express/file/0.1/>')
n.bind('glob',    '<http://dwiel.net/express/glob/0.1/>')
n.bind('color',   '<http://dwiel.net/express/color/0.1/>')
n.bind('sparql',  '<http://dwiel.net/express/sparql/0.1/>')
n.bind('image',   '<http://dwiel.net/express/image/0.1/>')
n.bind('pil',     '<http://dwiel.net/express/python/pil/0.1/>')
n.bind('glob',    '<http://dwiel.net/express/python/glob/0.1/>')
n.bind('call',    '<http://dwiel.net/express/call/0.1/>')
n.bind('test',    '<http://dwiel.net/express/test/0.1/>')
n.bind('flickr',  '<http://dwiel.net/express/flickr/0.1/>')
n.bind('dt',      '<http://dwiel.net/axpress/datetime/0.1/>')

class PassCompleteReadsTestCase(unittest.TestCase):
  def setUp(self):
    self.parser = Parser(n)
  
  def test1(self):
    assert self.parser.parse_expression("image[flickr.tag] = 'sunset'") == [[Var.image, n.flickr.tag, 'sunset']]
  
  def test1b(self):
    assert self.parser.parse_expression("image[flickr.tag] = 'sunset' | 'sunrise'") == [[Var.image, n.flickr.tag, ['sunset', 'sunrise']]]
  
  def test2(self):
    assert self.parser.parse_expression("image[flickr:tag] = 1.5") == [[Var.image, n.flickr.tag, 1.5]]
  
  def test3(self):
    assert self.parser.parse_expression("image[flickr:tag] = 4 * 9") == [[Var.image, n.flickr.tag, 4 * 9]]

  def test4(self):
    assert self.parser.parse_expression("image[flickr.tag] = tag") == [[Var.image, n.flickr.tag, Var.tag]]
  
  def test5(self):
    assert self.parser.parse_expression("tag = image[flickr.tag]") == [[Var.image, n.flickr.tag, Var.tag]]
  
  def test6(self):
    assert self.parser.parse_expression("image1[flickr.tag] = image2[flickr.tag]") == [
      [Var.image1, n.flickr.tag, Var.bnode1],
      [Var.image2, n.flickr.tag, Var.bnode1],
    ]
  
  def test7(self):
    assert self.parser.parse_expression("tag = image[flickr.tag][string.upper]") == [
      [Var.image, n.flickr.tag, Var.bnode1],
      [Var.bnode1, n.string['upper'], Var.tag],
    ]
  
  def test8(self):
    assert self.parser.parse_expression("""
      color.distance{
        color.rgb : 1,
        color.rgb : 2,
      } = distance""") == [
      [Var.bnode1, n.color.rgb, 1],
      [Var.bnode1, n.color.rgb, 2],
      [Var.bnode1, n.color.distance, Var.distance],
    ]
  
  """
  location[axpress.is] = "%location_s%"
  location[freebase.type] = '/location/location'
  location[wunderground.weather] = weather
    =>
  location{
    freebase.type = '/location/location'
    wunderground.weather = weather
  }
  
  location[axpress.is] = "%location_s%"
  location[freebase.type] = '/location/location'
  location[wunderground.weather] = weather
  weather[wunderground.dew_point] = dew_point
    =>
  location{
    freebase.type = '/location/location'
    wunderground.weather = weather{
      wunderground.dew_point = dew_point
    }
  }
  
  This kind of change, is less typing, but is that the highest priority right now?
  it might be high since the goal is to get people to write apps ...
  
  location[wunderground.weather] = weather
  location[freebase.type] = '/location/location'
  location[freebase./location/location/geolocation] = geo
  geo[freebase./location/geocode/latitude] = _lat
  geo[freebase./location/geocode/longitude] = _lon
    =>
  location{
    wunderground.weather = weather
    freebase.type = '/location/location'
    freebase./location/location/geolocation = geo{
      freebase./location/geocode/latitude = _lat
      freebase./location/geocode/longitude = _lon
    }
  }
  
  there might be more savings in helping create sets of translations ...
  there is a bunch of redundancy mapping the various types ...
  I guess this is because of all of the duck typing ... must type out the 
  lat/lon uris in order to get access to those values, where as if there were
  more explicit types, then there might be shorthand for these ... freebase is
  especially bad at this, thought it will hopefully, mostly be automatically
  generated.  Interfacing with it though ... autocomplete could help
  """
  
  def test9(self):
    assert self.parser.parse_expression("""
      math.sum(1, 2) = sum""") == [
      [n.math.sum, 1, 2, Var.sum],
    ]
  
  def test9_1(self):
    assert self.parser.parse_expression("""
      sum = math.sum(1, 2)""") == [
      [n.math.sum, 1, 2, Var.sum],
    ]
  
  #def test10(self):
    #assert self.parser.parse_expression("""
      #color.distance{
        #color.rgb : something[color],
        #color.rgb : 2,
      #} = distance""") == [
      #[Var.something, Var.color, Var.bnode2],
      #[Var.bnode1, n.color.rgb, Var.bnode2],
      #[Var.bnode1, n.color.rgb, 2],
      #[Var.bnode1, n.color.distance, Var.distance],
    #]
  
  def test11(self):
    assert self.parser.parse_expression("image[flickr.tag] = x") == [[Var.image, n.flickr.tag, Var.x]]

  def test12(self):
    assert self.parser.parse_expression("image[flickr:tag] = True") == [[Var.image, n.flickr.tag, True]]
  
  def test13(self):
    assert self.parser.parse_expression("image[flickr.tag] = image_tag") == [[Var.image, n.flickr.tag, Var.image_tag]]
    
  def test14(self):
    assert self.parser.parse_expression('image[file.filename] = "/home/dwiel/AMOSvid/1065/20080821_083129.jpg"') == [
      [Var.image, n.file.filename, "/home/dwiel/AMOSvid/1065/20080821_083129.jpg"]
    ]
    
  def test15(self):
    assert self.parser.parse_expression('image[file.filename] = "home/dwiel/AMOSvid/1065/*.jpg"[glob.glob]') == [
      [Var.image, n.file.filename, Var.bnode1],
      ["home/dwiel/AMOSvid/1065/*.jpg", n.glob.glob, Var.bnode1],
    ]
  
  def test16(self):
    assert self.parser.parse_expression('_pattern[glob.glob] = ?filename') == [
      [LitVar.pattern, n.glob.glob, MetaVar.filename],
    ]
  
  def test17(self):
    query = """uri[test.result] = '<script type="text/javascript" src="external.js"></script>'"""
    assert self.parser.parse_query(query) == [
      [ Var.uri, n.test.result, '<script type="text/javascript" src="external.js"></script>', ],
    ]
    
  def test18(self):
    query = """test.func("xyz()", 'abc = 123') = "what's um, the deal?" """
    #assert self.parser.parse_query(query) == [
      #[ Var.bnode1, n.call.arg1, 'xyz()', ],
      #[ Var.bnode1, n.call.arg2, 'abc = 123', ],
      #[ Var.bnode1, n.test.func, "what's um, the deal?", ],
    #]
    assert self.parser.parse_query(query) == [
      [ n.test.func, 'xyz()', 'abc = 123', "what's um, the deal?", ],
    ]
  
  def test19(self):
    query = """test.func('''xyz() + 'what?' and "what?" ''', 'abc = 123') = "what's um, the deal?" """
    #assert self.parser.parse_query(query) == [
      #[ Var.bnode1, n.call.arg1, 'xyz() + \'what?\' and "what?" ', ],
      #[ Var.bnode1, n.call.arg2, 'abc = 123', ],
      #[ Var.bnode1, n.test.func, "what's um, the deal?", ],
    #]
    assert self.parser.parse_query(query) == [
      [ n.test.func, 'xyz() + \'what?\' and "what?" ', 'abc = 123', "what's um, the deal?", ],
    ]
  
  def test_parseQuery1(self):
    query = [
      'uri[test.sum] = sum',
    ]
    assert self.parser.parse_query(query) == [
      [Var.uri, n.test.sum, Var.sum],
    ]
  
  def test_parseQuery2(self):
    query = [
      'uri[test.sum] = sum',
      'uri[test.x] = uri2[test.x]',
      [Var.uri, n.test.x, 1],
    ]
    assert self.parser.parse_query(query) == [
      [Var.uri, n.test.sum, Var.sum],
      [Var.uri, n.test.x, Var.bnode1],
      [Var.uri2, n.test.x, Var.bnode1],
      [Var.uri, n.test.x, 1],
    ]
  
  def test_parseQuery3(self):
    query = [
      'image[file.filename] = "/home/dwiel/pictures/stitt blanket/*.jpg"[glob.glob]',
      'thumb = image.thumbnail(image, 4, 4, image.antialias)',
      'thumb_image = thumb[pil.image]',
    ]
    ret = self.parser.parse_query(query)
    #assert ret == [
      #[ Var.image, n.file.filename, Var.bnode1, ],
      #[ '/home/dwiel/pictures/stitt blanket/*.jpg', n.glob.glob, Var.bnode1, ],
      #[ Var.bnode2, n.call.arg1, Var.image, ],
      #[ Var.bnode2, n.call.arg2, 4, ],
      #[ Var.bnode2, n.call.arg3, 4, ],
      #[ Var.bnode2, n.call.arg4, n.image.antialias, ],
      #[ Var.bnode2, n.image.thumbnail, Var.thumb, ],
      #[ Var.thumb, n.pil.image, Var.thumb_image, ],
    #]
    assert ret == [
      [ Var.image, n.file.filename, Var.bnode1, ],
      [ '/home/dwiel/pictures/stitt blanket/*.jpg', n.glob.glob, Var.bnode1, ],
      [ n.image.thumbnail, Var.image, 4, 4, n.image.antialias, Var.thumb, ],
      [ Var.thumb, n.pil.image, Var.thumb_image, ],
    ]
  
  def test_parseQuery4(self):
    query = """
      uri[test.sum] = sum
      uri[test.x] = uri2[test.x]
      uri[test.x] = 1
    """
    #p('self.parser.parse_query(query)', self.parser.parse_query(query))
    assert self.parser.parse_query(query) == [
      [Var.uri, n.test.sum, Var.sum],
      [Var.uri, n.test.x, Var.bnode1],
      [Var.uri2, n.test.x, Var.bnode1],
      [Var.uri, n.test.x, 1],
    ]
  
  def test_parseKeyword(self):
    query = """
      c[file.count] = _count
    """
    assert self.parser.parse_query(query) == [
      [Var.c, n.file['count'], LitVar.count],
    ]
  
  def test_parseBrokenQuery(self):
    query = """
      note[e.tag] _tag
    """
    try :
      p('parsed',self.parser.parse_query(query))
    except TypeError :
      assert True
  
  def test_emptyNamespace(self):
    query = """
      note[:tag] = _tag
    """
    
    assert self.parser.parse_query(query) == [
      [Var.note, n['']['tag'], LitVar.tag],
    ]
  
  def test_emptyNamespace2(self):
    query = """
      note[.tag] = _tag
    """
    
    assert self.parser.parse_query(query) == [
      [Var.note, n['']['tag'], LitVar.tag],
    ]
  
  def test_URIwithSlashes(self):
    query = """
      x[test./type/type] = test.property
    """
    assert self.parser.parse_query(query) == [
      [Var.x, n.test['/type/type'], n.test['property']],
    ]
    
  def test_full_line_comment(self):
    query = """
      x[test./type/type] = test.property
      # this is a comment
    """
    assert self.parser.parse_query(query) == [
      [Var.x, n.test['/type/type'], n.test['property']],
    ]
    
  def test_after_triple_comment(self):
    query = """
      x[test./type/type] = test.property # this is a comment
    """
    assert self.parser.parse_query(query) == [
      [Var.x, n.test['/type/type'], n.test['property']],
    ]
  
  def test_comment_in_middle_of_query(self):
    query = """
      x[test./type/type] = test.property
      # this is a comment
      x[test./type/type] = test.property
    """
    assert self.parser.parse_query(query) == [
      [Var.x, n.test['/type/type'], n.test['property']],
      [Var.x, n.test['/type/type'], n.test['property']],
    ]
  
  def test_implied_var(self):
    query = """
      x[test.test][test.test] = 1
    """
    assert self.parser.parse_query(query) == [
      [Var.x, n.test['test'], Var.bnode1],
      [Var.bnode1, n.test['test'], 1]
    ]
  
  #def test_implied_type(self):
    #query = """
      #x[test.test] = "day before %:dt.date%"
    #"""
    #ret = self.parser.parse_query(query)
    #p('ret', ret)
    #assert ret == [
      #[Var.x,      n.test['test'],  "day before %date_auto_str%"],
      #[Var.bnode1, n.axpress['is'], "%date_auto_str%"],
      #[Var.bnode1, n.dt['date'],    LitVar.date],
    #]

  def test_multiLineOr(self):
    query = """
      i[flickr.tag] = 'sunset' |
                      'sunrise'
    """
    assert self.parser.parse_query(query) == [
      [Var.i, n['flickr']['tag'], ['sunset', 'sunrise']],
    ]

  def test_optional(self) :
    query = """
      x[test.foo] = y
      | x[test.bar] = z
    """
    assert self.parser.parse_query(query) == [
             [Var.x, n['test']['foo'], Var.y],
      Triple([Var.x, n['test']['bar'], Var.z], optional=True),
    ]
    
  def test_unknown(self) :
    query = """
      weather[axpress.is] = "current weather in bloomington, indiana"
      weather[test.current_temperature] = _current_temperature
    """
    ret = self.parser.parse_query(query)
    #p('ret', ret)
    assert ret == [
      [ Var.weather, n.axpress['is'], 'current weather in bloomington, indiana', ],
      [ Var.weather, n.test.current_temperature, LitVar.current_temperature, ],
    ]

  def test_simple_string_var(self) :
    query = """
      book[axpress.is] = "%title%"
      book[test.type] = _type
    """
    ret = self.parser.parse_query(query)
    #p('ret', ret)
    assert ret == [
      [ Var.book, n.axpress['is'], '%title%', ],
      [ Var.book, n.test.type, LitVar.type, ],
    ]
  
  def test_broken_once(self) :
    query = """
      r = test.new(dt, "bzzt ... alarm!")
      dt[test.datetime] = "%datetime%"
    """
    ret = self.parser.parse_query(query)
    #p('ret', ret)
    assert ret == [
      [ n.test.new, Var.dt, "bzzt ... alarm!", Var.r],
      [ Var.dt, n.test.datetime, "%datetime%"],
    ]

  def test_nested_fns(self) :
    query = """
      x = test.foo(test.bar(1), test.baz(2), 3)
    """
    ret = self.parser.parse_query(query)
    #p('ret', ret)
    assert ret == [
      [ n.test.bar, 1, Var.bnode1, ],
      [ n.test.baz, 2, Var.bnode2, ],
      [ n.test.foo, Var.bnode1, Var.bnode2, 3, Var.x, ],
    ]
    
if __name__ == "__main__" :
  unittest.main()


#print parse("image[image.average_color] = color")
#print parse("distance = color.distance(color.red, color)")
#print parse("sparql.order_ascending = color.distance(color.red, image[image.average_color])")

