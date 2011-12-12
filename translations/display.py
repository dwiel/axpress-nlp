from mako.template import Template
import freebase

def loadTranslations(axpress, n) :
  n.bind('display', '<http://dwiel.net/axpress/display/0.1/>')
  n.bind('simple_display', '<http://dwiel.net/axpress/simple_display/0.1/>')
  n.bind('freebase', '<http://dwiel.net/axpress/freebase/0.1/>')

  def display_html_filenames(vars) :
    str = "<ul>"
    for filename in vars['filenames'] :
      str += "<li>" + filename
    str += "</ul>"
    return str
  axpress.register_translation({
    n.meta.name : 'filename as html',
    n.meta.input : """
      file[file.filename] = _filename
    """,
    n.meta.output : """
      file[display.html] = _html
    """,
    n.meta.function : display_html_filenames,
  })

  def simple_render(bindings_set) :
    blurbs = get_blurbs([b['mid'] for b in bindings_set])
    
    for vars, blurb in zip(bindings_set, blurbs) :
      vars['html'] = Template(u"""## -*- coding: utf-8 -*-
      <div class="item">
        <div class="image">
          <img src='http://api.freebase.com/api/trans/image_thumb/${mid}?maxwidth=150' style='width:150px;height:150px'>
        </div>
        <div class="side">
          <div class="title"><a href="freebase.com/view${mid}">${name}</a></div>
          <div class="blurb">${blurb}</div>
        </div>
        <div class="clear" />
      </div>
      """).render_unicode(blurb = blurb, **vars)
  axpress.register_translation({
    n.meta.name : 'freebase simple render',
    n.meta.input : """
      x[freebase.name] = name
      x[freebase.mid] = _mid
      x[freebase.blurb] = _blurb
    """,
    n.meta.output : """
      x[simple_display.text] = _html
    """,
    n.meta.multi_function : simple_render,
  })
  
  def direct_related(vars) :
      vars['out'] = Template(u"""## -*- coding: utf-8 -*-
      <div id="two_pane" style="width:400px">
        <div id="direct">
          <div style="font-size:350%;text-align:center">
            ${direct_label}${direct}
          </div>
        </div>
        <div id="related">
          ${related}
        </div>
      </div>
      """).render_unicode(**vars)
    #vars['out'] = unicode(vars['direct']) + unicode(vars['related'])
  axpress.register_translation({
    n.meta.name : 'two pane render',
    n.meta.input : """
      x[simple_display.direct_label] = _direct_label
      x[simple_display.direct] = _direct
      x[simple_display.related][simple_display.text] = _related
    """,
    n.meta.output : """
      x[simple_display.text] = _out
    """,
    n.meta.function : direct_related,
  })
