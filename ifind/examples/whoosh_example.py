__author__ = 'leif'
from ifind.search import EngineFactory
from example_utils import make_query, run_query, display_results
import os

query_str = u'french'



gov_engine = EngineFactory('whooshtrec', whoosh_index_dir=os.path.abspath('sample_data/index/'))

query = make_query(query_str)

response = run_query(gov_engine, query)

display_results(response)