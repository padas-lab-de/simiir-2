import json
import jsonpickle
import ifind.common.make_json_serializable


class Response(object):
    """
    Models a Response object for use with ifind's search interface.

    Response Attributes:
        query_terms:  string representation of original query terms
        query:        ifind.Query object related ot the resuts, optional.
        results:      list representation of retrieved results (each result being a dict)
                      i.e {'title': Crow Rearing, 'url': http://etc.com, 'summary': How to rear crows?}
        result_total: integer representation of total results retrieved
    """

    def __init__(self, query_terms, query=None):
        """
        Response constructor.

        Args:
            query_terms (str): original query terms

        Attributes:
            results (list): list of retrieved results (each result being a Result object)
            result_total (int): total results retrieved

        Usage:
            response = Response(query.terms)

        """
        self.query_terms = query_terms
        self.query = query
        self.results = []
        self.result_total = 0
        self.total_pages = 0
        self.results_on_page = 0
        self.actual_page = 0
        # Flag to determine whether the engine has any more results for this query.
        self.no_more_results = False
        # The url to request the next page from
        self.next_page = None

    def add_result_object(self, result_object):
        """
        Adds a Result object to the Response's results list.
        """
        self.results.append(result_object)
        self.result_total += 1

    def add_result(self, title="", url="", summary="", imageurl='', rank=-1, **kwargs):
        """
        Adds a result to Response's results list.

        Kwargs:
            title (str): title of search result
            url (str): url of search result
            summary (str): summary of search result
            imageurl (str): the url of an image from the search result
            rank (int): the rank of the result
            **kwargs: further optional result attributes

        Usage:
            response.add_result(title="don's shop", url="www.dons.com",\
            summary="a very nice place", imageurl="http://stuff.com/img" rank=2)

        """
        self.results.append(Result(title, url, summary, imageurl , rank, **kwargs))
        self.result_total += 1

    def to_json(self):
        """
        Serialises Response and returns it as JSON.

        Returns:
            str: json string of Response

        Usage:
            response = engine.search(query)
            json_response = response.to_json()

        """
        response_dict = json.loads(jsonpickle.encode(self.__dict__))

        for result in response_dict[u'results']:
            del result[u'py/object']

        return json.dumps(response_dict)

    def __str__(self):
        """
        Returns human-readable string representation of response object.

        Returns:
            str: formatted new-lined list of results with info above

        Usage:
            print response

        """
        half_string = 'Result_total: {0}\nQuery_terms: {1}\nResults:\n\n'.format(self.result_total, self.query_terms)
        end_string = '\n\n'.join(['{0}'.format(result) for result in self.results])

        return half_string + end_string

    def __iter__(self):
        """
        Implements iterator for Response, returning a single result at a time.
        Uses generator function to lazy load results.

        Usage:
            for result in response:
                print result

        """
        for result in self.results:
            yield result

    def __len__(self):
        """
        Implements len() builtin for Response.

        Returns:
            int: number of results within response

        Usage:
            print len(response) --> 15

        """
        return self.result_total

    def __iadd__(self, other):
        """
        Overrides '+=' operator, adds other.results to self.results.

        Usage:
            print len(response1) --> 10
            print len(response2) --> 15
            response1 += response2
            print len(response1) --> 25

        """
        self.results += other.results
        self.result_total += other.result_total

        return self

    def __eq__(self, other):
        """
        Overrides '==' operator, returns True if both objects are responses which hash to the same value,
        otherwise returns False.

        Usage:
            response = Response("hello world")
            response2 = Response("hello world")
            print response == response2 --> False
            print response == None --> False

        """
        if type(other) == Response:
            return tuple(self.__dict__.items()) == tuple(other.__dict__.items())
        else:
            return False


class Result(object):
    """
    Models a Result object for use with ifind's Response class.

    """
    def __init__(self, title='', url='', summary='', imageurl='', rank=0, **kwargs):
        """
        Result constructor.

        Kwargs:
            title (str): title of search result
            url (str): url of search result
            summary (str): summary of search result
            imageurl (str): the url of an image from the search result
            rank (int): the rank of the search result
            **kwargs: further optional result attributes

        Usage:
            result = Result(title="pam's shop", url="www.pam.com", summary="a nice place")

        """
        self.title = title
        self.url = url
        self.summary = summary
        self.rank = rank
        self.imageurl = imageurl

        for key, value in kwargs.items():
            setattr(self, key, value)

        for key, value in self.__dict__.items():
            self.__dict__[key] = value

            if isinstance(value, str):
                self.__dict__[key] = value.encode('utf-8').rstrip()

    def __str__(self):
        """
        Returns human-readable string representation of result object.

        Returns:
            str: formatted new-lined list of result attributes

        Usage:
            print result

        """
        result = "\n"
        for key, value in self.__dict__.items():
            if isinstance(value, str):
                value = value.encode('ascii','ignore')

            result = result + "{0}: {1}\n".format(key, value)
        return result

    def __eq__(self, other):
        """
        Overrides '==' operator, returns True if both responses hash to the same value.

        Usage:
            response = Response("hello world")
            response2 = Response("hello world")
            print response == response2 --> False

        """
        return tuple(self.__dict__.items()) == tuple(other.__dict__.items())

    def to_json(self):
        """
        Returns object instance as a JSON string.
        """
        return vars(self)