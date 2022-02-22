__author__ = 'leif'


class RotationOrdering(object):
    """ creates ordering for lists with an attribute id

    """
    def __init__(self):
        pass

    def number_of_orderings(self, slist=None):
        return 1

    def get_ordering(self, slist, i=0):
        """ given a list (i.e. of pages, cats), return the ith ordering

        :param list with and id:
        :param i:
        :return: list of ids
        """

        id_list = []
        for p in slist:
            if p.id:
                id_list.append(p.id)

        from random import shuffle
        shuffle(id_list)
        #id_list = id_list[::-1]

        return id_list


class PermutatedRotationOrdering(RotationOrdering):

    def number_of_orderings(self, slist=None):
        return reduce (lambda x, y: x * y, range (1, len (slist) + 1), 1)

    def get_ordering(self, slist, i=0):
        return self.PermN(slist, i)

    def PermN (self, seq, index):
        "Returns the th permutation of  (in proper order)"
        seqc = list (seq [:])
        result = []
        fact = self.number_of_orderings(seq)
        index %= fact
        while seqc:
            fact = fact / len (seqc)
            choice, index = index // fact, index % fact
            result += [seqc.pop (choice)]
        return result




