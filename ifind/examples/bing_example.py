__author__ = 'leif'

from ifind.search import EngineFactory
from example_utils import make_query, run_query, display_results

query_str = u'retrievability'

api_key = None


if api_key == None:
    print "A Bing Api Key is required to run this example"
    print "Go to: https://datamarket.azure.com/dataset/bing/search to get a key."
    print "Then update the api_key variable."
else:
    gov_engine = EngineFactory('bing', api_key=api_key)

    query = make_query(query_str)

    response = run_query(gov_engine, query)

    display_results(response)

