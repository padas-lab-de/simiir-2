__author__ = 'leif'
from ifind.search import EngineFactory
from example_utils import make_query, run_query, display_results

query_str = u'drivers license'


gov_engine = EngineFactory('govuk')

query = make_query(query_str)

response = run_query(gov_engine, query)

display_results(response)


