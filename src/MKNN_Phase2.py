__author__ = 'divya'

from .MKNN_Phase2_init import MKNN_Phase2_init
from .MKNN_Phase2_execute import MKNN_Phase2_execute

def MKNN_Phase2(CL_List, MKNN, num_nodes, c_label, num_clusters, LIMIT_CLUSTERS, log):

    #########################
    #Initialization of Phase2:
    #Task1: Calculate CM and other matrices
    #Task2: Sort CM
    ######################
    (CM_List, CM_sort_List, OutreachM_List, ProjectionM_List, NumNodesM_List) = MKNN_Phase2_init(CL_List, MKNN, num_nodes, num_clusters, log)



    #Task 3: Merge nodes based upon CM values until a number M of clusters is
    #reached, or there is no connectivity left among the nodes of the graph.
    #Subtask: Update CM values after each merge.
    (CL_List, num_clusters) = MKNN_Phase2_execute(CM_List, CM_sort_List, NumNodesM_List, ProjectionM_List, OutreachM_List, CL_List, c_label, num_clusters, LIMIT_CLUSTERS, log)


    return (CL_List, num_clusters)