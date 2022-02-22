import json
import requests
from ifind.search.engine import Engine
from ifind.search.response import Response
from ifind.search.exceptions import EngineConnectionException, QueryParamException

API_ENDPOINT = 'https://www.gov.uk/api/search.json?q='


class Govuk(Engine):
    """
    GOV.uk search engine.

    """
    def __init__(self, **kwargs):
        """
        GOV.uk engine constructor.

        Kwargs:
            See Engine.

        Usage:
            See EngineFactory.

        """
        Engine.__init__(self, **kwargs)

    def _search(self, query):
        """
        Concrete method of Engine's interface method 'search'.
        Performs a search and retrieves the results as an ifind Response.

        Args:
            query (ifind Query): object encapsulating details of a search query.

        Query Kwargs:
            top (int): specifies maximum amount of results to return, no minimum guarantee

        Returns:
            ifind Response: object encapulsating a search request's results.

        Raises:
            EngineException

        Usage:
            Private method.

        """
        if not query.top:
            raise QueryParamException(self.name, "Total result amount (query.top) not specified")

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
        search_params = {'q': query.terms}

        try:
            response = requests.get(API_ENDPOINT + search_params['q'])
        except requests.exceptions.ConnectionError:
            raise EngineConnectionException(self.name, "Unable to send request, check connectivity")

        if response.status_code != 200:
            raise EngineConnectionException(self.name, "", code=response.status_code)

        return Govuk._parse_json_response(query, response)

    @staticmethod
    def _parse_json_response(query, results):
        """
        Parses GOV.uk's JSON response and returns as an ifind Response.

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

        # The base url - results do not provide a full link.
        base_url = "https://www.gov.uk"
        rank = 0

        for result in content[u'results']:
            text = result.get(u'description', '')
            title = result[u'title']
            url = base_url + result[u'link']
            rank = rank + 1
            # Add the result to the ifind response
            response.add_result(title=title, url=url, summary=text, rank=rank)

            if len(response) == query.top:
                break

        return response