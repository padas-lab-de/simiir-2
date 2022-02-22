import json
import requests
from ifind.search.engine import Engine
from ifind.search.response import Response
from ifind.search.exceptions import EngineAPIKeyException, QueryParamException, EngineConnectionException
from ifind.utils.encoding import encode_symbols
import time

API_ENDPOINT = "https://www.googleapis.com/plus/v1/"

RESULT_TYPES = ('people', 'activities', 'person_lookup')
DEFAULT_RESULT_TYPE = 'people'
MAX_PAGE_SIZE = {'people': 50, 'activities': 20, 'person_lookup': 1}


class Googleplus(Engine):
    """
    Googleplus search engine.

    """

    def __init__(self, api_key='', **kwargs):
        """
        Googleplus engine constructor.

        Kwargs:
            api_key (str): string representation of api key needed to access bing search api
            default_result_type (str): Optionally provide a default result type.
            See Engine.

        Raises:
            EngineException

        Usage:
            engine = EngineFactory('Googleplus api_key='etc123456etc123456etc123456')

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
            top (int): number of tweets to return up to MAX_PAGE_SIZE
            page_token (str): a page token to obtain a specific page in paginated results
        Returns:
            ifind Response: object encapulsating a search request's results.

        Raises:
            EngineException

        Usage:
            Private method.

        Notes:
            https://developers.google.com/ for full API documentation.

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
        Creates and returns Googleplus API query string with encoded query parameters.

        Args:
            query (ifind Query): object encapsulating details of a search query.

        Returns:
            str: query string for Googleplus API request

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

        # Set the number of results to get back, max value specified at the top of this file
        if query.top and query.top <= MAX_PAGE_SIZE[result_type]:
            top = query.top
        else:
            top = MAX_PAGE_SIZE[result_type]

        # Dictionary of search paramaters
        search_params = {'result_type': result_type,
                         'q': query.terms,
                         'top': top,
                         'page_token': query.__dict__.get('page_token', '')
                         }

        # Craft the string to append to the endpoint url
        if result_type in ['people', 'activities']:
            query_append = "{}?query='{}'&maxResults={}&key={}&pageToken={}".format\
                (search_params['result_type'], search_params['q'],
                 search_params['top'], self.api_key, search_params['page_token'])

        elif result_type == 'person_lookup':
            query_append = "people/{}?key={}&pageToken={}".format\
                (search_params['q'], self.api_key, search_params['page_token'])

        return API_ENDPOINT + encode_symbols(query_append)

    @staticmethod
    def _resize_image(imageurl, newsize=125):
        """
        Modifiies the image size parameter in the image URL, returns the modified string.

        Args:
            imageurl (str): The Googleplus image url
            newsize (int):  The new size of the image, the API returns ?sz=50

        Returns:
            str/None: An updated URL or None if input was incorrect
        """

        if imageurl:
            return imageurl.split('?sz=')[0] + '?sz=' + str(newsize)
        else:
            return None

    @staticmethod
    def _build_activity_summary(activity):
        """
        Builds the summary portion of the activity search. Strips out the various JSON elements and returns an appropriate
        summary string.

        Args:
            activity (dict): An activity dictionary from the Googleplus JSON response

        Returns:
            str: Summary string
        """

        object = "\n" + activity[u'object'][u'objectType'] + "\n" + activity[u'object'][u'content']
        attachment =''

        try:
            activity[u'object'][u'attachments']
            attachment = "\nAttachment: "
        except KeyError:
            pass

        if attachment:
            attachment += activity[u'object'].get(u'attachments', [{}])[0].get(u'objectType', '')
            try:
                attachment += activity[u'object'][u'attachments'][0][u'displayName']
            except KeyError:
                pass
            attachment += "\n" + activity[u'object'][u'attachments'][0].get(u'url', '')

        actorname = activity[u'actor'][u'displayName']
        published = activity[u'published']
        summary = u"User: {}\nPublished: {}{}{}".format(actorname, published, object, attachment)
        return summary

    @staticmethod
    def _build_person_summary(person):
        """
        Builds the summary portion of a person lookup.

        Args:
            person (dict): A dictionary representing the

        Returns:
            str: Summary of the person response (occupation, places lived, about)
        """

        occupation = person.get(u'occupation', '')
        if occupation:
            occupation = 'Occupation: ' + occupation.encode('utf-8')

        about_me = person.get(u'aboutMe', '')
        if about_me:
            about_me = 'About Me : ' + about_me.encode('utf-8')

        pl = person.get(u'placesLived', '')
        places_lived = []
        if pl:
            for location in pl:
                places_lived.append(location.get(u'value').encode('utf-8'))
            places_lived = str(places_lived).translate(None, '[]')
        if places_lived:
            places_lived = 'Places Lived: ' + places_lived.encode('utf-8')

        summary = "{}{}{}".format(occupation, places_lived, about_me)

        return summary



    def _parse_json_response(self, query, results):
        """
        Parses Googleplus's JSON response and returns as an ifind Response.

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

        if result_type == 'people':
            # Build the ifind response for a people search

            for user in content[u'items']:
                name = user[u'displayName']
                url = user[u'url']
                imageurl = Googleplus._resize_image(user[u'image'][u'url'])
                summary = ''

                # Kwargs
                id = user[u'id']

                # Add the result to the response
                response.add_result(title=name, url=url, summary=summary, imageurl=imageurl, id=id)

        elif result_type == 'activities':
            # Build the ifind response for an activity search
            for activity in content[u'items']:

                # The three dictionaries below are passed as keyword arguments to the result object
                activity_dict = {
                    'url': activity.get(u'url'),
                    'verb': activity.get(u'verb'),
                    'title': activity.get(u'title'),
                    'published': activity.get(u'published'),
                    'updated': activity.get(u'updated'),
                    'kind': activity.get(u'kind'),
                    'id': activity.get(u'id')
                }

                actor_dict = {
                    'display_name': activity.get(u'actor').get(u'displayName'),
                    'url': activity.get(u'actor').get(u'url'),
                    'image': activity.get(u'actor').get(u'image').get(u'url'),
                    'id': activity.get(u'actor').get(u'id')
                    }

                object_dict = {
                    'type': activity.get(u'object').get(u'objectType'),
                    'content': activity.get(u'object').get(u'content').encode('utf-8'),
                    'url': activity.get(u'object').get(u'url'),
                    }

                title = u"{}  ({})".format(activity_dict.get('title'),
                                          activity_dict.get('verb'))
                url = activity_dict.get('url')
                summary = Googleplus._build_activity_summary(activity)
                imageurl = Googleplus._resize_image(actor_dict.get('image'))

                # Attachments is a list of dictionaries with keys:
                # u'objectType', u'displayName', u'content', u'url' and potentially nested dictionaries,
                # such as u'embed', u'image', u'thumbnails (list of dicts).
                attachments = activity.get(u'object').get(u'attachments')

                # Add the result to the response.
                response.add_result(title=title, url=url, summary=summary, imageurl=imageurl,
                                    actor=actor_dict, object=object_dict, activity=activity_dict,
                                    attachments=attachments)

        elif result_type == 'person_lookup':
            # Build the ifind response for a person lookup. No loop as the content is for a single person.

            title = content[u'displayName']
            url = content[u'url']
            imageurl = content[u'image'][u'url']
            summary = Googleplus._build_person_summary(content)

            about_me = content.get(u'aboutMe')
            occupation = content.get(u'occupation')
            verified = content.get(u'verified')
            circled_count = content.get(u'circledByCount')
            is_plus_user = content.get(u'isPlusUser')
            birthday = content.get(u'birthday')
            bragging_rights = content.get(u'braggingRights')
            emails = content.get(u'emails')
            skills = content.get(u'skills')
            relationship_status = content.get(u'relationshipStatus')
            places_lived = content.get(u'placesLived')
            organizations = content.get(u'organizations')
            tagline = content.get(u'tagline')

            # Kwargs below
            person = {'about_me': about_me, 'occupation':occupation, 'verified': verified, 'emails': emails,
                      'circled_count': circled_count, 'is_plus_user': is_plus_user, 'birthday': birthday,
                      'bragging_rights': bragging_rights, 'skills': skills, 'relationship_status': relationship_status,
                      'places_lived': places_lived, 'organizations': organizations, 'tagline': tagline
                    }

            # Add the result to the response.
            response.add_result(title=title, url=url, summary=summary, imageurl=imageurl, person=person)

        return response