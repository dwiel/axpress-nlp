"""The application's Globals object"""

from beaker.cache import CacheManager
from beaker.util import parse_cache_config_options

from SimpleSPARQL import *

class Globals(object):
    """Globals acts as a container for objects available throughout the
    life of the application

    """

    def __init__(self, config):
        """One instance of Globals is created during application
        initialization and is available during requests via the
        'app_globals' variable

        """
        self.cache = CacheManager(**parse_cache_config_options(config))

        #self.sparql = SimpleSPARQL("http://localhost:2020/sparql")
        #self.sparql.setGraph("http://dwiel.net/axpress/testing")

        """
        n = self.sparql.n
        n.bind('math', '<http://dwiel.net/express/math/0.1/>')
        n.bind('glob', '<http://dwiel.net/express/glob/0.1/>')
        n.bind('color', '<http://dwiel.net/express/color/0.1/>')
        n.bind('sparql', '<http://dwiel.net/express/sparql/0.1/>')
        n.bind('call', '<http://dwiel.net/express/call/0.1/>')
        n.bind('library', '<http://dwiel.net/axpress/library/0.1/>')
        n.bind('music', '<http://dwiel.net/axpress/music/0.1/>')
        n.bind('music_album', '<http://dwiel.net/axpress/music_album/0.1/>')
        n.bind('source', '<http://dwiel.net/axpress/source/0.1/>')
        n.bind('lastfm', '<http://dwiel.net/axpress/lastfm/0.1/>')
        n.bind('rdfs', '<http://www.w3.org/2000/01/rdf-schema#>')
        n.bind('bound_var', '<http://dwiel.net/axpress/bound_var/0.1/>')
        n.bind('amos', '<http://dwiel.net/axpress/amos/0.1/>')
        a = n.rdfs.type

        self.compiler = Compiler(n)
        self.evaluator = Evaluator(n)
        
        self.axpress = Axpress(
          sparql = self.sparql,
          compiler = self.compiler,
          evaluator = self.evaluator
        )
        loadTranslations(self.axpress, n)
        """
        
        self.axpress = Axpress()
        loadTranslations(self.axpress)
