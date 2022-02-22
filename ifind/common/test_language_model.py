__author__ = 'rose'
from language_model import LanguageModel
import unittest
import logging
import sys

class TestLanguageModel(unittest.TestCase):

    def setUp(self):
        self.expected = {'hello': 10, 'world': 20, 'goodbye': 10}
        self.logger = logging.getLogger("TestLanguageModel")
        self.bk_model = LanguageModel(file='term_occurrences.txt')
        self.doc_model = LanguageModel(term_dict=self.expected)

    def test_populate_occurrences(self):
        self.logger.debug("Test Populate Occurrences")
        self.bk_model._populate_occurrences('term_occurrences.txt')
        #check it's not null and contains the following
        #hello 10
        #world 20
        #goodbye 10
        self.assertDictEqual(self.bk_model.occurrence_dict,self.expected)

#don't think I need to test doc and bk separately, bk read into dict and
#this has been tested

    def test_get_number_occurrences_doc(self):
        self.logger.debug("Test Get Number of Occurrences with dictionary")
        hello_count=self.doc_model.get_num_occurrences('hello')
        hello_expected=10
        self.assertEquals(hello_count,hello_expected)

    def test_get_number_occurrences_bk(self):
        self.logger.debug("Test Get Number of Occurrences with file")
        #same test as _doc but with bk model
        hello_count=self.bk_model.get_num_occurrences('hello')
        hello_expected=10
        self.assertEquals(hello_count,hello_expected)

    def test_when_no_occurrences_bk(self):
        self.logger.debug("Test when term does not exist")
        #same test as _doc but with bk model
        term_count=self.bk_model.get_num_occurrences('garble')
        term_expected=0
        self.assertEquals(term_count, term_expected)

    def test_calc_total_occurrences_doc(self):
        self.logger.debug("Test calculate total occurrences with dictionary")
        actual_total=self.doc_model.get_total_occurrences()
        expected_total=40
        self.assertEquals(expected_total,actual_total)

    def test_calc_total_occurrences_bk(self):
        self.logger.debug("Test calculate total occurrences with file")
        actual_total=self.bk_model.get_total_occurrences()
        expected_total=40
        self.assertEquals(expected_total,actual_total)

    def test_get_term_probability(self):
        self.logger.debug("Test get term probability")
        #probability of hello is 10/40 = 0.25
        expected=0.25
        actual=self.bk_model.get_term_prob('hello')
        self.assertEquals(expected,actual)

if __name__ == '__main__':
    logging.basicConfig(stream=sys.stderr)
    logging.getLogger("TestLanguageModel").setLevel(logging.DEBUG)
    unittest.main(exit=False)
