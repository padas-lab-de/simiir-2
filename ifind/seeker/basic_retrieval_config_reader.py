#!/usr/bin/env python
# -*- coding: utf-8 -*-

#
# seekiir Framework - Retrieval
# BasicRetrievalConfigReader implementation
#

__author__ = 'leifos'
__date__ = '2012-10-28'

from ifind.seeker.abstract_config_reader import AbstractConfigReader

class BasicRetrievalConfigReader(AbstractConfigReader):
    '''
    Config reader class for the retrieval module.
    A derived class from abstract class framework.common.abstract_config_reader.AbstractConfigReader.
    Provides the settings that are expected for an indexing config file.
    '''

    def __init__(self, filename):
        '''
        Initialises the class. Ensures that the abstract class is initialised through use of super(). Initialise any additional required objects here.
        '''
        self.settings = { # This needs to go inside __init__ otherwise it updates for all instances of BasicRetrievalConfigReader
            'data': {
                'query_file' : (str, None),
                'result_file': (str, None)
            },
            'retrieval':{
                'model' : (str, 'bm25'),
                'num_results' : (int, 1000),
                'b': (float, 0.75),
                'c': (float, 10.0),
                'k1':(float, 1.5)
            },
            'index': {
                'directory'  : (str, None),
                'name'       : (str, None)
            },
        }

        super(BasicRetrievalConfigReader, self).__init__(filename)