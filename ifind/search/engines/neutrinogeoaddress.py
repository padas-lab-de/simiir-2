__author__ = 'smck'
import json
import requests
from ifind.search.engine import Engine
from ifind.search.response import Response
from ifind.search.exceptions import EngineAPIKeyException, QueryParamException, EngineConnectionException
from ifind.utils.encoding import encode_symbols
from string import maketrans


API_ENDPOINT = "https://neutrinoapi.com/geocode-address"


class Neutrinogeoaddress(Engine):
    """
    Neutrinogeoaddress search engine.

    """

    def __init__(self, api_key='', username='', google_api_key='', **kwargs):
        """
        Neutrinogeoaddress engine constructor.

        Kwargs:
            api_key (str): string representation of api key needed to access the search api
            username (str): string representing the username associated with the service
            google_api_key(str): string representation of a Google API key which has map API permissions, this is used
                for generating the iframe url for embedded maps.
            See Engine.

        Raises:
            EngineException

        Usage:
            engine = EngineFactory('Neutrinogeoaddress api_key='etc123456etc123456etc123456', username='someguy',
                                    google_api_key='12313414412')

        """
        Engine.__init__(self, **kwargs)
        self.api_key = api_key
        self.username = username
        self.google_api_key = google_api_key

        self.country_code = kwargs.get('country_code', 'GB')  # Set country code to GB if not found
        self.language_code = kwargs.get('language_code', '')

        if not self.api_key:
            raise EngineAPIKeyException(self.name, "'api_key=' keyword argument not specified")
        elif not self.username:
            raise EngineAPIKeyException(self.name, "'username=' keyword argument not specified")

    def _search(self, query):
        """
        Concrete method of Engine's interface method 'search'.
        Performs a search and retrieves the results as an ifind Response.

        Args:
            query (ifind Query): Object encapsulating details of a search query.

        Returns:
            ifind Response: object encapulsating a search request's results.

        Raises:
            EngineException

        Usage:
            Private method.

        Notes:
            https://www.neutrinoapi.com/api/geocode-address/ for full API documentation.

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
        Creates and returns Neutrinogeoaddress API query string with encoded query parameters.

        Args:
            query (ifind Query): object encapsulating details of a search query.

        Query Kwargs:
            address: (str) The address string. If this is not found terms will be used instead.

        Returns:
            str: query string for Neutrinogeoaddress API request

        Raises:
            EngineException

        Usage:
            Private method.

        """

        address = query.__dict__.get('address', query.terms)

        # Throw an exception if we have no search terms.
        if not address:
            raise QueryParamException(self.name, "No address provided!")

        query_append = "?address={}&country-code={}&language-code={}&user-id={}&api-key={}".format\
            (address, self.country_code, self.language_code, self.username, self.api_key)

        return API_ENDPOINT + encode_symbols(query_append)


    def _build_iframe_url(self, address, trans_table):
        """
        Builds the url to be used in an iframe for an embedded Google map of the address

        Args:
            address (str): The address to be used in the search on Google maps
            trans_table (str): A translation string to be used with the string.translate method. Can be generated using
                the maketrans function.

        Returns:
            iframe_url (str): The string to be used in the iframe to embed the map.
        """

        google_endpoint = 'https://www.google.com/maps/embed/v1/search'
        iframe_url = '{}?q={}&key={}'.format(google_endpoint,
                                             encode_symbols(address.encode('utf-8').translate(trans_table)),
                                             encode_symbols(self.google_api_key))
        return iframe_url

    @staticmethod
    def _build_summary(address, city, country, postcode, latitude, longitude):
        """
        Uses the information in the response to build a summary string

        Args:
            address (str): The complete address
            city (str): The city name portion of the address
            country (str): The country portion of the address
            postcode (str): The postcode portion of the address
            latitude (str): The latitude portion of the coordinates
            longitude (str): The longitude portion of the coordinates

        Returns:
            summary (str): A string representing the result

        Usage:
            Private method.
        """
        if address:
            address = 'Adddress: ' + address.encode('utf-8')
        if city:
            city = 'City: ' + city.encode('utf-8')
        if country:
            country = 'Country: ' + city.encode('utf-8')
        if postcode:
            postcode = 'Postcode: ' + postcode.encode('utf-8')
        if latitude and longitude:
            coords = 'Coordinates: ' + str((latitude, longitude))
        else:
            coords = ''

        summary = '{} {} {} {}'.format(address, city, country, postcode, coords)

        return summary

    def _parse_json_response(self, query, results):
        """
        Parses Neutrinogeoaddress's JSON response and returns as an ifind Response.

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

        # Results aren't paginated, no more to get.
        response.no_more_results = True

        url_base = 'https://www.google.co.uk/maps/place/'
        trans_table = maketrans(u' ', u'+')  # Switch spaces with + for the google maps url

        locations = content.get(u'locations')
        if locations:
        # There are results present, iterate over them.
            for loc in locations:
                # Kwargs below
                address = loc.get(u'address', '')
                latitude = loc.get(u'latitude', '')
                longitude = loc.get(u'longitude', '')
                country = loc.get(u'country', '')
                country_code = loc.get(u'country-code', '')
                city = loc.get(u'city', '')
                postcode = loc.get(u'postal-code', '')

                # The iframe_url must be placed in an iframe in order to render the map.
                if self.google_api_key:
                    iframe_url = self._build_iframe_url(address, trans_table)
                else:
                    iframe_url = None

                url = url_base + encode_symbols(address.encode('utf-8').translate(trans_table))
                text = Neutrinogeoaddress._build_summary(address, city, country, postcode, latitude, longitude)

                response.add_result(title=address, url=url, summary=text, imageurl=None,
                                    address=address, latitude=latitude, longitude=longitude, country=country,
                                    country_code=country_code, city=city, postcode=postcode, iframe_url=iframe_url)

        return response

