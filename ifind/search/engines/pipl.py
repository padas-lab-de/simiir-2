import json
import requests
from ifind.search.engine import Engine
from ifind.search.response import Response
from ifind.utils.encoding import encode_symbols
from ifind.search.exceptions import QueryParamException, EngineAPIKeyException, EngineConnectionException


API_ENDPOINT = "https://api.pipl.com/search/v3/json/"

DEFAULT_COUNTRY = 'GB'


class Pipl(Engine):
    """
    Pipl search engine.

    """

    def __init__(self, api_key='', **kwargs):
        """
        Pipl engine constructor.

        Kwargs:
            See Engine.

        Raises:
            EngineException

        Usage:
            engine = EngineFactory('Pipl api_key='etc123456etc123456etc123456')

        """
        Engine.__init__(self, **kwargs)
        self.api_key = api_key

        if not self.api_key:
            raise EngineAPIKeyException(self.name, "'api_key=' keyword argument not specified")

    def _search(self, query):
        """
        Concrete method of Engine's interface method 'search'.
        Performs a search and retrieves the results as an ifind Response.



        Args:
            query (ifind Query): Object encapsulating details of a search query.

        Query Kwargs:
            ********
            Note: If *both* the first name and last name are absent, query.terms will be interpreted as raw_name
            ********

            first_name (str): The first name of the target. Minimum 2 characters.
            middle_name (str): The middle name or initial of the target
            last_name (str): The last name of the target. Minimum 2 characters.
            phone (str) The phone number of the target. Only supports US numbers at time of writing (06/10/14)
                    formats:    phone= '999888777'
                                phone= '(999) 888-777'
                                phone= '+1 999888777'
            username (str): A username or screen name associated with the target. Minimum 4 characters.
            email (str): An email address associated with the target.
            country (str): Two letter country code: e.g. GB, US.
            state (str): A US or Canada state code, e.g. CO
            city (str): A city name associated with the target.
            raw_name (str): An unparsed version of the name. Built from query terms if no first and last name provided.
            raw_address (str): An unparsed address.
            from_age (int): Lower limit on the age of the target.
            to_age(int) Upper limit on the age of the target.

        Returns:
            ifind Response: object encapulsating a search request's results.

        Raises:
            EngineException

        Usage:
            Private method.

        Notes:
            http://dev.pipl.com/docs/ for full API documentation.

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

        return Pipl._parse_json_response(query, response)

    def _create_query_string(self, query):
        """
        Creates and returns Pipl API query string with encoded query parameters.

        Args:
            query (ifind Query): object encapsulating details of a search query.

        Returns:
            str: query string for Pipl API request

        Raises:
            EngineException

        Usage:
            Private method.

        """

        query_append = self._build_query_append(query)
        return API_ENDPOINT + unicode(encode_symbols(query_append), encoding='utf-8')

    def _build_query_append(self, query):

        first_name = query.__dict__.get('first_name', '')
        middle_name = query.__dict__.get('middle_name', '')
        last_name = query.__dict__.get('last_name', '')
        phone = query.__dict__.get('phone', '')
        username = query.__dict__.get('username', '')
        email = query.__dict__.get('email', '')
        country = query.__dict__.get('country', DEFAULT_COUNTRY)
        state = query.__dict__.get('state', '')
        city = query.__dict__.get('city', ''),
        raw_name = query.__dict__.get('raw_name', '')
        raw_address = query.__dict__.get('raw_address', '')
        from_age = str(query.__dict__.get('from_age', ''))
        to_age = str(query.__dict__.get('to_age', ''))

        if not (first_name and last_name) and not raw_name:
            raw_name = query.terms

        if not (raw_name or (first_name and last_name) or phone or email or username):
            raise QueryParamException(self.name, "Require one of: raw_name,\
             (first_name + last_name), phone, email, username)")

        return "?first_name={}&middle_name={}&last_name={}".format(first_name, middle_name, last_name) +\
               "&phone={}&email={}".format(phone, email) +\
               "&country={}&state={}&city={}".format(country, state, city) +\
               "&raw_name={}&raw_address={}".format(raw_name, raw_address) +\
               "&from_age={}&to_Age={}".format(from_age, to_age) +\
               "&key={}".format(self.api_key)


        # JSON layout of the person object - can be used to expand functionality later.
        #
        # json.dumps({'names': [{'first': first_name, 'middle': middle_name, 'last': last_name }],
        #             'addresses': [{'country': country, 'state': state,
        #                            'city': city, 'street': street, 'house': house_number}],
        #             'phones': [],
        #             'emails': [],
        #             'usernames': [],
        #             'dobs': [],
        #             'jobs': [],
        #             'educations': [],
        #             'images': [],
        #             'related_urls': [],
        #             'relationships': []
        #             })

    @staticmethod
    def _build_summary(record):
            usernames = []
            try:
                for usr in record[u'usernames']:
                    usernames.append(usr[u'content'].encode('utf-8'))
                usernames = '\nUsernames: ' + str(usernames)
            except KeyError:
                usernames = ''

            addresses = []
            try:
                for add in record[u'addresses']:
                    addresses.append(add[u'display'].encode('utf-8'))
                addresses = '\nAddresses: ' + str(addresses)
            except KeyError:
                addresses = ''

            relationships = []
            try:
                for rel in record[u'relationships']:
                    relationships.append(rel[u'name'][u'display'].encode('utf-8'))
                relationships = u'\nRelationships: ' + str(relationships)
            except KeyError:
                relationships = ''

            jobs = []
            try:
                for job in record[u'jobs']:
                    jobs.append(job[u'display'].encode('utf-8'))
                jobs = '\nJobs: ' + str(jobs)
            except KeyError:
                jobs = ''

            educations = []
            try:
                for edu in record[u'educations']:
                    educations.append(edu[u'display'].encode('utf-8'))
                educations = '\nEducations: ' + str(educations)
            except KeyError:
                educations = ''
            tags = []
            try:
                for tag in record[u'tags']:
                    tags.append(tag[u'content'].encode('utf-8'))
                tags = '\ntags: ' + str(tags)
            except KeyError:
                tags = ''

            return '{}{}{}{}{}{}'.format(jobs, addresses, educations, relationships, usernames, tags).translate(None, '[]')


    @staticmethod
    def _parse_json_response(query, results):
        """
        Parses Pipl's JSON response and returns as an ifind Response.

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

        # Pipl only returns 20 results, so there are no more.
        response.no_more_results = True

        for record in content[u'records']:
            try:
                name = record[u'names'][0][u'display']
            except KeyError:
                name = record.get('source').get('url', "_no title_")
            url = record[u'source'][u'url']
            imageurl = None
            try:
                imageurl = record[u'images'][0][u'url']
            except:
                pass
            summary = Pipl._build_summary(record)

            # Kwargs below
            # Each keyword contains a list of (potentially empty) dictionary objects.
            usernames = record.get(u'usernames')
            addresses = record.get(u'addresses')
            relationships = record.get(u'relationships')
            jobs = record.get(u'jobs')
            educations = record.get(u'educations')
            tags = record.get(u'tags')


            response.add_result(title=name, url=url, summary=summary, imageurl=imageurl,
                                usernames=usernames, addresses=addresses, relationships=relationships,
                                jobs=jobs, educations=educations, tags=tags)

        return response