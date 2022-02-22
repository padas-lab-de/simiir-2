#!/usr/bin/env python
# -*- coding: utf-8 -*-

#
# seekiir Framework - Common Files
# AbstractConfigReader and Associated Classes
#

__author__ = 'David Maxwell <maxwelld90@gmail.com>'
__date__ = '2012-10-31'

from ConfigParser import ConfigParser
from ifind.seeker.common_helpers import file_exists
from base_exception import Error as BaseError

class AbstractConfigReader(object):
    '''
    The abstract config file reader. Do NOT instantiate this class directly. The results obtained will be undefined. Extends this class for each different kind of config file you'd like to load and check. Once loaded, a derived class will contain a dictionary of settings that can be accessed using dot notation - and a types dictionary, too.
    '''
    settings_types = {} # A blank dictionary which contains the types for each value.
    settings = {} # A blank settings for an abstract class.
    config_type_method_dict = {} #is takes the type and relates it to the appropriate ConfigParser read method

    def __init__(self, filename = None):
        '''
        Initialises the abstract class. Calls self.__set_settings(), which repopulates self.settings and populates self.settings_types. If a valid filename is provided, we then call self.__read_settings_from_file() to open the file and read the configuration settings from there.
        '''
        self.__config_parser = ConfigParser()
        self.__set_settings(self.settings) # Referring to our settings
        self.__config_type_method_dict = {
            str   : self.__config_parser.get,
            bool  : self.__config_parser.getboolean,
            int   : self.__config_parser.getint,
            float : self.__config_parser.getfloat
        }

        if filename is not None:
            if not file_exists(filename): # File doesn't exist!
                raise IOError("Could not find the specified configuration file, %s." % (filename))

            self.__read_settings_from_file(filename) # File does exist; attempt to read.

    def __set_settings(self, settings):
        '''
        Populates the two dictionaries self.settings_types and self.settings based upon the initial dictionary self.settings defined in a concrete class. Resolves each of the tuples in this initial dictionary, setting self.settings to the default values.
        '''
        for section, values in settings.items():
            nested_types = self.DictDotNotation()
            nested_settings = self.DictDotNotation()

            for value_name, value_tuple in values.items():
                # tuple[0] == type, tuple[1] == default value
                nested_types[value_name] = value_tuple[0]
                nested_settings[value_name] = value_tuple[1]

            # Appends our DictDotNotation dictionaries to the relevant parent dictionaries.
            self.settings_types[section] = nested_types
            self.settings[section] = nested_settings

        # Convert our dictionaries to DictDotNotNotation so we can access them using dots!
        self.settings_types = self.DictDotNotation(self.settings_types)
        self.settings = self.DictDotNotation(self.settings)

    def __read_settings_from_file(self, filename):
        '''
        Reads settings from the specified config file. Replaces the defaults in self.settings.
        If a setting does not exist in the config file which does not have a default value, a BadConfigError exception is thrown.
        '''
        self.__config_parser.read(filename) # Opens the ConfigParser

        for section, values in self.settings.items():
            for value_name, default_value in values.items():
                value_type = self.settings_types[section][value_name]
                config_file_value = None

                if self.__config_parser.has_option(section, value_name): # If the section/value combo exists within the config file, we want to pull its value out using the appropriate getter method (based on the expected type). If the value doesn't match the expected type, a ValueError exception will be thrown.
                    if value_type in self.__config_type_method_dict:
                        config_file_value = self.__config_type_method_dict[value_type](section, value_name)
                    else:
                        raise BadConfigError("Specified type '%s' cannot be used." % (str(value_type)))

                if default_value == None and config_file_value == None: # No value found in the config file, and no default provided - we cannot continue!
                    raise BadConfigError(
                        "The required value '%s' in section '%s' of config file '%s' was not specified."
                        % (value_name, section, filename))

                if config_file_value != None: # If a default was supplied, and the config file provides a new value, we replace the existing with this one.
                    self.settings[section][value_name] = config_file_value

    def add_settings_group(self, group_name):
        '''
        Adds a new group to the settings dictionary. If the group name specified by parameter group_name already exists, this method simply returns False. Otherwise, the group is added to the settings dictionary, and True is returned to indicate a successful addition.
        '''
        if group_name not in self.settings:
            new_dict = self.DictDotNotation()
            self.settings[group_name] = new_dict
            return True

        return False # Group already exists; return False to show addition failed

    def save(self, filename):
        '''
        Saves the settings dictionary to a file, specified by parameter filename. If the file exists, any contents within the file will be overwritten.
        '''
        for section_name, section_values in self.settings.items():
            values_dict = {}

            # Loop through each section's values, and check if they are not None (undefined) - if not, add them to temporary dictionary values_dict.
            for value_name, value in section_values.items():
                if value is not None:
                    values_dict[value_name] = value

            # Using the temporary dictionary, check if the section has any values - if so, we add the section to the ConfigParser and add the associated values.
            if len(values_dict) > 0:
                self.__config_parser.add_section(section_name)

                for value_name, value in values_dict.items():
                    self.__config_parser.set(section_name, value_name, value)

        # Open the new file for writing, write to it, and close cleanly.
        file_object = open(filename, 'w')
        self.__config_parser.write(file_object)
        file_object.close()


    def print_params(self):
        '''
        Prints each parameter from a new instance of the calling class.
        '''
        settings = self.settings

        for section, values in settings.items():
            for value_name, value in values.items():
                print "%s\t%s\t%s" % (section, value_name, value)

    class DictDotNotation(dict):
        '''
        A class which extends the Python native dict object to allow the access of elements using dot notation. Based on code from http://parand.com/say/index.php/2008/10/24/python-dot-notation-dictionary-access/
        '''
        def __getattr__(self, attr):
            return self.get(attr, None)

        __setattr__ = dict.__setitem__
        __delattr__ = dict.__delitem__

class BadConfigError(BaseError):
    '''
    Exception class used for the identification of a seekiir config error.
    '''
    pass