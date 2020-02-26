__author__ = 'divya'

import numpy as np
import logging

def get_n_hop_neighbors(SM, source, nhops, log):

    #logger = log.get_logger(__name__)
    logger = logging.getLogger('root')
    logger.debug("Debugging from inside P1_get_n_hop_neighbors module")

    num_nodes  = nhops+1

    #Generate a mapping for all neighbors to 0,1,2,,3,...
    neighbors = []
    temp = []
    allNeighbors = []
    #allNeighbors.append(source)
    node = source
    neighbors += np.array(np.nonzero(SM[node,:])[1]).tolist()[0]
    allNeighbors += neighbors

    hop =1
    while (hop <= nhops):
        for neighbor in neighbors:
            temp = union(temp,np.array(np.nonzero(SM[neighbor,:])[1]).tolist()[0])
        allNeighbors = union(allNeighbors,temp)
        neighbors = temp
        hop = hop +1
        temp = []

    #Get all similarities to 4 hop neighbors inside an array
    m=0
    n=0
    Mapping_n = np.array(allNeighbors)
    SM_n = np.zeros(shape= (len(allNeighbors), len(allNeighbors)))
    for i in allNeighbors:
        for j in allNeighbors:
            SM_n[m,n] = SM[i,j]
            #print(i)
            #print(j)
            n=n+1

        m=m+1
        n=0

    return (SM_n, Mapping_n)


def union(a, b):
    """ return the union of two lists """
    return list(set(a) | set(b))