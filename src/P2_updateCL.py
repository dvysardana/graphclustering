__author__ = 'divya'

import logging

def updateCL(CL_List, old_cluster_label, new_cluster_label, log):
    #In CL, change all rows with the old cluster label to new
    #cluster label

    #logger = log.get_logger(__name__)
    logger = logging.getLogger('root')
    logger.debug("Debugging from inside P2_updateCL module")

    indices = [i for i, x in enumerate(CL_List) if x == old_cluster_label]
    for i in indices:
        CL_List[i] = new_cluster_label

    return CL_List

