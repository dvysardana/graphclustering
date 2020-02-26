__author__ = 'divya'

import numpy as np
import logging

def calculate_degree(SM_orig, num_nodes, log):

    #logger = log.get_logger(__name__)
    logger = logging.getLogger('root')
    logger.debug("Debugging from inside P1_calc_degree module")

    Deg = np.zeros(shape = (num_nodes, 1))
    for i in range(num_nodes):
        Deg[i,0] =  np.count_nonzero(SM_orig[i,:])-1

    return np.matrix(Deg)
