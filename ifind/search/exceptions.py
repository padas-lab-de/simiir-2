# TODO When raising an exception pass a lambda function, the function being the module/path/name thing

ERROR = {'default': "Unknown engine error ({0})",
         400: "Bad request sent to search API ({0})",
         401: "Incorrect API Key ({0})",
         403: "Correct API but request refused ({0})",
         404: "Bad request sent to search API ({0})"}


class SearchException(Exception):
    """
    Abstract class representing an ifind search exception.

    """
    def __init__(self, module, message):
        """
        SearchException constructor.

        Args:
            module (str): name of module/class that's raising exception
            message (str): exception message to be displayed

        Usage:
            raise SearchException("Test", "this is an error")

        """
        message = "{0} - {1}".format(module, message)
        Exception.__init__(self, message)


class EngineConnectionException(SearchException):
    """
    Thrown when an Engine connectivity error occurs.
    Returns specific response message if status code specified.

    """
    def __init__(self, engine, message, code=None):
        """
        EngineException constructor.

        Args:
            engine (str): name of engine that's raising exception
            message (str): exception message to be displayed (ignored usually here)

        Kwargs:
            code (int): response status code of issued request

        Usage:
            raise EngineException("Bing", "", code=200)

        """
        self.message = message
        self.code = code

        if code:
            self.message = ERROR.get(code, ERROR['default']).format(self.code)

        SearchException.__init__(self, engine, self.message)


class EngineLoadException(SearchException):
    """
    Thrown when an Engine can't be dynamically loaded.

    """
    pass


class EngineAPIKeyException(SearchException):
    """
    Thrown when an Engine's API key hasn't been provided.

    """
    pass


class QueryParamException(SearchException):
    """
    Thrown when a query parameters incompatible or missing.

    """
    pass


class CacheConnectionException(SearchException):
    """
    Thrown when cache connectivity error occurs.

    """
    pass


class InvalidQueryException(SearchException):
    """
    Thrown when an invalid query is passed to engine's search method.

    """
    pass


class RateLimitException(SearchException):
    """
    Thrown when an engine's request rate limit has been exceeded.

    """
    pass