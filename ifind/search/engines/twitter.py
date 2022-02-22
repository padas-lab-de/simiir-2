import json
import requests
import oauth2 as oauth
from ifind.search.engine import Engine
from ifind.search.response import Response
from ifind.search.exceptions import EngineAPIKeyException, QueryParamException, EngineConnectionException

API_ENDPOINT = 'https://api.twitter.com/1.1/search/tweets.json'

CONSUMER_KEY = '1S2HEggPpCnDMmHQMMTt1g'
CONSUMER_SECRET = '3ui76cSSGWB6mUsrB7dL4Pg0fhUqlfNUKfRxZSTrak'

ACCESS_TOKEN_KEY = '330254387-hPlGvv0aCrBwDl2GRyIusgEzWVKryIJwjJU86PLV'
ACCESS_TOKEN_SECRET = '9Zgn25M3QohKCeu65mVtkG1bMun62U2ae5wCv6kys'

OAUTH_TOKEN = oauth.Token(key=ACCESS_TOKEN_KEY, secret=ACCESS_TOKEN_SECRET)    # TODO get api.keys sorted
OAUTH_CONSUMER = oauth.Consumer(key=CONSUMER_KEY, secret=CONSUMER_SECRET)   # TODO get api.keys sorted

SIGNATURE_METHOD_HMAC_SHA1 = oauth.SignatureMethod_HMAC_SHA1()

RESULT_TYPES = ('mixed', 'recent', 'popular')

DEFAULT_RESULT_TYPE = 'mixed'

MAX_PAGE_SIZE = 100


