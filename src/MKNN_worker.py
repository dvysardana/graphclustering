__author__ = 'divya'

import logging

from .MKNN_Phase1 import MKNN_Phase1
from .MKNN_Phase2 import MKNN_Phase2
from .MKNN_visualize import MKNN_visualize

def MKNN_worker(K, LIMIT_CLUSTERS, SM, SM_orig, num_nodes, node_codes, currentdate_str, dataset_name, eval_results_dir, log):



    #logger = log.get_logger(__name__)
    logger = logging.getLogger('root')
    logger.debug("Debugging from inside MKNN_worker module")


    #####################
    # a = np.zeros(shape=(6,6))
    # a[0,0] = 1
    # a[0,1] = 0.9
    # a[1,1] = 1
    # a[1,0] = 0.9
    # a[1,3] = 0.8
    # a[1,5] = 0.8
    # a[2,2] = 1
    # a[2,3] = 0.9
    # a[2,4] = 0.8
    # a[2,5] = 0.7
    # a[3,3] = 1
    # a[3,1] = 0.8
    # a[3,2] = 0.9
    # a[4,4] = 1
    # a[4,2] = 0.8
    # a[5,5] = 1
    # a[5,1] = 0.8
    # a[5,2] = 0.7


    # a[0,0] = 1
    # a[0,1] = 0.7
    # a[1,1] = 1
    # a[1,0] = 0.9
    # a[1,3] = 0.8
    # a[1,5] = 0.9
    # a[2,2] = 1
    # a[2,3] = 0.9
    # a[2,4] = 0.7
    # a[2,5] = 0.9
    # a[3,3] = 1
    # a[3,1] = 0.8
    # a[3,2] = 0.9
    # a[4,4] = 1
    # a[4,2] = 0.8
    # a[5,5] = 1
    # a[5,1] = 0.8
    # a[5,2] = 0.7



    #SM = np.matrix(a)
    #####################
    #Phase 1
    ##########################
    (CL_List, num_clusters, MKNN, c_label) = MKNN_Phase1(SM, SM_orig, num_nodes, node_codes, K, log)

    #############################################################
    #Printing and Visualization/Evaluation steps between Phase 1 and 2 begin
    #############################################################
    MKNN_visualize(CL_List, num_clusters, SM, SM_orig, num_nodes, node_codes, K, currentdate_str, dataset_name, eval_results_dir,1, log)

    #save this CL and num_clusters for later use
    CL_List_P1 = list(CL_List)
    num_clusters_P1 = num_clusters

    ##################################
    #Evaluation after phase 1 ends
    ##################################

    #######################################################
    #Phase two implementation of Zhen Hu's MKNN algorithm
    #######################################################

    (CL_List, num_clusters) = MKNN_Phase2(CL_List, MKNN, num_nodes, c_label, num_clusters, LIMIT_CLUSTERS, log)

    ########################################
    #Visualization of clusters after phase 2
    ########################################

    MKNN_visualize(CL_List, num_clusters, SM, SM_orig, num_nodes, node_codes, K, currentdate_str, dataset_name, eval_results_dir, 2 , log)

    return (CL_List, CL_List_P1, SM, SM_orig, num_clusters, num_clusters_P1, num_nodes)