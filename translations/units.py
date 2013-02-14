from SimpleSPARQL.PrettyQuery import prettyquery as p

def loadTranslations(axpress) :
    axpress.n.bind('u', '<http://dwiel.net/axpress/units/0.1/>')
    rule = axpress.rule

    # could go in a string/std library somewhere
    # could also use at some point to add word number parsing ...
    def str_to_float(vars) :
        vars['f'] = float(vars['s'])
    def infn(vars) :
        try :
            float(vars['s'])
            return True
        except :
            return False
    rule('str to float', """
        a.float(_s) = f
    """, """
        _f[a.type] = a.float
    """, str_to_float, infn)

    def unit(names, square=True) :
        singular = names[0].replace(' ', '_')
        plural = names[1].replace(' ', '_')

        # parsing the unit
        rule('parse %s str' % singular,
             '_[a.is] = "%i% ({s})"'.format(s='|'.join(names)),
             #'_[u.%s] = a.float(_i)' % plural)
             '_[u.{plural}] = a.float("%i%")'.format(plural=plural))

        # TODO: should be able to use _length instead of "%length%" in
        # the output
        # parsing the string request a length in particular units
        rule('length in %s' % plural,
             '_[a.is] = "%length% in ({s})"'.format(s='|'.join(names)),
             """
              _[a.is] = "%length%"
              _[speech.out] = _[u.{plural}_str]
             """.format(plural=plural))

        # converting the unit back into a string
        def f_str(vars) :
            vars['str'] = '%0.3f %s' % (vars['f'], plural)
        rule('%s to str' % plural,
             "_[u.%s] = _f" % plural,
             "_[u.%s_str] = _str" % plural,
             f_str
        )

        """
        # square units
        sq_names = []
        sq_names.extend('square %s' for name in names)
        sq_names.extend('sq %s' for name in names)
        sq_names.extend('%s^2' for name in names)
        unit(sq_names, False)
        """

    unit(['inch', 'inches', 'in'])
    unit(['foot', 'feet', 'ft'])
    unit(['yard', 'yards', 'yd', 'yds'])
    unit(['mile', 'miles', 'mi'])
    unit(['cm', 'centimeters', 'centimeter'])
    unit(['mm', 'milimeters', 'milimeter'])
    unit(['m', 'meters', 'meter', 'ms'])

    def conv(src, dest, fn) :
        def wrapper_fn(vars) :
            vars['out'] = fn(vars['in'])
        rule("%s -> %s" % (src, dest),
             "_[u.%s] = _in" % src,
             """_[u.%s] = _out
                _out[a.type] = a.float""" % dest,
             wrapper_fn)
    def rconv(src, dest, m) :
        conv(src, dest, lambda x:x*m)
        conv(dest, src, lambda x:x/m)
    # by only defining some transitions, movement between all is
    # possible, could this be precompiled?
    # 1 in in feet - 0.5 seconds compile time
    # 1 in in milimeters - 2.4 seconds compile time
    rconv('feet', 'inches', 12)
    rconv('feet', 'yards', 1/3.)
    rconv('feet', 'meters', 0.3048)
    rconv('meters', 'kilometers', 0.001)
    rconv('meters', 'centimeters', 100)
    rconv('meters', 'milimeters', 1000)

    """
    def square_unit(names) :
        unit(sq_names)
    square_unit(['meter', 'meters', 'm', 'ms'])
    square_unit(['kilometer', 'kilometers', 'km', 'kms'])
    """

    """
    # this could work, but it would help if we knew the type of _xm and _ym ...
    # I was able to add type info to the rules above, but realized that won't
    # work in this case where the meters are supplied directly
    # there is an implicit type for u.meters ...
    
    x[u.meters] = _xm
    y[u.meters] = _ym
    z = a.mul(x, y)
      =>
    z[u.sq_meters] = a.mul(_xm, _ym)
    """
    
    """
    x[u.meters] = 10
    y[u.meters] = 10
    z = a.mul(x, y)
    z[u.sq_meters] = _out
    """

def test(axpress) :
    def speech(s) :
        return axpress.read_translate("""
            x[axpress.is] = "%s"
            x[speech.out] = _out
        """ % s)[0]['out']
    
    #assert speech('1 inch in meters') == "0.025 meters"
    #assert speech('1 foot in inches') == "12.000 inches"
    assert speech('1 foot in meters') == "0.305 meters"

if __name__ == '__main__' :
    test()
        
