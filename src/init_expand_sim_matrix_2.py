__author__ = 'divya'


import numpy as np
import logging

from .P1_get_n_hop_neighbors import get_n_hop_neighbors
from .P1_calc_DijkstraSim import dijkstra_imp

#This function extrapoles the matrix SM
#to generate all edges for upto nhops
def expand_SM_2(SM, nhops, log):

    #logger = log.get_logger(__name__)
    logger = logging.getLogger('root')
    logger.debug("Debugging from inside init_expand_sim_matrix_2 module")

    num_nodes = SM.shape[0]

    SM_expanded_array = np.zeros(shape = (num_nodes, num_nodes))

    #Calculate similarity upto  four hop neighbors for all the nodes in the graph
    for i in range(0, num_nodes):
        #source = i
        source=i
        #Get a four hop neighbor matrix SM_n for s along with a mapping matrix for all members of SM_n

        (SM_n, Mapping_n) = get_n_hop_neighbors(SM, source, nhops, log)

        #SM_n
        #Mapping_n

        #Apply Dijkstra algorithm on the matrix generated above to update the
        #similarities/distances
        SM_expanded_array = dijkstra_imp(SM_n, np.where(Mapping_n==source)[0][0], Mapping_n, SM_expanded_array, log)


    return np.matrix(SM_expanded_array)