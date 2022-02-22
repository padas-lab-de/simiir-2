__author__ = 'rose'
import unittest
import logging
import sys
from position_content_extractor import PositionContentExtractor
from pagecapture import PageCapture


class TestPositionExtractor(unittest.TestCase):

    def setUp(self):
        self.logger = logging.getLogger("TestStructuredExtractor")
        html = ' <html> <div id="header"><h1>hello world</h1>' \
               '</div><div id="content"><p>this is important</p>' \
               '<p> study computing it is fun</p></div>' \
               '<div id="footer"> <h2>byes</h2></div> ' \
               '<div id="post"> stay <div id="sub-post">should be gone</div>' \
               '</div><footer class="myfoot">at the bottom</footer></html> '
        div_ids = []
        self.extractor = PositionContentExtractor(div_ids=div_ids)
        self.extractor.process_html_page(html)

    def test_remove_div_content(self):
        div_id=["header"]
        self.extractor.set_div_ids(div_id)
        expected = "this is important study computing it is fun byes stay should be gone at the bottom"

        self.process_test_equals(expected, self.extractor.text)

        div_id = ["content"]
        expected = "hello world byes stay should be gone at the bottom"
        self.extractor.set_div_ids(div_id)

        self.process_test_equals(expected, self.extractor.text)
        #test multiple div removal
        ignore_divs = ['header','footer']
        self.extractor.set_div_ids(ignore_divs)

        expected = 'this is important study computing it is fun stay should be gone at the bottom'
        self.process_test_equals(expected, self.extractor.text)

        #test remove div within a div
        expected = "at the bottom"
        ignore_divs = ['header','footer','content','post']
        self.extractor.set_div_ids(ignore_divs)
        self.process_test_equals(expected, self.extractor.text)

    def test_get_subtext(self):
        self.extractor.text = "this is a sentence which has some words in it"
        result = self.extractor.get_subtext(num_words=2)
        expected = "this is"
        self.process_test_equals(expected,result)
        #test greater than length returns whole text
        result = self.extractor.get_subtext(num_words=12)
        self.process_test_equals(self.extractor.text, result)

    def test_get_content(self):
        expected = "at the bottom"
        result = self.extractor._get_content("footer",tag_class="myfoot")
        self.process_test_equals(expected,result)

    def test_set_all_content(self):
        included_ids = ['content']
        expected = "this is important study computing it is fun"
        self.extractor.set_all_content(included_ids,"div")
        result = self.extractor.text
        self.process_test_equals(expected,result)

    def process_test_equals(self, expected, result):
        msg = 'Expected but got: ', expected, result
        self.assertEqual(expected, result, msg)




class WebTestPositionExtractor(unittest.TestCase):

    def setUp(self):
        """
        Setting up test on offensive page
        """
        self.logger = logging.getLogger("TestStructuredExtractor")
        pc = PageCapture('https://www.gov.uk/vehicles-you-can-drive')
        self.html = pc.get_page_sourcecode()
        self.div_ids=[]


        #from BeautifulSoup import BeautifulSoup
        #soup = BeautifulSoup(html)
        #texts = soup.findAll(text=True)
        #print texts

    def test_extract_from_bad_page(self):
        self.extractor = PositionContentExtractor(div_ids=self.div_ids)
        self.extractor.process_html_page(self.html)
        #todo pass if no errors?
        div_ids = ['related','skiplink-container']
        self.extractor.set_div_ids(div_ids)






if __name__ == '__main__':
    logging.basicConfig(stream=sys.stderr)
    logging.getLogger("TestPositionExtractor").setLevel(logging.DEBUG)
    unittest.main(exit=False)

