__author__ = 'leif'


from rotation_ordering import PermutatedRotationOrdering
import unittest
import logging
import sys


class TestPermutatedRotationOrdering(unittest.TestCase):

    def setUp(self):
        self.logger = logging.getLogger("TestPermutatedRotationOrdering")
        self.pro = PermutatedRotationOrdering()

    def test_perm_count(self):
        l = [1,2,3]
        n = self.pro.number_of_orderings(l)
        self.assertEquals(n, 6)

        l = [1,2,3,4]
        n = self.pro.number_of_orderings(l)
        self.assertEquals(n, 24)

    def test_perm(self):
        l = [1,2,3]
        o = self.pro.get_ordering(l,0)
        self.assertEquals(o,[1,2,3])

    def test_perm_1(self):
        l = [1,2,3]
        o = self.pro.get_ordering(l,1)
        self.logger.debug(o)
        self.assertEquals(o,[1,3,2])

    def test_perm_3(self):
        l = [1,2,3]
        o = self.pro.get_ordering(l,3)
        self.logger.debug(o)
        self.assertEquals(o,[2,3,1])


    def test_perm_5(self):
        l = [1,2,3]
        o = self.pro.get_ordering(l,5)
        self.logger.debug(o)
        self.assertEquals(o,[3,2,1])


    def test_perm_23(self):
        l = [1,2,3,4]
        o = self.pro.get_ordering(l,23)
        self.logger.debug(o)
        self.assertEquals(o,[4,3,2,1])

if __name__ == '__main__':
    logging.basicConfig(stream=sys.stderr)
    logging.getLogger("TestPermutatedRotationOrdering").setLevel(logging.DEBUG)
    unittest.main(exit=False)