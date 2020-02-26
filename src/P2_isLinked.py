__author__ = 'divya'

import logging

from .P2_isMKNN import is_MKNN

#Function to check if a node node_x is linked to a cluster cluster_y
def is_Linked(node_x, cluster_y, MKNN, log):

    #logger = log.get_logger(__name__)
    logger = logging.getLogger('root')
    logger.debug("Debugging from inside P2_isLinked module")

    for node_y in cluster_y:
        if(is_MKNN(node_x, node_y, MKNN, log)):
            return True

    return False


