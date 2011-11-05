# NOTE: depends on freebase

import json
import urllib2

def loadTranslations(axpress, n) :
  n.bind('wunderground', '<http://dwiel.net/axpress/wunderground/0.1/>')

  axpress.register_translation({
    n.meta.name : 's current weather',
    n.meta.input : """
      weather[axpress.is] = "(the |)(current |)(weather|temperature|temp) (in |at |near |by |near by |)%location_s%( right now| now|)"
    """,
    n.meta.output : """
      location[axpress.is] = "%location_s%"
      location[freebase.type] = '/location/location'
      location[wunderground.weather] = weather
    """,
  })
  
  def lookup_current_weather(vars) :
    return json.loads(
      urllib2.urlopen(
        "http://api.wunderground.com/api/648fbe96a3f5358d/conditions/q/%s,%s.json" % (
          vars['lat'], vars['lon']
        )
      ).read()
    )['current_observation']
  
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
      weather[wunderground.current_temperature] = _temp_f
    """,
    n.meta.function : lookup_current_weather,
  })
  
  # Simple Display
  axpress.register_translation({
    n.meta.name : 'simple render temp',
    n.meta.input : """
      x[wunderground.current_temperature] = _out
    """,
    n.meta.output : """
      x[simple_display.text] = _out
    """,
  })
  
  

  
  