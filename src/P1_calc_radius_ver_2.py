__author__ = 'divya'

import numpy as np
import logging

def calculate_radius_ver_2(SM, MKNN, Deg, num_nodes, log):

    #logger = log.get_logger(__name__)
    logger = logging.getLogger('root')
    logger.debug("Debugging from inside P1_calc_radius_ver_2 module")

    MKNN_rad = np.zeros(shape = (num_nodes, 1))

    for i in range(num_nodes):
        #all MKNN neighbors of node i
        a = np.array(MKNN[i,:])
        a = a[a != -1]
        type(a)

        #number of non -1 neighbors
        num_row = a.size


        sum_row = sum((Deg[int(e),0] * SM[i,int(e)]) for e in list(a)) #version 2

        #normalize sum_row
        if(num_row != 0):
            sum_row = sum_row/num_row

        MKNN_rad[i,0] = sum_row

    return np.matrix(MKNN_rad)


