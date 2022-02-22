
from ifind.search.response import Response
from ifind.search.engine import Engine
from ifind.search import Query, EngineFactory
from ifind.search.exceptions import EngineAPIKeyException, QueryParamException, EngineConnectionException
from copy import copy


SM_LIST = ['facebook.com', 'twitter.com', 'plus.google.com', 'uk.linkedin.com', 'bebo.com', 'pinterest.com']


class Socialaccounts(Engine):
    """
    Meta Engine to obtain social media specific results from Bing


    """

    def __init__(self, api_key='',  **kwargs):
        """
        Constructor for the SocialAccounts meta engine

        Kwargs:
            api_key (str): string representation of api key needed to access bing search api. A valid Bing API key
                is required as this engine leverages Bing.
            See Engine.

        Raises:
            EngineException

        Usage:
            engine = EngineFactory('socialaccounts', api_key='etc123456etc123456etc123456')

        """

        if not api_key:
            raise EngineAPIKeyException(self.name, """Bing API Key Required (Searches for the various social media
            accounts are done via Bing).""")

        Engine.__init__(self, **kwargs)
        self.api_key = api_key

    def _search(self, query):
        """
        Concrete search method, iterates through the specified Social Media domain list and performs an advanced
        Bing query formulation search for each.

        Args:
            query (ifind Query): The ifind query object representing the original query object. This will get copied and
                modified for each Social Media domain. Kwargs in the original Query object will carry over to the individual
                Bing searches.

        Query Kwargs:
            site_list (list): A list of sites (social media domain names, preferably) to include in the site: field.
            username (bool): Specify if the search is attempting to list users or not. If true, the intitle: field
                operator is used to wrap the query terms, though no phrase quotation marks are added.

        Raises:
            See Bing

        :return:
        """
        responses = []
        # Get the list of Social Media domains to form the site: field for each query. If none are specified, use the
        # hardcoded default in SM_LIST
        sites = query.__dict__.get('site_list', SM_LIST)

        if not query.__dict__.get('username'):
            # It's a general site search, don't supply the intitle field.
            q_base = u"site:{} {}"
        else:
            # Attempt to get user pages by including the intitle field operator.
            q_base = u"site:{} intitle:{}"

        # Create the bing Engine object for the searches.
        e = EngineFactory('bing', api_key=self.api_key)

        # Submit a Bing query for each Social Media domain.
        for site in sites:
            # Create the query string.
            terms = q_base.format(site, query.terms)
            # Copy the Query object so the original is not mutated.
            new_query = copy(query)
            # Set the terms for the copy of the query
            new_query.terms = terms

            # Add the results for this domain to the response list
            responses.append(e.search(new_query))

        # Unify all Bing responses in to a single ifind Response object. Return it as the result of the meta search.
        concat_response = Response(query.terms, query)
        for response in responses:
            for result in response:
                concat_response.add_result_object(result)

        return concat_response