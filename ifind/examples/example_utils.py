__author__ = 'leif'

from ifind.search import Query


def make_query(query_str, num_results=10):
    """
    :param query_str:
    :return: ifind.search.query
    """
    return Query(query_str,top=num_results)


def run_query(engine, query):
    """
    :param engine: ifind.search.engine
    :param query: ifind.search.query
    :return: ifind.search.response
    """
    return engine.search(query)

def display_results(response):
    """
    :param response: ifind.search.response
    :return:
    """
    for result in response:

        print '{0}: {1}'.format(result.rank,result.title)
        print result.url
        print result.summary
        print ''