"""
An abstract class to generate queries list
=============================
Author: rose : <Rosanne.English@glasgow.ac.uk>
Date:   08/08/2013
Version: 0.1
"""

from collections import Counter
from re import sub
from nltk import clean_html, regexp_tokenize
from bs4 import BeautifulSoup

from ifind.common.pipeline import TermPipeline
from ifind.common.pipeline import TermProcessor,AlphaTermProcessor,StopwordTermProcessor,SpecialCharProcessor,\
    LengthTermProcessor,PunctuationTermProcessor

class QueryGeneration(object):
    """
    Abstract class to represent structure for a query generator
    """

    def __init__(self, stopwordfile = None, minlen = 3):
        """
        constructor for QueryGeneration
        """
        self.min_len = minlen
        self.stop_filename = stopwordfile

    def extract_queries_from_html(self, html):
        """
        :param url: the html from which the queries are to be constructed
        :return: list of queries
        """

        soup = BeautifulSoup(html,'html.parser')

        content = soup.get_text()
        #content = ' '.join(content.split())
        return self.extract_queries_from_text(content)

    def extract_queries_from_text(self, text):
        """
        :param text: the text from which the queries are to be constructed
        :return: list of queries
        """
        if text:
            query_list = self.clean_text(text)
            return query_list
        else:
            return []

    def clean_text(self, text):
        """ normalizes the text
        :param text: a string of text, to be cleaned.
        :return: a list of terms (i.e. tokenized)
        """
        if text:
            text = text.lower()
            text = text.replace('-', ' ')
            text = text.split()
            cleaned = []
            cleaner_pipeline = TermPipeline()
            cleaner_pipeline = self.construct_pipeline(cleaner_pipeline)

            for term in text:
                clean_result = cleaner_pipeline.process(term)
                if clean_result:
                    cleaned.append(clean_result)
            return cleaned
        else:
            return ''

    #todo do we want the user to determine what processors they want?
    def construct_pipeline(self, pipeline):
        #create all processors and add to pipeline
        ltp = LengthTermProcessor()
        ltp.set_min_length(self.min_len)
        stp = StopwordTermProcessor(stopwordfile=self.stop_filename)
        ptp = PunctuationTermProcessor()
        atp = AlphaTermProcessor()
        sctp = SpecialCharProcessor()

        pipeline.add_processor(ltp)
        pipeline.add_processor(sctp)
        pipeline.add_processor(ptp)
        pipeline.add_processor(stp)
        pipeline.add_processor(atp)

        return pipeline

    def get_doc_term_counts(self, query_list):
        """
        for use in query ranker, for each term calculate number of occurrences
        in the document,
        :return dict of term, occurrence pairs
        """
        count_dict = {}
        for term in query_list:
            if term in count_dict:
                count_dict[term]+=1
            else:
                count_dict[term]=1
        return count_dict


class SingleQueryGeneration(QueryGeneration):

    def extract_queries_from_text(self, text):
        """
        :param text: the text from which the queries are to be constructed
        :return: list of queries
        """

        term_list = self.clean_text(text)
        self.query_count = {}

        for query in term_list:
            if query in self.query_count:
                self.query_count[query] = self.query_count[query] + 1
            else:
                self.query_count[query] = 1
        query_list = []
        for key in self.query_count:
            query_list.append(key)

        return query_list


class BiTermQueryGeneration(QueryGeneration):

    def extract_queries_from_text(self, text):
        """
        :param text: the text from which the queries are to be constructed
        :return: list of queries
        """
        if text:
            term_list = self.clean_text(text)
            #query count holds the queries with their text as the key, count as value
            self.query_count = {}
            #take first term and pair with the rest of the terms in the text
            #then move to second and repeat
            prev_term = term_list[0]

            term_list= term_list[1:len(term_list)]

            for term in term_list:
                query = prev_term + ' ' + term
                qlist = [prev_term, term]


                sqlist = set(qlist)
                qlist = list(sqlist)
                qlist.sort()
                query = ' '.join(qlist)


                if query in self.query_count:
                    self.query_count[query] = self.query_count[query] + 1
                else:
                    self.query_count[query] = 1

                prev_term = term

            query_list = []
            for key in self.query_count:
                query_list.append(key)

            return query_list
        else:
            return []


class TriTermQueryGeneration(QueryGeneration):

    def extract_queries_from_text(self, text):
        """
        :param text: the text from which the queries are to be constructed
        :return: list of queries
        """
        term_list = self.clean_text(text)

        self.query_count = {}

        prev_prev_term = term_list[0]
        prev_term = term_list[1]

        term_list= term_list[2:len(term_list)]

        for term in term_list:
            qlist = [prev_prev_term, prev_term, term]


            sqlist = set(qlist)
            qlist = list(sqlist)
            qlist.sort()
            query = ' '.join(qlist)
            if query in self.query_count:
                self.query_count[query] = self.query_count[query] + 1
            else:
                self.query_count[query] = 1

            prev_prev_term = prev_term
            prev_term = term


        query_list = []
        for key in self.query_count:
            query_list.append(key)

        return query_list
