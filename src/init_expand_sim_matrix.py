__author__ = 'divya'

import logging


def expand_SM(SM, SM_orig, num_nodes, log):
    #expand SM upto k hops.
    #expand the similarity matrix

    #logger = log.get_logger(__name__)
    logger = logging.getLogger('root')
    logger.debug("Debugging from inside init_expand_sim_matrix module")

    for i in range(num_nodes):
        for j in range(num_nodes):
            if(i != j):
                max= SM[i,j]
                for k in range(num_nodes):
                    if(k!=i and k != j):
                        if(SM[i,k] != 0 and SM[k,j] != 0):
                            tmpSim = SM[i,k]*SM[k,j]
                            if(tmpSim > max):
                                max = tmpSim
                                SM[i,j] = max

    return SM