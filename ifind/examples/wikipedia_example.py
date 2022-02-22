__author__ = 'leif'

from ifind.search import EngineFactory
from example_utils import make_query, run_query, display_results


query_str = u'retrievability'


wiki_engine = EngineFactory('wikipedia')

query = make_query(query_str)

response = run_query(wiki_engine, query)

display_results(response)