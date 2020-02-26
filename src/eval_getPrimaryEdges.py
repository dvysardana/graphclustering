__author__ = 'divya'

import logging

def getPrimaryEdges(nodes_Ci, SM_orig, log):

    #logger = log.get_logger(__name__)
    logger = logging.getLogger('root')
    logger.debug("Debugging from inside eval_getPrimaryEdges module")

    primary_edges_Ci = []
    num_nodes_Ci = len(nodes_Ci)
    for idx_i in range(0, num_nodes_Ci):
        for idx_j in range(0, num_nodes_Ci):
            if(idx_i < idx_j): #Add each edge exactly once
                if(SM_orig[nodes_Ci[idx_i], nodes_Ci[idx_j]] > 0.0):
                    #Add edges with non zero and non -1 weight
                    primary_edges_Ci.append(SM_orig[nodes_Ci[idx_i], nodes_Ci[idx_j]])

    return primary_edges_Ci

