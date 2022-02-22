#!/usr/bin/env python
# -*- coding: utf-8 -*-

#
# seekiir Framework - Indexing
# IndexConfigReader implementation
#

__author__ = 'David Maxwell <maxwelld90@gmail.com>'
__date__ = '2012-10-31'

from ifind.seeker.abstract_config_reader import AbstractConfigReader

class IndexConfigReader(AbstractConfigReader):
    '''
    Config reader class for the indexing module.
    A derived class from abstract class framework.common.abstract_config_reader.AbstractConfigReader.
    Provides the settings that are expected for an indexing config file.
    '''
    settings = {
        'source_data': {
            'format'         : (str, 'base'),
            'compression'    : (str, 'gz'),
        },
        'index': {
            'directory'      : (str, None),
            'name'           : (str, None),
            'append'         : (bool, True),
        },
        'analysis': {
            'clean_html'     : (bool, False),
            'apply_stemming' : (bool, True),
            'stemmer'        : (str, 'porter'),
            'apply_stopping' : (bool, True),
            'stopword_path'  : (str, ''),
        },
        'batch_settings': {
            'commit_period'  : (int, 0),
            'commit_limit'   : (int, 1000),
            'lrb_limit'      : (int, -1),
            'num_cores'      : (int, 1),
            'mb_limit'       : (int, 512)
        }
    }

    def __init__(self, filename):
        '''
        Initialises the class. Ensures that the abstract class is initialised through use of super(). Initialise any additional required objects here.
        '''
        super(IndexConfigReader, self).__init__(filename)