class Twitter(Engine):
    """
    Twitter search engine.

    """

    def __init__(self, **kwargs):
        """
        Twitter engine constructor.

        Kwargs:
            default_result_type (str): Optionally provide a default result type.
            See Engine.

        Raises:
            EngineException

        Usage:
            engine = EngineFactory('twitter')

        """
        Engine.__init__(self, **kwargs)

        if not CONSUMER_KEY or not CONSUMER_SECRET or not ACCESS_TOKEN_KEY or not ACCESS_TOKEN_SECRET:
            raise EngineAPIKeyException(self.name, 'OAuth details not supplied')

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
            top (int): number of tweets to return up to MAX_PAGE_SIZE
            result_type (str): 'mixed' - popular and recent results
                               'recent' - most recent results
                               'popular' - most popular results
            lang (str): restricts tweets to given language by ISO 639-1 code, i.e. 'eu'

        Returns:
            ifind Response: object encapulsating a search request's results.

        Raises:
            EngineException

        Usage:
            Private method.

        Notes:
            https://dev.twitter.com/docs/api/1.1/get/search/tweets for full API documentation.

        """
        if not query.top:
            raise QueryParamException(self.name, "Total result amount (query.top) not specified")

        if query.top > MAX_PAGE_SIZE:
            raise QueryParamException(self.name, 'Requested result amount (query.top) '
                                                 'exceeds max of {0}'.format(MAX_PAGE_SIZE))
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
            raise EngineConnectionException(self.name, "Unable to send request, check connectivity")

        if response.status_code != 200:
            raise EngineConnectionException(self.name, "", code=response.status_code)

        return self._parse_json_response(query, response)

    def _create_query_string(self, query, search_params=''):
        """
        Creates and returns Twitter API query string with encoded query parameters.

        Args:
            query (ifind Query): object encapsulating details of a search query.

        Returns:
            str: query string for Twitter API request

        Raises:
            EngineException

        Usage:
            Private method.

        """
        # Check to see if there is an existing dictionary of twitter search parameters. This will only happen when
        # creating the string for the next page
        if not search_params:
            # Check for a result type, if none found, set it to default.
            result_type = query.result_type
            if not result_type:
                result_type = self.default_result_type

            # Check to if the result type is valid
            if result_type not in RESULT_TYPES:
                raise QueryParamException(self.name, "Engine doesn't support query result type '{0}'"
                                                     .format(query.result_type))
            search_params = {'count': query.top,
                             'result_type': result_type,
                             'lang': query.lang,
                             'q': query.terms}

        request = oauth.Request.from_consumer_and_token(OAUTH_CONSUMER,
                                                        token=OAUTH_TOKEN,
                                                        http_method='GET',
                                                        http_url=API_ENDPOINT,
                                                        parameters=search_params)

        request.sign_request(SIGNATURE_METHOD_HMAC_SHA1, OAUTH_CONSUMER, OAUTH_TOKEN)

        return request.to_url()

    def _parse_json_response(self, query, results):
        """
        Parses Twitter's JSON response and returns as an ifind Response.

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

        # Check to see if there are more results.
        next_results = content[u'search_metadata'].get(u'next_results', '')
        if next_results:
            # Create a dictionary from the string found in u'next_results'
            params = next_results[1:]
            params = params.split('&')
            for index in range(len(params)):
                params[index] = params[index].split('=')
            param_dic = {}
            # At this point params looks like: [['someparam', 'somevalue'], ['someparam', 'somevalue']....]
            for lis in params:
                param_dic[lis[0]] = lis[1]

            # Set the next page URL in the response.
            response.next_page = self._create_query_string(query, search_params=param_dic)
        else:
            # No more results, set the flag in the response
            response.no_more_results = True

        for result in content[u'statuses']:

            text = result[u'text']
            result_id = str(result[u'id'])

            # User dictionary
            user = {'user_id': result[u'user'][u'id_str'],
                    'profile_image': result.get(u'user').get(u'profile_image_url'),
                    'geo_enabled': result.get(u'user').get(u'geo_enabled'),
                    'description': result.get(u'user').get(u'description'),
                    'follower_count': result.get(u'user').get(u'followers_count'),
                    'protected': result.get(u'user').get(u'protected'),
                    'location': result.get(u'user').get(u'location'),
                    'utc_offset': result.get(u'user').get(u'utc_offset'),
                    'time_zone': result.get(u'user').get(u'time_zone'),
                    'name': result.get(u'user').get(u'name'),
                    'screen_name': result.get(u'user').get(u'screen_name'),
                    'member_since': result.get(u'user').get(u'created_at')
            }

            # TODO clean this up
            stamp = result[u'created_at'].split()
            # Created at in format: '01 Jan, 2014 @ 20:23'
            created_at = "{} {}, {} @ {}".format(stamp[2], stamp[1], stamp[5], stamp[3][:-3])

            url = 'https://www.twitter.com/{0}/status/{1}'.format(user['user_id'], result_id)
            imageurl = user.get('profile_image')
            title = u"{} ({}) - {}".format(user['name'], user['screen_name'], created_at)

            # Kwargs below
            source = result.get(u'source')
            coordinates = result.get(u'coordinates')
            place = result.get(u'place')
            hashtags= result.get(u'entities').get(u'hashtags')
            user_info = user
            reply_to_screen_name = result.get(u'in_reply_to_screen_name')
            reply_to_userid = result.get(u'in_reply_to_user_id_str')
            reply_to_status = result.get(u'in_reply_to_status_id_str')
            tweet_id = result_id


            # List of links in the tweet. Each item in the list is a dictionary with keys:
            # u'url, u'indices', u'expanded_url, u'display_url'
            links = result.get(u'entities').get(u'urls')

            # List of media items in the tweet. Each item in the list is a dictionary with keys:
            # u'expanded_url', u'sizes', u'url', u'media_url_https',
            # u'id_str', u'indices', u'media_url', u'type', u'id', u'display_url'
            media = result.get(u'entities').get(u'media')

            # List of users mentioned in the tweet. Each item in the list is a dictionary with keys:
            # u'indices', 'u'screen_name', u'PSG_inside', u'id', u'name', u'id_str'
            user_mentions = result.get(u'entities').get(u'user_mentions')


            response.add_result(title=title, url=url, summary=text, imageurl=imageurl, stamp=stamp,
                                user_info=user_info, media=media, links=links, user_mentions=user_mentions,
                                source=source, coordinates=coordinates, place=place,
                                hashtags=hashtags,  reply_to_screen_name=reply_to_screen_name,
                                reply_to_status=reply_to_status, reply_to_userid=reply_to_userid, tweet_id=tweet_id)

            if len(response) == query.top:
                break

        return response