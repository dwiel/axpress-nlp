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
        
        self.axpress = Axpress()
