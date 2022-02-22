#!/usr/bin/env python
# -*- coding: utf-8 -*-

#
# seekiir Framework - Indexing
# CrawlerConfigReader implementation
#


import string
from ifind.seeker.abstract_config_reader import AbstractConfigReader
from ifind.seeker.abstract_config_reader import BadConfigError

class BasicCrawlingConfigReader(AbstractConfigReader):
	'''
	Config reader class for the indexing module. A derived class from abstract class framework.common.abstract_config_reader.AbstractConfigReader. Provides the settings that are expected for an indexing config file.
	'''
	settings = {
		# The dictionary of values we are expecting - note that it mimics the strutcture of the configuration file itself. Each attribute has a tuple in the form (default value, type reference, reference to checker)
		'spider': {
			'name': (str, None),
		},
		'output': {
			'directory': (str, None),
			'html': (bool, True),
		    'html_files': (int, 1000)
		},
		'trec': {
			'trec': (bool, True),
		    'trec_files': (int, 1000),
			'doc_prefix': (str, None),
			'key_length': (int, 7),
			'id_start': (int, 0)
		}
	}

	def __init__(self, filename):
		'''
		Initialises the class. Ensures that the abstract class is initialised through use of super(). Initialise any additional required objects here.
		'''

		super(BasicCrawlingConfigReader, self).__init__(filename)