__author__ = 'leif'
import string
import httplib
from urlparse import urlparse


def read_in_urls(filename):
    # read in file - store in a list (url_list)
    # Open the file with read only permit
    f = open(filename, 'r')
    # Read the first line
    url_list = []
    for line in f:
        # Strip urls from spaces
        url = line.strip()
        # validate the url
        if check_url(url):
            url_list.append(url)

    f.close()
    print 'URLs has been read successfully, the next step is taking the screenshots'
    return url_list


def convert_url_to_filename(url):

    '''
    :param url: Takes a url string
    :return: a valid filename constructed from the string

    >>> convert_url_to_filename("http://www.google.com")
    'www-google-com'
    >>> convert_url_to_filename("http://www.dcs.gla.ac.uk/~leif/index.html")
    'www-dcs-gla-ac-uk-leif-index-html'
    >>> convert_url_to_filename("www.ball.com/dj")
    'www-ball-com-dj'
    '''

    # Remove the http:// from the url as it is common among all the urls
    url = url.replace('http://', '')
    valid_chars = "-_.()/ %s%s" % (string.ascii_letters, string.digits)
    # Uses a whitelist approach: any characters not present in valid_chars are removed
    # spaces,slashes and dots are replaced with dashes
    filename = ''.join(c for c in url if c in valid_chars)
    filename = filename.replace(' ', '-')  # to replace spaces in file names with dashes.
    filename = filename.replace('/', '-')  # to replace slashes in file names with dashes.
    filename = filename.replace('.', '-')  # to remove dots in file names.
    return filename


def check_url(url):
    '''
    :param url: takes a url string
    :return: true if the url exists on the web
            false: if the url does not exist on the web
    >>> urlparse('//www.cwi.nl:80/%7Eguido/Python.html')
    ParseResult(scheme='', netloc='www.cwi.nl:80', path='/%7Eguido/Python.html', params='', query='', fragment='')
    >>> urlparse('www.cwi.nl/%7Eguido/Python.html')
    ParseResult(scheme='', netloc='', path='www.cwi.nl:80/%7Eguido/Python.html', params='', query='', fragment='')
    >>> urlparse('help/Python.html')
    ParseResult(scheme='', netloc='', path='help/Python.html', params='', query='', fragment='')

    '''
    p = urlparse(url)
    conn = httplib.HTTPConnection(p.netloc)
    conn.request('HEAD', p.path)
    resp = conn.getresponse()
    return resp.status < 400


def encode_string_to_url(str):
    """ takes as string (like a name) and replaces the spaces for underscores to make a string for a url
    :param str: string
    :return: encoded string with underscores for spaces
    >>> encode_string_to_url('hello')
    'hello'
    >>> encode_string_to_url('hello world')
    'hello_world'
    >>> encode_string_to_url(' hello world ')
    'hello_world'

    """
    s = str.strip()
    return s.replace(' ', '_')



def decode_url_to_string(urlstr):
    """ takes a string (which has been part of a url) that has previously been encoded, and converts it back to a normal string
    :param urlstr: takes part of a urlstr that represents a string name
    :return: the string without the underscores
    >>> decode_url_to_string('hello_world')
    'hello world'
    """
    return urlstr.replace('_', ' ')


#fetch data for population from file
def get_trending_queries(filename):
    """Extract population data from a file.
       Returns a list of tuples created from comma separated values in file
    """
    f = open(filename, 'r')
    trend_tuples_list = []
    for line in f:
        trend_tuples_list.append(tuple((line.strip()).split(',')))
    f.close()
    return trend_tuples_list


if __name__ == '__main__':
    import doctest
    doctest.testmod()
