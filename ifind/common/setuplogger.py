__author__ = 'leif'

import logging

logger_name = 'ifind'




def create_ifind_logger(filename):
    """ this creates a logger, and saves the log to the filename provided
    the main application should create this logger, which is then used elsewhere
    """
    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.INFO)
    fh = logging.FileHandler(filename)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    fh.setFormatter(formatter)
    logger.addHandler(fh)
    return logger


def get_ifind_logger(name):
    """ classes and functions in the ifind project can call this to get access to a common
    logger and output to it as usual logger.debug("message") or logger.info("message")
    """
    n = '%s.%s' %(logger_name,name)
    logger = logging.getLogger(n)
    return logger


