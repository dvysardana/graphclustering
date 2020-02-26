__author__ = 'divya'

import sys
import logging

#This function is not used any more.
#Instead a config ini file is used for the same setup.
def init_getfilename(log):

    print((sys.path))

    #logger = log.get_logger(__name__)
    logger = logging.getLogger('root')
    logger.debug("Debugging from inside init_getfilename module")


    sys.path.insert(1, '/Users/divya/Documents/Dissertation/')

    ####################
    #Synthetic Datasets
    ####################

    #Synthetic Dataset 1
    inp_file = '/Users/divya/Documents/Dissertation/data/Synthetic/A2Zsim.txt'

    #Synthetic Dataset 2
    #inp_file = '/Users/divya/Documents/Dissertation/data/Synthetic/A2Zsim1.txt'

    #Synthetic Dataset 3
    #inp_file = '/Users/divya/Documents/Dissertation/data/Synthetic/synRec3.txt'

    ####################
    #Real Datasets
    ####################

    #Real Dataset 1
    #inp_file = '/Users/divya/Documents/Dissertation/data/Real/collins2007.txt'

    return inp_file
