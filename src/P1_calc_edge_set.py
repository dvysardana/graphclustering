__author__ = 'divya'

import numpy as np
import logging

#function to calculate the set of edges between two sets
def calculate_edge_set(SM_orig, set_input1, set_input2, same, log):

    #logger = log.get_logger(__name__)
    logger = logging.getLogger('root')
    logger.debug("Debugging from inside P1_calc_edge_set module")


    #set_input1 = np.matrix([[2]])
    #set_input2 = np.matrix([[3]])
    #same = False
    set_edges = []
    for i in range(np.shape(set_input1)[0]):
        for j in range(np.shape(set_input2)[0]):
            if(same==True):
                if(i < j):
                    set_edges.append(float(SM_orig[set_input1[i], set_input2[j]]))
            else:
                set_edges.append(float(SM_orig[set_input1[i], set_input2[j]]))
    matrix_edges = np.matrix(set_edges)
    #returns 0 as well if an edge weight = 0
    return  matrix_edges
