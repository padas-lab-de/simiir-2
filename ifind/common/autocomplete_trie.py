from whoosh.index import open_dir
import operator
import datrie
import string
import os


class AutocompleteTrie(object):
    """
    A class implementing a trie data structure to provide suggestions to aid participants to complete queries.
    Employs the use of the datrie package.

    Author: dmax
    Date: 2013-11-12
    Revision: 3
    """
    def __init__(self,
                 index_path,
                 stopwords_path,
                 vocab_path,
                 vocab_trie_path,
                 min_occurrences=3,
                 suggestion_count=-1,
                 include_stopwords=False):
        """
        AutocompleteTrie constructor. Creates an instance of the AutocompleteTrie class.

        Args:
            index_path (str): path to the document index to use.
            stopwords_path (str): path to the stopwords file to use.
            vocab_path (str): path to the vocabulary file to use.
            vocab_trie_path (str): path to the trie file to use.
            min_occurrences (int): number of times a term should appear before being included in the trie.
            suggestion_count (int): number of suggestions to provide to end users (-1 = max of 10, 0 = none).
            include_stopwords (bool): include stopwords in the suggestions.
        """
        self.__index_path = index_path
        self.__vocab_path = vocab_path
        self.__stopwords_path = stopwords_path
        self.__vocab_trie_path = vocab_trie_path

        self.__min_occurrences = min_occurrences
        self.__suggestion_count = suggestion_count
        self.__include_stopwords = include_stopwords
        self.__include_fields = ['content', 'title']

        self.__vocab_handle = self.__get_vocab_file_handle()
        self.__stopwords = self.__get_stopwords_list()
        self.__trie = self.__get_trie()

    def __get_vocab_file_handle(self):
        """
        Returns a handle for the vocabulary file.
        If the file does not exist, the file is created and a handle is then returned to the new file.
        """
        def sum_occurrences(reader_param, term_unicode_param):
            """
            A small helper function that returns the total number of occurrences of a term across the fields
            mentioned in the instance variable __include_fields.
            """
            summed_occurrences = 0

            for field in self.__include_fields:
                summed_occurrences += int(reader_param.frequency(field, term_unicode_param))

            return summed_occurrences

        if os.path.exists(self.__vocab_path):
            return open(self.__vocab_path, 'r')
        else:
            print "Vocabulary file not found. Building vocabulary file..."
            index = open_dir(self.__index_path)
            vocab_handle = open(self.__vocab_path, 'w+')
            vocab_dict = {}

            with index.reader() as reader:
                for term in reader.all_terms():
                    term_unicode = term[1]

                    if term[0] in self.__include_fields:
                        occurrences = sum_occurrences(reader, term_unicode)
                        vocab_dict[term_unicode] = occurrences

            vocab_dict = sorted(vocab_dict.iteritems(), key=operator.itemgetter(1), reverse=True)

            for term in vocab_dict:
                vocab_handle.write('{0},{1}{2}'.format(term[0], term[1], os.linesep))

            vocab_handle.seek(0)
            return vocab_handle


    def __get_stopwords_list(self):
        """
        Returns a list of stopwords, read in from the file pointed to by instance variable __stopword_path.
        """
        try:
            stopwords = open(self.__stopwords_path, 'r')
        except IOError:
            print ("Stopwords file could not be found for constructing a suggestion trie!")
            return []

        return_list = []

        for word in stopwords:
            return_list.append(unicode(word.strip()))

        return return_list


    def __get_trie(self):
        """
        Opens and returns the trie if located on backing storage.
        If the trie does not exist, a new one is created and saved!
        """

        if os.path.exists(self.__vocab_trie_path):
            print "Loading trie..."
            return datrie.BaseTrie.load(self.__vocab_trie_path)
        else:
            print "Trie not found - creating..."
            trie = datrie.BaseTrie(string.printable)  # Our acceptable characters - everything in string.printable

            for input_line in self.__vocab_handle:
                input_line = input_line.strip().split(',')
                term = unicode(input_line[0])
                frequency = long(input_line[1])

                trie[term] = frequency

            trie.save(self.__vocab_trie_path)
            return trie


    def suggest(self, characters):
        """
        Returns a list of unicode suggestions to assist in completing a query. The more frequently occurring the term in
        the collection used, the higher up the suggestion list the term will be.
        The list returned is dependant on two main factors.
            - Instance variable __min_occurrences determines how many times a term should appear before being eligible.
            - Instance variable __suggestion_count determines the maximum number of suggestions to be returned. If set
              to -1, the top 10 suggestions are returned. When set to 0, an empty list is always returned.
        """
        results = self.__trie.items(unicode(characters))
        results = sorted(results, key=operator.itemgetter(1), reverse=True)  # Order results by descending occurrence

        # Remove stopwords from the result list if the option to include stopwords isn't enabled.
        if not self.__include_stopwords:
            results[:] = [x for x in results if x[0] not in self.__stopwords]

        # Trim the results list to size if a size has been specified!
        if self.__suggestion_count == -1:
            results = results[0:10]
        else:
            results = results[0:self.__suggestion_count]

        # Return the unicode strings only of our resulting list.
        return [i[0] for i in results]


    @staticmethod
    def initialise_files(index_path,
             stopwords_path,
             vocab_path,
             vocab_trie_path):
        """
        Initialises a AutocompleteTrie with the aim of creating the necessary vocabulary files.
        """
        AutocompleteTrie(index_path=index_path,
                       stopwords_path=stopwords_path,
                       vocab_path=vocab_path,
                       vocab_trie_path=vocab_trie_path)