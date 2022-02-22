#!/usr/bin/env python
# -*- coding: utf-8 -*-

#
# seekiir Framework - Retrieval
# AutomatedRetrievalConfigReader implementation
#

__author__ = 'David Maxwell <maxwelld90@gmail.com>'
__date__ = '2012-11-18'

from ifind.seeker.abstract_config_reader import AbstractConfigReader

class AutomatedRetrievalConfigReader(AbstractConfigReader):
    '''
    Config reader class for the automated retrieval module.
    A derived class from abstract class framework.common.abstract_config_reader.AbstractConfigReader.
    Provides the settings that are expected for an automated retrieval config file.
    '''
    def __init__(self, filename):
        '''
        Initialises the class. Ensures that the abstract class is initialised through use of super(). Initialise any additional required objects here.
        '''
        settings = {
            'data': {
                'query_file'     : (str, None),
                'qrel_file'      : (str, None),
                },
            'output': {
                'experiment_name': (str, None),
                'base_dir'       : (str, None),
                },
            'applications': {
                'trec_eval_path' : (str, None),
                },
            'index': {
                'directory'      : (str, None),
                'name'           : (str, None),
                },
            'retrieval': {
                'model'          : (str, 'bm25'),
                'max_results'    : (int, 1000),
                'b'              : (str, ''),
                'c'              : (str, ''),
                'k1'             : (str, ''),
                },
        }
        
        super(AutomatedRetrievalConfigReader, self).__init__(filename)