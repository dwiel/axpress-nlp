## -*- coding: utf-8 -*-
# NOTE: depends on freebase

from SimpleSPARQL.Utils import p

import json
import urllib2

from mako.template import Template

"""
How to selectively show the dew point, along with the rest of the forecast.

generating just the susinct answer is different than generating other relevant
information.  Ideally, the former problem is a subset of the later.
"""

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
  
  axpress.register_translation({
    n.meta.name : 's current weather',
    n.meta.input : """
      weather[axpress.is] = "(the |)(current |)dew point (in |at |near |by |near by |)%location_s%( right now| now|)"
    """,
    n.meta.output : """
      location[axpress.is] = "%location_s%"
      location[freebase.type] = '/location/location'
      location[wunderground.weather] = weather
      weather[wunderground.dew_point] = dew_point
    """,
  })
  
  def lookup_current_weather(vars) :
    conditions = json.loads(
      urllib2.urlopen(
        "http://api.wunderground.com/api/648fbe96a3f5358d/conditions/q/%s,%s.json" % (
          vars['lat'], vars['lon']
        )
      ).read()
    )
    
    forecast_ret = json.loads(
      urllib2.urlopen(
        "http://api.wunderground.com/api/648fbe96a3f5358d/forecast7day/q/%s,%s.json" % (
          vars['lat'], vars['lon']
        )
      ).read()
    )
    
    forecast = []
    for day in forecast_ret['forecast']['simpleforecast']['forecastday'] :
      forecast.append({
        'weekday'  : day['date']['weekday_short'],
        'high'     : day['high']['fahrenheit'],
        'low'      : day['low']['fahrenheit'],
        'icon_url' : day['icon_url'],
      })
    
    ret = conditions['current_observation']
    ret['forecast'] = tuple(forecast)
    
    p('ret', ret)
    return ret
  
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
      weather[wunderground.icon_url] = _icon_url
      weather[wunderground.forecast] = _forecast
    """,
    n.meta.function : lookup_current_weather,
  })
  
  # Simple Display
  def render_weather(vars) :
    vars['out'] = Template(u"""## -*- coding: utf-8 -*-
      <div id="weather" style="width:378px">
        <div id="today" style="margin:auto;width:220px">
          <div id="temp" style="font-size:350%;float:left;padding-left:0em;padding-right:0.5em">
            ${temp}° F
          </div>
          <img src="${icon_url}" style="float:right;padding-top:7px">
          <div style="clear:both"></div>
        </div>
        <div id="forecast" style="padding-top:1em;text-align:center;text-transform:uppercase">
          % for day in forecast :
            <div class="day" style="float:left">
              <div class="weekday">${day['weekday']}</div>
              <div class="icon"><img src="${day['icon_url']}"></div>
              <div class="high" style="font-size:150%">${day['high']}</div>
              <div class="low" style="font-size:150%">${day['low']}</div>
            </div>
          % endfor
          <div style="clear:both" />
        </div>
      </div>
      """).render_unicode(**vars)
  axpress.register_translation({
    n.meta.name : 'simple render temp',
    n.meta.input : """
      x[wunderground.current_temperature] = _temp
      x[wunderground.icon_url] = _icon_url
      x[wunderground.forecast] = _forecast
    """,
    n.meta.output : """
      x[simple_display.text] = _out
    """,
    n.meta.function : render_weather
  })
  
  

  
  