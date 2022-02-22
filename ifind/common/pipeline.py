__author__ = 'rose'
"""
To deal with cleaning the terms, this file contains a TermPipeline class
 as well as TermProcessors, a TermPipeline is made of processors and
 runs a term provided through each of the processors in the list to see
 if a cleaned term is returned at the end
"""
import re

class TermPipeline():
    """

    """

    def __init__(self):
        """
        constructor for TermPipeline
        :return:
        """
        #lower case
        self.pipeline = []

    def add_processor(self, termprocessor):
        """ Adds a term processor to the pipeline
        :param termprocessor: ifind.common.TermProcessor
        :return: None
        """
        self.pipeline.append(termprocessor)

    def process(self, term):
        """
        goes through each processor in the pipeline, stops if
        term is removed at any point
        :return:
        """
        for processor in self.pipeline:
            #for each processor in the pipeline perform the check
            #if returns None at any point, exit the pipeline
            #first set the processor term to be the current term
            term = processor.process(term)
            #now perform the check
            #return None if no term left
            if term is None:
                return None
            #else set the term to be the result
        #if the pipeline has gone through all checks, return term
        return term


class TermProcessor():

    def process(self, term):
        """
        :param term: string
        :return: lowercase string
        """
        return term.lower()


class LengthTermProcessor(TermProcessor):

    def __init__(self):
        self.min_len = 3

    def set_min_length(self, min_len):
        if min_len > 0:
            self.min_len = min_len

    def process(self, term):
        """
        :param term: takes a term
        :return: returns the term, if it meets the minimum length criteria
        """
        if len(term) >= self.min_len:
            return term
        else:
            return None


class PunctuationTermProcessor(TermProcessor):

    def process(self, term):

        """remove punctation surrounding a term
        :param term:
        :return: term without punctation
        """
        #get the last character
        #is there a possibility multiple punctuation at start and end?
        length = len(term)
        firstChar = term[0:1]
        if str(firstChar).isalnum():
            term = term
        else:
            #print "cutting first letter " + firstChar + " from " +term
            term = term[1:length]
            #print "term now " +term
        #get length again incase punctuation at start and end
        length = len(term)
        lastChar = term[length-1:length]
        if str(lastChar).isalnum():
            term = term
        else:
            #print "cutting last letter " + lastChar + "from " + term
            term = term[0:length-1]
            #print " is now " + term

        #now check if there's nothing left, then don't add, if there is, add it
        if term:
            return term
        else:
            return None

class StopwordTermProcessor(TermProcessor):

    def __init__(self, stopwordfile=None, stoplist=None):
        """
        :return:
        """
        if stoplist:
            self.stoplist = stoplist
        else:
            self.stoplist = []

        if stopwordfile:
            self.read_stopwordfile(stopwordfile)

    def process(self, term):
        if term in self.stoplist:
            return None
        else:
            return term

    def set_stoplist(self, stoplist):
        self.stoplist=stoplist
        #print self.stoplist

    def read_stopwordfile(self, stopwordfile):
        stopwords = open(stopwordfile).readlines()
        for term in stopwords:
            self.stoplist.append(term.strip())
        #print self.stoplist

class AlphaTermProcessor(TermProcessor):

    def process(self, term):
        clean =''
        for c in term:
            if c.isalpha() or c==' ':
                clean +=c

        clean = re.sub(r'\s+', ' ', clean)
        #returns unicode, strip trailing and leading whitespace
        return clean.strip()

class SpecialCharProcessor(TermProcessor):

    def process(self, term):
        cleaned = ''
        for letter in term:
            if letter.isalnum() or letter == ' ':
                cleaned += letter
        if cleaned.__len__() > 0:
            return cleaned
        else:
            return None
