#!/usr/bin/python
# -*- coding: latin-1 -*-
__author__ = 'rose'
from pipeline import PunctuationTermProcessor, AlphaTermProcessor, StopwordTermProcessor
from pipeline import LengthTermProcessor, TermPipeline, TermProcessor, SpecialCharProcessor
import unittest
import logging
import sys

class TestTermPipeline(unittest.TestCase):

    def setUp(self):
        self.logger = logging.getLogger("TestTermPipeline")

        self.ltp = LengthTermProcessor()
        self.tp = TermProcessor()
        self.stp = StopwordTermProcessor(stopwordfile='stopwords_test.txt')
        self.ptp = PunctuationTermProcessor()
        self.atp = AlphaTermProcessor()
        self.sctp = SpecialCharProcessor()



        self.pipeline = TermPipeline()
        self.pipeline.add_processor(self.sctp)
        self.pipeline.add_processor(self.tp)
        self.pipeline.add_processor(self.ltp)
        self.pipeline.add_processor(self.ptp)
        self.pipeline.add_processor(self.stp)
        self.pipeline.add_processor(self.atp)

    def test_read_stopfile(self):
        expected = ['accessibility', 'information', 'site', 'skip',
                    'main', 'content', 'a', 'about', 'above', 'after',
                    'again', 'against', 'all', 'am', 'an', 'and', 'any',
                    'are', "arent", 'as', 'at', 'be', 'because', 'been',
                    'before', 'being', 'below', 'between', 'both', 'but',
                    'by', "cant", 'cannot', 'could', "couldnt", 'did',
                    "didnt", 'do', 'does', "doesnt", 'doing', "dont",
                    'down', 'during', 'each', 'few', 'for', 'from',
                    'further', 'had', "hadnt", 'has', "hasnt", 'have',
                    "havent", 'having', 'he', "hed", "hell", "hes",
                    'her', 'here', "heres", 'hers', 'herself', 'him',
                    'himself', 'his', 'how', "hows", 'i', "id", "ill",
                    "im", "ive", 'if', 'in', 'into', 'is', "isnt",
                    'it', "its", 'its', 'itself', "lets", 'me', 'more',
                    'most', "mustnt", 'my', 'myself', 'no', 'nor', 'not',
                    'of', 'off', 'on', 'once', 'only', 'or', 'other',
                    'ought', 'our', 'ours', 'ourselves', 'out', 'over',
                    'own', 'same', "shant", 'she', "shed", "shell",
                    "shes", 'should', "shouldnt", 'so', 'some', 'such',
                    'than', 'that', "thats", 'the', 'their', 'theirs',
                    'them', 'themselves', 'then', 'there', "theres",
                    'these', 'they', "theyd", "theyll", "theyre",
                    "theyve", 'this', 'those', 'through', 'to', 'too',
                    'under', 'until', 'up', 'us', 'very', 'was', "wasnt",
                    'we', "wed", "well", "were", "weve", 'were',
                    "werent", 'what', "whats", 'when', "whens", 'where',
                    "wheres", 'which', 'while', 'who', "whos", 'whom',
                    'why', "whys", 'with', "wont", 'would', "wouldnt",
                    'you', "youd", "youll", "youre", "youve", 'your',
                    'yours', 'yourself', 'yourselves']
        self.assertEquals(expected, self.stp.stoplist)

    def test_process(self):
        #test removal of punctuation, numbers, special characters, can't from stopfile
        #other cases are tested in test_query_gen where the clean
        #method which uses the pipeline process method is tested
        terms = 'hello WORlD. my name  is Python111!!! ü can\'t'
        terms = terms.split()
        result = []
        for term in terms:
            clean = self.pipeline.process(term)
            if clean:
                result.append(clean)
        expected = ['hello', 'world', 'name', 'python']
        self.assertEquals(expected,result)
        #as above but tests cant is removed as well as can't
        # term = 'hello WORlD. my name  is Python111!!! ü cant'
        # expected = 'hello world my name is python '
        # result = self.pipeline.process(term)
        self.assertEquals(expected,result)

    def test_processors_config_order(self):
        #todo this is to see the impact of adding processors in
        #different orders
        pass
