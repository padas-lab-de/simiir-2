#!/usr/bin/env python
# -*- coding: utf-8 -*-

#
# seekiir Framework - Indexing
# ListReader class
#

import string
from os import linesep
from ifind.seeker.common_helpers import file_exists

class ListReader(list):
    '''
    A simple class which extends the Python list object. Reads in the input file list and stores them in this object.
    '''

    def __init__(self, filename):
        '''
        Initialises the required instance variables. Opens the input file (if possible) and calls the __read_file method. Throws an IOError exception if the file cannot be opened.
        '''
        self.__filename = filename

        if file_exists(self.__filename):
            self.__file_handle = open(self.__filename, mode='r')
            self.__read_file()
        elif filename is not None:
            raise IOError("Could not open the specified list file, %s." % self.__filename)

    def __read_file(self):
        '''
        Reads the opened input file and places valid filenames in the internal list.
        '''
        lines = self.__file_handle.readlines()
        self.__file_handle.close()

        for line in lines:
            line = string.rstrip(line, linesep) # Strip trailing newline character

            if not(line.startswith('#') or len(' '.join(line.split())) == 0): # Line doesn't start with a hash, and when all whitespace is removed, the string doesn't have a length of zero
                append_value = self._can_append_entry(line)

                if append_value:
                    self.append(append_value.strip())

    def save(self, filename):
        '''
        Saves the contents of the list object to a file, one item per line. The filename to save to is specified as filename. If the file exists, the contents of the original file is overwritten.
        '''
        file_object = open(filename, 'w')

        for item in self:
            file_object.write(str(item) + linesep) # One item per line (os.linesep to split lines natively)

        file_object.close()

    def _can_append_entry(self, line):
        '''
        A callback method which is called in __read_file(). This method returns either False if the line should not be appended to the list, or the value which should be appended to this. This means that the method can alter the value to be appended (e.g. converting to lowercase) before the append method is called.
        '''
        return line