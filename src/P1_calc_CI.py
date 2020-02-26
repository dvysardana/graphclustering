__author__ = 'divya'


import numpy as np
import logging

def calculate_CI(MKNN_rad, num_nodes, log):

    #logger = log.get_logger(__name__)
    logger = logging.getLogger('root')
    logger.debug("Debugging from inside calculate_CI module")


    x = np.array(list(range(num_nodes)), dtype=int).reshape(num_nodes, 1)

    z = np.concatenate((x, np.array(MKNN_rad)), axis=1)

    col=1
    CI = np.matrix(z[np.array(z[:,col].argsort(axis=0)[::-1].tolist()).ravel()])

    return CI