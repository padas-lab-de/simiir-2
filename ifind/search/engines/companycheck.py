import json
import requests
from ifind.search.engine import Engine
from ifind.search.response import Response
from ifind.search.exceptions import EngineAPIKeyException, QueryParamException, EngineConnectionException
from ifind.utils.encoding import encode_symbols

API_ENDPOINT = "https://companycheck.co.uk/api/json/"

RESULT_TYPES = ('company', 'director')
DEFAULT_RESULT_TYPE = 'company'


class Companycheck(Engine):
    """
    Companycheck search engine.

    """

    def __init__(self, api_key='', **kwargs):
        """
        Companycheck engine constructor.

        Kwargs:
            api_key (str): string representation of api key needed to access the CompanyCheck search api
            default_result_type (str): Optionally provide a default result type.
            See Engine.

        Raises:
            EngineException

        Usage:
            engine = EngineFactory('Companycheck api_key='etc123456etc123456etc123456')

        """
        Engine.__init__(self, **kwargs)
        self.api_key = api_key

        if not self.api_key:
            raise EngineAPIKeyException(self.name, "'api_key=' keyword argument not specified")

        self.default_result_type = kwargs.get('default_result_type', DEFAULT_RESULT_TYPE)
        # Catch empty strings and such.
        if not self.default_result_type:
            self.default_result_type = DEFAULT_RESULT_TYPE

    def _search(self, query):
        """
        Concrete method of Engine's interface method 'search'.
        Performs a search and retrieves the results as an ifind Response.

        Args:
            query (ifind Query): Object encapsulating details of a search query.

        Query Kwargs:
            result_type (str): specifies the type of results to return (see top of class for available types).
            postcode (str): an additional postcode to include in the query

        Returns:
            ifind Response: object encapulsating a search request's results.

        Raises:
            EngineException

        Usage:
            Private method.

        Notes:
          http://help.companycheck.co.uk/hc/en-us/articles/202713993-API-JSON-Documentation for full API documentation.

        """
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
        Creates and returns Companycheck API query string with encoded query parameters.

        Args:
            query (ifind Query): object encapsulating details of a search query.

        Returns:
            str: query string for Companycheck API request

        Raises:
            EngineException

        Usage:
            Private method.

        """

        result_type = query.result_type
        if not result_type:
            result_type = self.default_result_type

        # Check to if the result type is valid
        if result_type:
            if result_type not in RESULT_TYPES:
                raise QueryParamException(self.name, "Engine doesn't support query result type '{0}'"
                                                 .format(query.result_type))

        # Fetch the postcode keyword
        postcode = query.__dict__.get('postcode', '')

        # Build the appropriate query string based on the result type
        if result_type == 'company':
            # Company search format:
            # https://companycheck.co.uk/api/json/ search?name=tesco&postcode=xxxx&apiKey=xxxxxx

            query_append = "search?name={}&postcode={}&apiKey={}".format\
                (query.terms, postcode, self.api_key)

        elif result_type == 'director':
            # Director search format:
            # https://companycheck.co.uk/api/json/ directorSearch?name=branson&postcode=W11&apiKey=xxxxxx

            query_append = "directorSearch?name={}&postcode={}&apiKey={}".format\
                (query.terms, postcode, self.api_key)
        else:
            raise QueryParamException(self.name, "No handler found for result type: {}"
                                                 .format(query.result_type))

        return API_ENDPOINT + encode_symbols(query_append)

    @staticmethod
    def _build_company_summary(company):
        """
        Builds the summary portion of the company result. This is essentially just a composite of several features in
        the response.

        :param: dict - company dictionary from the companycheck JSON response
        :return: str - summary
        """
        country = u'Country: ' + company[u'country']
        address = u'\nAddress: ' + company[u'address']
        sic = u'\nSic code: ' +  company[u'sic']
        status = u'\nStatus: ' + company[u'status']

        return country + address + sic + status

    @staticmethod
    def _build_director_summary(director):
        """
        Builds the summary portion of the directors result, this is essentially just a composite of several features in
        the resposne. Also returns a list of postcodes to be passed as keywords arguments in the response.

        :param: dict - company - company dictionary from the companycheck JSON response
        :return: dict{list, string} - containing the postcodes found as well as the string representing the summary
        """
        postcodes = []
        for pcode in director[u'registeredPostcodes']:
            postcodes.append(unicode(pcode[u'postcode0']))
        postcodes_sum = u'Registered Postcodes: ' + unicode(postcodes)

        return {'postcode_list': postcodes, 'summary': postcodes_sum}

    def _parse_json_response(self, query, results):
        """
        Parses Companycheck's JSON response and returns as an ifind Response.

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

        # The base URL to add the director or company number to, which provides the complete link.
        url_base = 'http://companycheck.co.uk/'

        # Since the object isn't mutated, set the default again if there is nothing present.
        result_type = query.result_type
        if not result_type:
            result_type = self.default_result_type


        # CompanyCheck returns all the results it has, it has no further results.
        response.no_more_results = True

        if result_type == 'company' or not result_type:
            # Create the ifind response for company searches
            for company in content:
                name = company[u'name']
                url =  url_base + 'company/' + str(company[u'number'])
                imageurl = None
                summary = Companycheck._build_company_summary(company)
                # Keyword args below
                number = company[u'number']
                country = company[u'country']
                address = company[u'address']
                sic = company[u'sic']
                status = company[u'status']
                # Add result object to the response
                response.add_result(title=name, url=url, summary=summary, imageurl=imageurl,
                                    number=number, country=country, address=address, sic=sic, status=status)

        elif result_type == 'director':
            # Create the ifind response for director searches
            for director in content:
                name = director[u'name']
                url =  url_base + 'director/' + str(director[u'number'])
                imageurl = None
                sum_dic = Companycheck._build_director_summary(director)
                summary = sum_dic.get('summary')
                # Keyword args below
                postcodes = sum_dic.get('postcode_list')
                number = director[u'number']
                # Add result object to the response
                response.add_result(title=name, url=url, summary=summary, imageurl=imageurl, postcodes=postcodes,
                                    number=number)

        return response