#
# class TestLengthTermProcessor(unittest.TestCase):
#
#     def setUp(self):
#         self.logger = logging.getLogger("TestLengthTermProcessor")
#         self.term = 'hi'
#         self.minlen=3
#         self.ltp= LengthTermProcessor()
#
#     def test_set_minlen(self):
#         #check -ve num returns current min len
#         min_len = self.ltp.min_len
#         self.ltp.set_min_length(-1)
#         result = self.ltp.min_len
#         self.assertEquals(result,min_len)
#         #check 0 returns current min_len
#
#         self.ltp.set_min_length(0)
#         result = self.ltp.min_len
#         self.assertEquals(result,min_len)
#
#         #now check >0
#         self.ltp.set_min_length(4)
#         result = self.ltp.min_len
#         self.assertEquals(result,4)
#
#     def test_check(self):
#         result = self.ltp.process('a')
#         self.assertEquals(result,None)
#
# class TestPunctTermProcessor(unittest.TestCase):
#
#     def setUp(self):
#         self.logger = logging.getLogger("TestPunctuationTermProcessor")
#         self.ptp = PunctuationTermProcessor()
#
#     def test_check(self):
#         #check removing ' ' ' the '
#         result = self.ptp.process(' the ')
#         self.assertEquals(result, 'the')
#         #check removing . at end 'hello.'
#
#         result = self.ptp.process('hello.')
#         self.assertEquals(result, 'hello')
#         #check removing ! and %
#         result = self.ptp.process('!good%')
#         self.assertEquals(result, 'good')
#
# class TestStopwordTermProcessor(unittest.TestCase):
#
#     def setUp(self):
#         self.logger = logging.getLogger("TestStopwordTermProcessor")
#         self.stp = StopwordTermProcessor(stopwordfile='stopwords_test.txt')
#
#     def test_check(self):
#         #test return None for term in list
#         in_list= 'myself'
#         result = self.stp.process(in_list)
#         self.assertEquals(result, None)
#
#         #test return None for term in list
#         in_list= 'against'
#         result = self.stp.process(in_list)
#         self.assertEquals(result, None)
#         #test return term for term not in list
#
#         non_list='sport'
#         result = self.stp.process(non_list)
#         self.assertEquals(result, non_list)
#
#
class TestAlphaTermProcessor(unittest.TestCase):

    def setUp(self):
        self.logger = logging.getLogger("TestAlphaTermProcessor")
        self.atp = AlphaTermProcessor()

    def test_check(self):

        result = self.atp.process('<h>')
        self.assertEquals(result, 'h')
        #check neg numbers

        result = self.atp.process('-5')
        self.assertEquals(result, '')

        #check pos numbers
        result = self.atp.process('5')
        self.assertEquals(result, '')
        #check punct
        result = self.atp.process('hello.')
        self.assertEquals(result, 'hello')
        term = "hello world my name is python111 cant"
        result = self.atp.process(term)
        self.assertEquals(result,'hello world my name is python cant')

# class TestSpecialCharTermProcessor(unittest.TestCase):
#
#     def setUp(self):
#         self.logger = logging.getLogger("TestSpecialCharTermProcessor")
#         self.sctm = SpecialCharProcessor()
#
#     def test_check(self):
#         #check inclusion of special character is removed
#         expected='hi'
#         result = self.sctm.process('±hi')
#         self.assertEquals(expected,result)
#         #check spaces aren't removed
#         expected='hi hello'
#         result = self.sctm.process(expected)
#         self.assertEquals(expected,result)
#         #check special char and spaces
#         testline = 'ähello my friend'
#         expected = 'hello my friend'
#         result = self.sctm.process(testline)
#         self.assertEquals(expected, result)





if __name__ == '__main__':
    logging.basicConfig(stream=sys.stderr)
    logging.getLogger("TestTermPipeline").setLevel(logging.DEBUG)
    unittest.main(exit=False)