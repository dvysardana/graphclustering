__author__ = 'divya'

import numpy as np

from .P2_calc_CM import calculate_CM
from .P2_sort_CM import sort_CM

def MKNN_Phase2_init(CL_List, MKNN, num_nodes, num_clusters, log):

    #Task 1: Calculate CM
    (CM, OutreachM, ProjectionM, NumNodesM) = calculate_CM(CL_List, MKNN, num_nodes, num_clusters, log)


    #Converting some of the matrices to lists because they will need to be updated
    #frequently in phase 2

    CM_List = np.array(CM).tolist()
    OutreachM_List = np.array(OutreachM).tolist()
    ProjectionM_List = np.array(ProjectionM).tolist()
    NumNodesM_List = np.array(NumNodesM).tolist()


    #Task 2: Sort clusters by CM value
    #The sorted matrix has three columns, first two for the indices
    #and the last one for the CM value.

    CM_sort_List = sort_CM(CM_List, log)

    return (CM_List, CM_sort_List, OutreachM_List, ProjectionM_List, NumNodesM_List)
