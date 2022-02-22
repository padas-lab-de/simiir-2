__author__ = 'leif'

from ifind.search import EngineFactory
from example_utils import make_query, run_query, display_results

query_str = u'retrievability'

api_key = None
cx = None

if api_key == None:
    print "A Google Api Key is required to run this example"
    print "Go to: https://www.google.com/cse/ to get a key."
    print "Then update the api_key and cx variable."
elif cx == None:
    print "A Google Api Key is required to run this example"
    print "Go to: https://www.google.com/cse/ to get a key."
    print "Then update the api_key and cx variable."
else:
    google_engine = EngineFactory('googlecse', api_key=api_key, cx=cx)

    query = make_query(query_str)

    response = run_query(google_engine, query)

    display_results(response)
