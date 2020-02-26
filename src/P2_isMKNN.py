__author__ = 'divya'

import numpy as np
import logging

#check if the two nodes are MKNN neighbors of each other
def is_MKNN(node_x, node_y, MKNN, log):

    #logger = log.get_logger(__name__)
    logger = logging.getLogger('root')
    logger.debug("Debugging from inside P2_isMKNN module")

    if(node_y in np.array(MKNN[node_x,:])):
        return True
    return False