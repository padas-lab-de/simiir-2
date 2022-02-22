# A small module containing functions to help tidy things up.

import re
import html
# from html.parser import HTMLParser

def clean_html(input_str):
    """
    Given an HTML-formatted string, decodes HTML entitles and removes any HTML tags.
    A list of terms is returned, leaving text. Punctuation is not removed.
    """
    # parser = HTMLParser.HTMLParser()
    
    # stripped = parser.unescape(input_str)
    # stripped = re.sub('<.*?>', '', stripped)
    
    if isinstance(input_str, str):
        stripped = re.sub('<.*?>', '', input_str)
    else:
        stripped = re.sub('<.*?>', '', input_str.decode("utf-8"))
    
    stripped = stripped.lower()
    stripped_list = stripped.split(' ')
    
    return stripped_list