#!/usr/bin/env python
# -*- coding: latin-1 -*-

__author__ = 'rose'

from BeautifulSoup import BeautifulSoup
import re
import sys

class PositionContentExtractor(object):

    def __init__(self, div_ids=None):
        self.div_ids = div_ids
        self.html = ''
        self.html_soup = None
        self.text = ''

    #if you set the div ids, then the html is processed again
    def set_div_ids(self, ids):
        """
        this method takes a list of div ids and sets the class ids variable
        it also re-processes the html
        :param ids: ids of divs to be ignored when generating queries
        :return: None
        """
        #print "here!"
        self.div_ids = ids
        #print "ids to remove are" ,ids
        self.process_html_page(self.html)

    def process_html_page(self, html):
        """ reads in the html, parses it, and removes the set of specified div ids, assigning the text to self.text
        :param html: expects a valid html document
        :return: None
        """
        self.html = html
        self.html_soup = BeautifulSoup(html)
        self.text = self._remove_div_content()

    def get_subtext(self, num_words=0, percentage=None):
        """
            takes first num_words from text and return them as a string
            :return: a string of length num words if self.text has >= num words
             else return self.text
            """
        words = self.text.split()
        subtext = ' '
        if percentage:
            #print "percent is ", percentage
            num_words = int(round(self._calc_percentage(percentage, len(words))))
            #print "num words is ",num_words
        if num_words:
            if num_words == 0:  # return all text if 0 assumes 0 means wants all
                return self.text
            if len(words) > num_words:
                return subtext.join(words[0:num_words])
            else:
                return self.text
        else:
            return self.text

    def _remove_div_content(self):
        """
            returns a string with the content the html with the content of
            divs in div_ids removed
            :param div_ids: a list of the ids of the div to be removed
            :return:None
            """
        result = ''
        #for all div ids find the elements in the beautiful soup tree and extract
        #the corresponding div
        #this updates self.html_soup, if divs are reset then soup is regenerated
        if self.div_ids:
            for div_id in self.div_ids:
                elem = self.html_soup.find("div", {"id": div_id})
                if elem:
                    elem.extract()
                else:
                    print "div with id ", div_id, " not found"
        #set the text of the class to be the result of removing the text from the divs
        #use find all text, returns list, join list elements
        texts = self.html_soup.findAll(text=True)

        #for each of the visible elements check it's not in style, script etc.
        #add it to visible elements
        visible_elements = [self._visible_text(elem) for elem in texts]
        #visible_text = ''.join(visible_elements)
        visible_text = visible_elements

        cleaned = self._clean_result(visible_text)
        if not cleaned:
            print "no text remains for generating queries "
            #sys.exit(2)
        #print cleaned
        return cleaned

    def _clean_result(self, text):
        text = ' '.join(text)
        text = re.sub(r'\s+', ' ', text)
        #returns unicode, strip trailing and leading whitespace
        return text.strip()
        #return text

    def _calc_percentage(self, percentage, total_words):
        if total_words == 0:
            return 0
        else:
            return 100 * (float(percentage)/float(total_words))

    def _visible_text(self, element):
        if element.parent.name in ['style', 'script', '[document]', 'head', 'title']:
            return ''
        result = re.sub('<!--.*-->|\r|\n', '', str(element), flags=re.DOTALL)
        result = re.sub('\s{2,}|&nbsp;', ' ', result)
        return result

    def print_text(self):
        print self.text

    def _get_content(self, tag, id="", tag_class=""):
        """
        finds elements in the soup with a given tag and id or class
        returns the text of this element
        :param tag: target tag
        :param id: target id
        :param tag_class: target class
        :return: text of element with given id or class and tag
        """
        elem = None
        #todo assumes only one element with given id or class for given tag
        #otherwise returns text of first tag if not given an id or class
        if id:
            elem =self.html_soup.find(tag,id=id)
        elif tag_class:
            elem = self.html_soup.find(tag, {"class" : tag_class})
        else:
            elem = self.html_soup.find(tag)

        texts=''
        if elem:
            texts = elem.findAll(text=True)
        else:
            print "No divs with this id ",id, " exist"

        #for each of the visible elements check it's not in style, script etc.
        #add it to visible elements
        visible_elements = [self._visible_text(part) for part in texts]
        #visible_text = ''.join(visible_elements)
        visible_text = visible_elements

        cleaned = self._clean_result(visible_text)
        #print cleaned
        return cleaned

    def set_all_content(self, attr_values, tag):
        """
        returns a string with the visible text the html with the content of
        tags with value tag (e.g. div, footer) and attr_values (e.g. id, class)
        :param tag: the name of the tag e.g. div
        :param attr_values: a list of the values such as id values
        :return:
        """
        #todo currently assumes dealing only with IDs
        content = ""
        for value in attr_values:
            content += self._get_content(tag, id=value)
        self.text = content
        if not self.text:
            print "no text remains for generating queries"
            #sys.exit(2)




