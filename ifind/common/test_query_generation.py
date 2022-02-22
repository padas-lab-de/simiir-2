__author__ = 'leif'

from query_generation import QueryGeneration, SingleQueryGeneration, BiTermQueryGeneration
import unittest
import logging
import sys


class TestQueryGeneration(unittest.TestCase):

    def setUp(self):
        self.logger = logging.getLogger("TestQueryGeneration")
        self.qg = QueryGeneration(minlen=4, stopwordfile='stopwords_test.txt')

    def test_extract_queries_from_text(self):
        self.logger.debug("Test Extract Queries")
        text = 'the good hello!'
        expected = ['good','hello']
        actual = self.qg.extract_queries_from_text(text)
        self.assertItemsEqual(expected, actual)

    def test_extract_queries_from_html(self):
        self.logger.debug("Test Extract Queries from HTML")
        html = '<HTML><b>Test</b> <h1>Extract</h2> Queries</HTML>'
        expected = ['test','extract', 'queries']
        actual = self.qg.extract_queries_from_html(html)
        self.assertItemsEqual(expected, actual)

    def test_clean_text(self):
        #todo should implement this as a loop with a dictionary of test
        #data and expected results
        self.logger.debug("Test Clean Text")
        #test one term with multiple punctuation
        test_text="?hello_"
        expected_result=["hello"]
        result = self.qg.clean_text(test_text)
        self.assertItemsEqual(expected_result,result)
        #test multiple terms with stop words in
        test_text="after again I am themselves true swashbuckling"
        expected_result=["true", "swashbuckling"]
        result = self.qg.clean_text(test_text)
        msg = "expected is " , expected_result , "result was " , result
        self.assertItemsEqual(expected_result,result, msg )
        #test line with numbers and non-alpha chars
        test_text="| hello 56"
        expected_result=["hello"]
        result = self.qg.clean_text(test_text)
        msg = "expected is " , expected_result , "result was ", result
        self.assertItemsEqual(expected_result,result, msg)
        #test line with single characters in
        test_text="b c d e sunshine"
        expected_result=["sunshine"]
        result = self.qg.clean_text(test_text)
        self.assertItemsEqual(expected_result,result)


class TestSingleQueryGeneration(unittest.TestCase):

    def setUp(self):
        self.logger = logging.getLogger("TestQueryGeneration")
        self.qg = SingleQueryGeneration(minlen = 4)

    def test_extract_queries_from_html(self):
        self.logger.debug("Extraction of Single (non) duplicate queries")
        html = '<HTML><b>Test</b> <h1>Extract</h2> Queries <b>Test</b> <h1>Extract</h2></HTML>'
        expected = ['test','extract', 'queries']
        actual = self.qg.extract_queries_from_html(html)
        self.assertItemsEqual(expected, actual)

        counts = {'test':2, 'extract': 2, 'queries':1}
        self.assertItemsEqual(self.qg.query_count, counts)


class TestBiTermQueryGeneration(unittest.TestCase):

    def setUp(self):
        self.logger = logging.getLogger("TestQueryGeneration")
        self.qg = BiTermQueryGeneration(minlen = 4)

    def test_extract_queries_from_html(self):
        self.logger.debug("Extraction of BiTerm (non) duplicate queries")
        html = '<HTML><b>Test</b> <h1>Extract</h2> Queries <b>Test</b> <h1>Extract</h2></HTML>'
        expected = ['extract test','extract queries', 'queries test']
        actual = self.qg.extract_queries_from_html(html)
        self.assertItemsEqual(expected, actual)

        counts = {'extract test':2, 'extract queries': 1, 'queries test':1}
        self.assertItemsEqual(self.qg.query_count, counts)


if __name__ == '__main__':
    logging.basicConfig(stream=sys.stderr)
    logging.getLogger("TestQueryGeneration").setLevel(logging.DEBUG)
    unittest.main(exit=False)