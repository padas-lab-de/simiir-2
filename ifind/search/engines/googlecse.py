import json
import requests
from ifind.search.engine import Engine
from ifind.search.response import Response
from ifind.search.exceptions import EngineAPIKeyException, QueryParamException, EngineConnectionException

# TODO: Bug fix - utils and utils.encoding do not exist
# from ifind.utils.encoding import encode_symbols



import time

API_ENDPOINT = "https://www.googleapis.com/customsearch/v1/"

# TODO: Temp limits.  Just returns the first page.  Google currently requires a paid API key.
MAX_PAGE_SIZE = 10
MAX_RESULTS = 10

RESULT_TYPES = ('web', 'image')
DEFAULT_RESULT_TYPE = 'web'

class Googlecse(Engine):
    """
    GoogleCustomSearch search engine.

    """

    def __init__(self, api_key='', cx='', **kwargs):
        """
        Google engine constructor.

        Kwargs:
            api_key (str): string representation of api key needed to access google custom search api
            cx (str): string representation of the cx parameter needed to access google custom search api
            See Engine.

        Raises:
            EngineException

        Usage:
            engine = EngineFactory('GoogleCSE', api_key='etc123456etc123456etc123456', cx='abc123abc123abc123')

        """
        Engine.__init__(self, **kwargs)
        self.api_key = api_key
        self.cx = cx

        if not self.api_key:
            raise EngineAPIKeyException(self.name, "'api_key=' keyword argument not specified")

        if not self.cx:
            raise EngineAPIKeyException(self.name, "'cx=' keyword argument not specified")

        self.default_result_type = kwargs.get('default_result_type', DEFAULT_RESULT_TYPE)
        # Catch empty strings and such.
        if not self.default_result_type:
            self.default_result_type = DEFAULT_RESULT_TYPE


    def _search(self, query):
        # TODO: Fix comments
        """
        Concrete method of Engine's interface method 'search'.
        Performs a search and retrieves the results as an ifind Response.

        Args:
            query (ifind Query): Object encapsulating details of a search query.

        Query Kwargs:
            result_type (str): specifies the type of results to return (see top of class for available types).
            top (int): number of tweets to return up to MAX_PAGE_SIZE
        Returns:
            ifind Response: object encapulsating a search request's results.

        Raises:
            EngineException

        Usage:
            Private method.

        Notes:
            https://developers.google.com/custom-search/ for full API documentation.

        """
        if not query.top:
            raise QueryParamException(self.name, "Total result amount (query.top) not specified")

        if query.top > MAX_RESULTS:
            raise QueryParamException(self.name, 'Requested result amount (query.top) '
                                                 'exceeds max of {0}'.format(MAX_PAGE_SIZE))

        # TODO: Currently assumes that all results fit on one page (query.top <= MAX_PAGE_SIZE)
        return self._request(query)


    def _request(self, query):

        """
        Issues a single request to the API_ENDPOINT and returns the result as
        an ifind Response.

        Args:
            query (ifind Query): object encapsulating details of a search query.

        Returns:
            ifind Response: object encapsulating a search request's results.

        Raises:
            EngineException

        Usage:
            Private method.

        """
        query_string = self._create_query_string(query)

        try:
            response = requests.get(query_string)
        except requests.exceptions.ConnectionError:
            raise EngineConnectionException(self.name, "Unable to send request, check connectivity.")

        if response.status_code != 200:
            raise EngineConnectionException(self.name, "", code=response.status_code)

        return self._parse_json_response(query, response)


    def _create_query_string(self, query):
        """
        Creates and returns Google Custom Search API query string with encoded query parameters.

        Args:
            query (ifind Query): object encapsulating details of a search query.

        Returns:
            str: query string for Google Custom Search API request

        Raises:
            EngineException

        Usage:
            Private method.

        """

        # Check for a result type, if none found, set it to default.
        result_type = query.result_type
        if not result_type:
            result_type = self.default_result_type

        # Check to if the result type is valid
        if result_type not in RESULT_TYPES:
            raise QueryParamException(self.name, "Engine doesn't support query result type '{0}'"
                                                 .format(query.result_type))

        if query.top and query.top <= MAX_PAGE_SIZE:
            top = query.top
        else:
            top = MAX_PAGE_SIZE

        # TODO: Should be all necessary parameters.
        # Dictionary of search paramaters
        search_params = {
                         'q': query.terms,
                         'top':top
                         }

        # TODO: Replace .replace() function with a substitute of 'encode_symbols' function.  encode_symbols no longer exists
        # Craft the string to append to the endpoint url
        if result_type in ['web', 'image']:
            query_append = "?&key={}&cx={}&q={}&num={}".format\
                (self.api_key, self.cx,
                 search_params['q'].replace(' ','+'), search_params['top'])



        # return API_ENDPOINT + encode_symbols(query_append)
        return API_ENDPOINT + query_append



    def _parse_json_response(self, query, results):
        """
        Parses Google Custom Search's JSON response and returns as an ifind Response.

        Args:
            query (ifind Query): object encapsulating details of a search query.
            results : requests library response object containing search results.

        Returns:
            ifind Response: object encapsulating a search request's results.

        Usage:
            Private method.
        """

        response = Response(query.terms, query)
        content = json.loads(results.text)

        # The query object wasn't mutated earlier and the result type isn't passed to this function.
        # Check for a result_type or set it to default.
        result_type = query.result_type
        if not result_type:
            result_type = self.default_result_type

        # Check for a next page token.
        next_page_token = content.get(u'nextPageToken')
        if next_page_token:
            # A page token exists, create the URL which will fetch the next page
            response.next_page = "{}&pageToken={}".format(self._create_query_string(query), next_page_token)

        rank_counter = 1

        if result_type == 'web' or not query.result_type:
            for result in content[u'items']:
                title = result[u'title']
                url = result[u'link']
                summary = result[u'snippet']
                response.add_result(title=title, url=url, summary=summary, rank=rank_counter)
                rank_counter+=1

        return response
