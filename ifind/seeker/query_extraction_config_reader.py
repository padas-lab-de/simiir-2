__author__ = 'Kojayboy'

#!/usr/bin/env python
# -*- coding: utf-8 -*-

#
# seekiir Framework - Indexing
# CrawlerConfigReader implementation
#


import string
from ifind.seeker.abstract_config_reader import AbstractConfigReader
from ifind.seeker.abstract_config_reader import BadConfigError

class QueryExtractionConfigReader(AbstractConfigReader):
	'''
	Config reader class for the indexing module. A derived class from abstract class framework.common.abstract_config_reader.AbstractConfigReader. Provides the settings that are expected for an indexing config file.
	'''
	settings = {
	# The dictionary of values we are expecting - note that it mimics the strutcture of the configuration file itself. Each attribute has a tuple in the form (default value, type reference, reference to checker)
	'queries': {
	'type': (str, 'single'),
	'number_of_queries': (int, 2000),
	'stopword_removal': (bool, True),
	'file': (str, None),
	'output': (str, 'queries.qry'),
	'html': (bool, True)
	}
	}

	def __init__(self, filename):
		'''
		Initialises the class. Ensures that the abstract class is initialised through use of super(). Initialise any additional required objects here.
		'''

		super(QueryExtractionConfigReader, self).__init__(filename)