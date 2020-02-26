__author__ = 'divya'

import numpy as np
import logging
from .P2_isLinked import is_Linked
from .P2_isMKNN import is_MKNN

def calculate_CM(CL_List, MKNN, num_nodes, num_clusters, log):

    #logger = log.get_logger(__name__)
    logger = logging.getLogger('root')
    logger.debug("Debugging from inside P2_calc_CM module")

    CL_List
    #Initialize CM
    CM =  -1 * np.matrix(np.ones(shape = (num_clusters, num_clusters)))
    OutreachM = -1 * np.matrix(np.ones(shape = (num_clusters, num_clusters)))
    ProjectionM = -1 * np.matrix(np.ones(shape = (num_clusters, num_clusters)))
    NumNodesM = -1 * np.matrix(np.ones(shape = (num_clusters, 1)))

    #For each cluster, calculate
    #1. Number of points belonging to the cluster



    #For each pair of clusters, calculate the following:
    #Projection
    #Outreach
    #Connectivity value
    for i in range(0, num_clusters):

        #Get nodes belonging to cluster Ci
        nodes_Ci = [x for x in range(0, num_nodes) if CL_List[x] == i]

        #store the number of nodes in Ci
        NumNodesM[i] = len(nodes_Ci)

        for j in range(0, num_clusters):

            #i=1;
            #j=2;
            projectionij_count = 0
            projectionji_count = 0
            outreachij_count = 0
            iteration_no = 1

            if i<j:
                #Get nodes belonging to cluster Cj
                nodes_Cj = [x for x in range (0, num_nodes) if CL_List[x] == j]

                #store the number of nodes in Cj
                NumNodesM[j] = len(nodes_Cj)

                for node_i in nodes_Ci:
                    projectionij_count = projectionij_count + is_Linked(node_i, nodes_Cj, MKNN, log)
                    for node_j in nodes_Cj:
                        if iteration_no == 1:
                            projectionji_count = projectionji_count + is_Linked(node_j, nodes_Ci, MKNN, log)

                        outreachij_count = outreachij_count + is_MKNN(node_i, node_j, MKNN, log)

                    iteration_no = -1

                ProjectionM[i,j] = projectionij_count
                ProjectionM[j,i] = projectionji_count
                OutreachM[i,j] = outreachij_count
                OutreachM[j,i] = outreachij_count


                CM[i,j] = (float)(OutreachM[i,j] * ProjectionM[i,j])/ (float)(NumNodesM[i] * NumNodesM[i] * NumNodesM[j])
                CM[j,i] = (float)(OutreachM[i,j] * ProjectionM[j,i])/ (float)(NumNodesM[i] * NumNodesM[j] * NumNodesM[j])

            elif i==j:
                #Leaving all diagonal values to be equal to -1 for now.
                CM

        #CM[i,j] = (OutreachM[i,j] * ProjectionM[i,j])/ (NumNodesM[i] * NumNodesM[i] * NumNodesM[j])
        #CM[j,i] = (OutreachM[i,j] * ProjectionM[j,i])/ (NumNodesM[i] * NumNodesM[j] * NumNodesM[j])


    CM
    OutreachM
    ProjectionM
    NumNodesM

    return (CM, OutreachM, ProjectionM, NumNodesM)