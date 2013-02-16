# super fast __eq__ (turns out to be slow for other things though ...)
class URIRef(int) :
    uri_to_id = {'' : 0}
    def __new__(cls, uri) :
        try :
            i = URIRef.uri_to_id[str(uri)]
        except KeyError :
            i = len(URIRef.uri_to_id)
            URIRef.uri_to_id[str(uri)] = i
        ret = super(URIRef, cls).__new__(cls, i)
        ret.uri = uri
        return ret
    def __str__(self) :
        return self.uri
    
    def __getslice__(self, *args, **kwargs) :
        return self.uri.__getslice__(*args, **kwargs)
    def __add__(self, other) :
        return self.uri + str(other)
    def __iter__(self) :
        return iter(self.uri)
class URIRef(str) : pass
#from rdflib import URIRef

def test() :
    a = URIRef('http://dwiel.net/axpress/datetime/0.1/')
    b = URIRef('http://dwiel.net/axpress/datetime/0.1/')
    c = URIRef('http://dwiel.net/axpress/date/0.1/')

    assert a == b
    assert a != c
    
if __name__ == '__main__' :
    test()
