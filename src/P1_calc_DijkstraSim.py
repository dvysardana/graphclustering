__author__ = 'divya'

import numpy as np
import logging

def dijkstra_imp(SM_n, source, Mapping_n, SM_expanded_array, log):

    #logger = log.get_logger(__name__)
    logger = logging.getLogger('root')
    logger.debug("Debugging from inside P1_calc_DijkstraSim module")

    num_nodes = int(SM_n.shape[0])


    # in SM convert all similarities to distances
    #Set adjacency distance matrix as 1-similarity matrix
    adjM = 1 - SM_n


    #Assign a temporary source
    s = source

    #Assign a set for all the nodes whose shortest distance from the source has
    #  been finalized
    list_found_nodes = [-1] * num_nodes;
    list_found_dist = [1] * num_nodes;

    #Assign a distance list dist (priority queue)
    list_nodes = list(range(0, num_nodes))
    #list_dist =  [adjM[s, n] for n in list_nodes]
    list_dist = [1] * num_nodes
    list_dist[s] = 0.0



    while abs(sum(list_dist)) != num_nodes:

        #Extract the node u with the minimum distance so far from the source, also save its distance u_dist
        sorted_nodes_dist = [[x, y] for (x, y) in sorted(zip(list_dist, list_nodes), key=lambda pair: pair[0])]
        u = sorted_nodes_dist[0][1]
        u_dist = sorted_nodes_dist[0][0]

        #u's shortest distance from the source is final, so add it in the found list
        list_found_dist[u] = u_dist
        list_found_nodes[u] = u


        #adjM

        a=[adjM[u, n] for n in range(0, num_nodes)]
        #Get the nodes adjacent to u
        u_adj = np.array(adjM[u, :]).flatten()
        u_adj_nodes_tmp = list(np.nonzero(u_adj != 1)[0])
        #7/9/15: Line below added to not include nodes for which shortest
        #distance has already been found.
        #u_adj_nodes = [x for x in u_adj_nodes if x not in list_found_nodes or u_adj_nodes.remove(x)]
        u_adj_nodes = [x for x in u_adj_nodes_tmp if x not in list_found_nodes]

        #u_adj_nodes = np.where(np.array(adjM[u,:]).flatten() != 1.0)[1].tolist()

        #u_adj_nodes_all = np.array(adjM[u,:]).tolist()[0]
        #u_adj_nodes = [i for i,e in enumerate(u_adj_nodes_all) if e!=1]

        for adj_node in u_adj_nodes:
            tmp_dist = u_dist + adjM[u, adj_node]
            if ( tmp_dist < list_dist[adj_node]):
            #adjM[s,adj_node] = tmp_dist
            #adjM[adj_node, s] = tmp_dist
                list_dist[adj_node] = tmp_dist

        #Remove s's distance from the list of all candidate nodes.
        list_dist[u] = 1  #a value to represent that the shortest distance to u has been found])


    #transfer all the shortest distances back to DM and then to SM
    #SM_expanded_array[s,:] = np.array([1-i for i in list_found_dist])

    for i in range(num_nodes):
        SM_expanded_array[Mapping_n[s], Mapping_n[i]] = 1 - list_found_dist[i]
        #SM_expanded_array[Mapping_n[i], Mapping_n[s]] = SM_expanded_array[Mapping_n[s], Mapping_n[i]]

    #SM_expanded_array[0,:]
    ########################

    # #expand SM upto k hops.
    # #expand the similarity matrix
    # for i in range(num_nodes):
    #     for j in range(num_nodes):
    #         if(i != j):
    #             max= SM[i,j]
    #             for k in range(num_nodes):
    #                 if(k!=i and k != j):
    #                     if(SM[i,k] != 0 and SM[k,j] != 0):
    #                         tmpSim = SM[i,k]*SM[k,j]
    #                         if(tmpSim > max):
    #                             max = tmpSim
    #                             SM[i,j] = max

    return SM_expanded_array
