__author__ = 'rose'

from query_ranker import QueryRanker
import unittest
import logging
import sys

class TestQueryRanker(unittest.TestCase):

    def setUp(self):
        self.logger = logging.getLogger("TestQueryRanker")
        self.doc_dict={'hello':2,'world':4}
        self.ranker = QueryRanker(background_file='term_occurrences.txt', doc_term_count=self.doc_dict)

    def test_calculate_query_probability(self):
        self.logger.debug("Test Calculate Query Probability")
        query="hello world"
        #bk_prob_hello=0.25
        #bk_prob_world=0.5
        #doc_prob_hello=0.5
        #doc_prob_world=0.67
        #l pdoc - (1-l)pback
        #hello = 0.5*0.33333 + 0.5*0.25 = 0.29165
        #world = 0.5*0.6666 + 0.5*0.5 = 0.58333333
        #total = 0.8749
        expected = 0.8749
        result=self.ranker.calculate_query_probability(query=query,l=0.5)
        self.assertAlmostEqual(expected,result,2)



    def test_calculate_query_list_probabilities(self):
        self.logger.debug("Test Calculate Query List Probabilities")
        queries=['hello world', 'hello']
        expected={'hello':0.29,'hello world':0.8749}
        #probabilities are 0.8749 and 0.29
        result = self.ranker.calculate_query_list_probabilities(queries)
        if result:
            for term, prob in result.items():
                #self.logger.debug("term is "+ term)
                expected_prob= expected[term]
                self.assertAlmostEqual(prob,expected_prob,2)
        else:
            self.logger.debug("nothing returned")

    def test_get_top_queries(self):
        #first need to populate query list prob
        queries=['hello world', 'hello']
        result = self.ranker.calculate_query_list_probabilities(queries)
        self.logger.debug("Test Get Top Queries")
        result = self.ranker.get_top_queries(2)
        self.assertEquals(len(result),2)
        expected = ['hello world','hello']
        for i in range(len(expected)):
            self.assertEquals(result[i],expected[i])

        # self.assertAlmostEqual(result.items()[0],expected.values()[0])


if __name__ == '__main__':
    logging.basicConfig(stream=sys.stderr)
    logging.getLogger("TestQueryRanker").setLevel(logging.DEBUG)
    unittest.main(exit=False)

