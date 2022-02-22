__author__ = 'rose'

class LanguageModel(object):
    """
    manages reading in a file and splitting into a term, occurrence dictionary
    or takes a term, occurrence dictionary
    calculates the probability of a term occurring given the occurrence dict
    """

    def __init__(self, file=None , term_dict=None):
        self.occurrence_dict = {}
        self.total_occurrences = 0

        if file:
            self._populate_occurrences(file)
        else:
            self.occurrence_dict = term_dict

        self._calc_total_occurrences()


    def _populate_occurrences(self, file_name):
        """
        reads in a file and stores in occurrences dictionary
        :param fileName
        """
        if file_name:
            f = open(file_name, 'r')
            for line in f:
                split_line=line.split()
                term = split_line[0]
                #TODO need to make robust for errors in input file
                count = int(split_line[1])
                self.occurrence_dict[term] = count

    def _calc_total_occurrences(self):
        """
        counts the total number of term occurrences in occurrence_dict
        """
        for term, count in self.occurrence_dict.items():
            self.total_occurrences += count

    def get_total_occurrences(self):
        return self.total_occurrences

    def get_num_terms(self):
        return len(self.occurrence_dict)

    def get_num_occurrences(self,term):
        """
        :param term: the individual term for which count is desired
        :return: number of occurrences for term in occurrence dict, 0 if not in
        """
        if term in self.occurrence_dict:
            return self.occurrence_dict[term]
        else:
            return 0

    def get_term_prob(self, term):
        """
        calculates the probability of a term
        :param term:
        :return:
        """
        term_count = self.get_num_occurrences(term)
        if  term_count == 0:
            return 0
        else:
            result = float(term_count)/float(self.get_total_occurrences())
            return result


