__author__ = 'divya'

import numpy as np
import logging

from .P1_calc_edge_set import calculate_edge_set

#function to calculate the set of edges between two sets
def check_primary(SM_orig, CL, c_initiator_MKNN, c_label_current, log):

    #logger = log.get_logger(__name__)
    logger = logging.getLogger('root')
    logger.debug("Debugging from inside P1_check_primary_conn module")

    add_flag = -1
    c_members_current = np.where(CL[:]==c_label_current)[0].T
    edge_set = calculate_edge_set(SM_orig, c_members_current, np.matrix([[int(c_initiator_MKNN)]]), False, log)
    edge_set = edge_set[edge_set !=0]
    if(edge_set.size):
        add_flag = 0
    return add_flag
