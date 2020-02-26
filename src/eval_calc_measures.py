__author__ = 'divya'

from .eval_getPrimaryEdges import getPrimaryEdges
import logging


def eval_calc_measures(CL_List, SM, SM_orig, num_clusters, num_nodes, log):


    #For each clusters, calculate the following evaluation measures:
    #1. Structural Density
    #2. Standard Deviation of Primary Edge Weights
    #Other cluster statistics:
    #num_clusters
    #min_cluster_size
    #max_cluster_size
    #Average variance (play with average or something else if possible)
    #Average structural density

    CL_List_unique = list(set(CL_List))
    Mean_List = []
    Variance_List = []
    Struct_Density_List = []
    Node_Count_List = []

    #logger = log.get_logger(__name__)
    logger = logging.getLogger('root')
    logger.debug("Debugging from inside eval_calc_measures module")


    for i in CL_List_unique:
        #i=32
        #Get nodes belonging to cluster Ci
        nodes_Ci = [x for x in range(0, num_nodes) if CL_List[x] == i]

        primary_edges_Ci = getPrimaryEdges(nodes_Ci, SM_orig, log)
        num_nodes_Ci = len(nodes_Ci)
        num_primary_edges_Ci = len(primary_edges_Ci)
        num_possible_edges_Ci = ((num_nodes_Ci) * (num_nodes_Ci-1))/2

        if num_possible_edges_Ci != 0: #Could be 0 if there is only one node in the cluster
            struct_density_Ci = (float)(num_primary_edges_Ci)/ (float)(num_possible_edges_Ci)
        else:
            struct_density_Ci = 0

        mean_Ci = (float)(sum(primary_edges_Ci)/ num_primary_edges_Ci) if num_primary_edges_Ci > 0 else float('nan')

        variance_Ci_Num_List = [((x-mean_Ci)*(x-mean_Ci))for x in range(0, num_primary_edges_Ci)]

        variance_Ci = (float)(sum(variance_Ci_Num_List))/ (float)(num_primary_edges_Ci * num_primary_edges_Ci) if num_primary_edges_Ci > 0 else float('nan')

        Mean_List.append(mean_Ci)
        Variance_List.append(variance_Ci)
        Struct_Density_List.append(struct_density_Ci)
        Node_Count_List.append(num_nodes_Ci)

    return (Mean_List, Variance_List, Struct_Density_List, Node_Count_List)


