import os
import redis
import pickle
import base64
from time import strftime, gmtime
from ifind.search.exceptions import CacheConnectionException


MODULE = os.path.basename(__file__).split('.')[0].title()
CACHE_TYPES = ('engine', 'instance')


class RedisConn(object):
    """
    Object to handle redis connection and configuration.

    """

    def __init__(self, host="localhost", port=6379, db=0, limit=10000000, password=''):
        self.host = host
        self.port = port
        self.password = password
        self.db = db
        self.connection = None
        self.set_name = 'default'
        self.limit = limit
        self.expires = 60 * 60 * 24*7

    def connect(self):
        """
        Connect method fails silently, ping is used to validate connection.

        Returns:
            StrictRedis client instance: Redis client object.

        Raises:
            CacheException

        Usage:
            connection = RedisConn(host='localhost', port=6379, db=0).connect()

        """
        try:
            ping_result = redis.StrictRedis(host=self.host, port=self.port, password=self.password).ping()
            #print "CACHE: ping result - {0}".format(ping_result)
        except redis.ConnectionError:
            raise CacheConnectionException(MODULE, "Failed to establish connection to "
                                                   "redis server @ {0}:{1}".format(self.host, self.port))

        self.connection = redis.StrictRedis(host=self.host, port=self.port, db=self.db)
        return self.connection


    def store(self, key, v):
        """
        Serialises and stores the value at the key location.

        Args:
            key:
            value:
            expires (int): amount of time for key to remain in database (seconds)
        """


        while self.connection.zcard(self.set_name) >= self.limit:
            key = self.connection.zremrangebyrank(self.set_name, 0, 0)
            self.connection.delete(key)

        value = base64.b64encode(pickle.dumps(v))

        pipe = self.connection.pipeline()
        pipe.hmset(key, {'response': value, 'count': 0, 'last': ''})
        pipe.zadd(self.set_name, 0, key)
        #pipe.expire(key, self.expires)
        pipe.execute()

    def get(self, key):
        """
        Retrieves a value associated with the key, returning None if not found.
        Args:
            key
        Returns:
            value
        """
        value = self.connection.hget(key, 'response')

        if value:
            pipe = self.connection.pipeline()
            pipe.hincrby(key, 'count', 1)
            pipe.hset(key, 'last', strftime("%Y/%m/%d %H:%M:%S", gmtime()))
            pipe.zincrby(self.set_name, key, 1)
            pipe.execute()
            return pickle.loads(base64.b64decode(value))
        else:
            return None
            
    def exists(self, key):
        return self.connection.exists(key)

    def keys(self, wildcard):
        return self.connection.keys(wildcard)
    
    def __contains__(self, key):
        """
        Special containment override for 'in' operator.

        """
        return self.connection.exists(key)


class QueryCache(object):
    """
    An object representing a query cache, assigned to an Engine instance upon its
    instantiation. Allows for the caching of ifind Response objects.

    """

    def __init__(self, engine, host='localhost', port=6379, db=0,
                 limit=1000, expires=60 * 60 * 24*7):
        """
        QueryCache contructor.

        Args:
            engine (ifind Engine): reference to engine that's instantiating the cache.

        Kwargs:
            host (str): hostname of redis server.
            port (int): port of redis server.
            db (int): database of redis server.
            limit (int): maximum amount of keys allowed in cache.
            expires (int): amount of time for key to remain in database (seconds(.

        Usage:
            cache = QueryCache(engine)
            cache = QueryCache(engine, limit = 10, expires=60)

        """
        self.engine_name = engine.name.lower()

        self.host = host
        self.port = port
        self.db = db

        self.limit = limit
        self.expires = expires
        self.cache_type = engine.cache_type

        self.set_name = self.get_set_name()

        self.connection = RedisConn(host=self.host, port=self.port, db=self.db).connect()

    def __del__(self):
        if self.cache_type == 'instance':
            for key in self.connection.zrange(self.set_name, 0, -1):
                self.connection.delete(key)
            self.connection.delete(self.set_name)

    def store(self, query, response, expires=None):
        """
        Serialises and stores a search response, keyed by its corresponding query.

        Args:
            query (ifind Query): object encapsulating details of search query.
            response (ifind Response): object encapsulating a search request's results.

        Kwargs:
            expires (int): amount of time for key to remain in database (seconds)

        Usage:
            cache.store(query, response)
            cache.store(query, response, expires=60 * 60)

        """
        if query in self:
            return

        while self.connection.zcard(self.set_name) >= self.limit:
            key = self.connection.zremrangebyrank(self.set_name, 0, 0)
            self.connection.delete(key)

        if expires is None:
            expires = self.expires

        key = self._make_key(query)
        value = base64.b64encode(pickle.dumps(response))

        pipe = self.connection.pipeline()
        pipe.hmset(key, {'response': value, 'count': 0, 'last': ''})
        pipe.zadd(self.set_name, 0, key)
        pipe.expire(key, expires)
        pipe.execute()

    def get(self, query):
        """
        Retrieves a query's response, returning None if not found.

        Args:
            query (ifind Query): object encapsulating details of search query.

        Returns:
            ifind Response: object encapsulating a search request's results.

        Usage:
            response = cache.get(query)

        """
        key = self._make_key(query)
        value = self.connection.hget(key, 'response')

        if value:
            pipe = self.connection.pipeline()
            pipe.hincrby(key, 'count', 1)
            pipe.hset(key, 'last', strftime("%Y/%m/%d %H:%M:%S", gmtime()))
            pipe.zincrby(self.set_name, key, 1)
            pipe.execute()
            return pickle.loads(base64.b64decode(value))
        else:
            return None

    def _make_key(self, query):
        """
        Creates key string for query, depending on cache type specified.

        Args:
            query (ifind Query): object encapsulating details of search query.

        Returns:
            str: query's unique key to be used as lookup in cache

        Usage:
            Private method.

        """
        hash_query = hash(query.terms + ' '+ str(query.top)+ ' ' + str(query.skip))

        if self.cache_type.lower() == 'engine':

            return "QueryCache::{0}::{1}".format(self.engine_name, hash_query)
        if self.cache_type.lower() == 'instance':
            return "QueryCache::{2}{0}::{1}".format(id(self), hash_query, self.engine_name)

    def get_set_name(self):

        if self.cache_type.lower() == 'engine':
            return "QueryCache::{0}-keys".format(self.engine_name)
        if self.cache_type.lower() == 'instance':
            return "QueryCache::{1}{0}-keys".format(id(self), self.engine_name)

    def __contains__(self, query):
        """
        Special containment override for 'in' operator.

        Usage:
            response = engine.search(query)
            print len(response) --> 10

        """
        return self.connection.exists(self._make_key(query))
