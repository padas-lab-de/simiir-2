__author__ = 'leif'


from ifind.search.engines.bing import Bing
from ifind.search.query import Query

class Sitebing(Bing):

    def __init__(self, api_key='', site='gla.ac.uk', **kwargs):
        """
        Bing engine constructor.

        Kwargs:
            api_key (str): string representation of api key needed to access bing search api
            See Engine.

        Raises:
            EngineException

        Usage:
            engine = EngineFactory('bing', api_key='etc123456etc123456etc123456')

        """
        Bing.__init__(self, api_key, **kwargs)
        self.site = site



    def search(self, query):
        """
        Public search method for an Engine instance, returning the results of a query argument.
        Caching handled here, true search implementation deferred to subclass '_search' method.

        Args:
            query (ifind Query): object encapsulating details of search query.

        Returns:
            ifind Response: object encapsulating a search request's results.

        Raises:
            CacheException, InvalidQueryException

        Usage:
            query = Query('hello world')
            engine = EngineFactory('wikipedia')
            response = engine.search(query)

        """
        query.terms = '%s site:%s' % (query.terms, self.site)

        return super(Sitebing,self).search(query)

