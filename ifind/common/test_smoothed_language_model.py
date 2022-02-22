
from language_model import LanguageModel
from smoothed_language_model import SmoothedLanguageModel, LaPlaceLanguageModel, BayesLanguageModel
import unittest
import logging
import sys

class TestSmoothedLanguageModel(unittest.TestCase):

    def setUp(self):

        self.doc = { 'hello': 1,
                'world': 2,
                'help': 1
        }

        self.col = {'hello': 20,
               'world': 5,
               'good': 5,
               'bye': 15,
               'free': 1,
               'code': 1,
               'source': 1,
               'compile': 1,
               'error': 1
        }

        self.colLM = LanguageModel(term_dict=self.col)
        self.docLM = LanguageModel(term_dict=self.doc)

    def test_calculate_likelihood(self):
        model = SmoothedLanguageModel(self.docLM, self.colLM, lam=0.5)
        phello = model.get_term_prob('hello')
        self.assertEquals(phello, (1.0/8.0)+(1.0/5.0))

        phelp = model.get_term_prob('help')
        self.assertEquals(phelp, (1.0/8.0))

        pworld = model.get_term_prob('world')
        self.assertEquals(pworld, (1.0/4.0)+(1.0/20.0))

        perror = model.get_term_prob('error')
        self.assertEquals(perror, 1.0/100.0)

    def test_calculate_laplace_likelihood(self):
        model = LaPlaceLanguageModel(self.docLM, self.colLM, alpha = 1.0)
        phello = model.get_term_prob('hello')
        self.assertEquals(phello,2.0/13.0)

        phelp = model.get_term_prob('help')
        self.assertEquals(phelp,2.0/13.0)

        pworld = model.get_term_prob('world')
        self.assertEquals(pworld,3.0/13.0)

        perror = model.get_term_prob('error')
        self.assertEquals(perror,1.0/13.0)



    def test_calculate_JM_likelihood(self):
        pass

    def test_calculate_bayes_likelihood(self):
        model = BayesLanguageModel(self.docLM, self.colLM, beta = 5.0)


        phello = model.get_term_prob('hello')
        self.assertAlmostEqual(phello, 3.0/9.0)

        phelp = model.get_term_prob('help')
        self.assertAlmostEqual(phelp, 1.0/9.0)

        pworld = model.get_term_prob('world')
        self.assertAlmostEqual(pworld, 2.5/9.0)

        perror = model.get_term_prob('error')
        self.assertAlmostEqual(perror, 1.0/90.0)

if __name__ == '__main__':
    logging.basicConfig(stream=sys.stderr)
    logging.getLogger("TestSmoothedModel").setLevel(logging.DEBUG)
    unittest.main(exit=False)


