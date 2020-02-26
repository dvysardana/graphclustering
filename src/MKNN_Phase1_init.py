__author__ = 'divya'

import logging

from .P1_calc_MKNN import calculate_MKNN
from .P1_calc_degree import calculate_degree
from .P1_calc_radius_ver_2 import calculate_radius_ver_2
from .P1_calc_radius_ver_1 import calculate_radius_ver_1
from .P1_calc_CI import calculate_CI

def MKNN_Phase1_init(SM, SM_orig, num_nodes, K, log):

    logger = logging.getLogger('root')
    logger.debug("Debugging from inside MKNN_Phase1_init")


    #Calculate the MKNN matrix
    MKNN = calculate_MKNN(SM, num_nodes, K, log)
    MKNN

    #Calculate the degree vector
    Deg = calculate_degree(SM_orig, num_nodes, log)

    #Calculate the radius vector
    #MKNN_rad = calculate_radius_ver_2(SM, MKNN, Deg, num_nodes, log)
    MKNN_rad = calculate_radius_ver_1(SM, MKNN, num_nodes, log)

    #Calculate cluster initiator order using MKNN_rad
    CI = calculate_CI(MKNN_rad, num_nodes, log)

    return (MKNN, Deg, MKNN_rad, CI)