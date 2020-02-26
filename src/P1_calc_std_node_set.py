__author__ = 'divya'

import numpy as np
import logging
from .P1_calc_edge_set import calculate_edge_set

#function to calculate the set of edges between two sets
def calculate_std_node_set(SM_orig, set_input, log):

    #logger = log.get_logger(__name__)
    logger = logging.getLogger('root')
    logger.debug("Debugging from inside P1_calc_std_node_set module")

    set_edges = calculate_edge_set(SM_orig, set_input, set_input, True, log)
    SD = np.std(set_edges[set_edges!=0])
    return SD
