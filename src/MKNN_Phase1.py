__author__ = 'divya'

from .MKNN_Phase1_execute import MKNN_Phase1_execute
from .MKNN_Phase1_init import MKNN_Phase1_init
from .helper_convertObjects import getListfromnpArray
from .helper_calculate import calcNumClusters

def MKNN_Phase1(SM, SM_orig, num_nodes, node_codes, K, log):

    ##############################
    #Phase 1 Initialization begins
    ##############################
    (MKNN, Deg, MKNN_rad, CI) = MKNN_Phase1_init(SM, SM_orig, num_nodes, K, log)

    ############################
    #Phase 1 Initialization ends
    ############################

    ############################
    #Execution of Phase 1 begins
    ############################

    (CL, CC, c_label) = MKNN_Phase1_execute(num_nodes, CI, K, MKNN, SM_orig, log)

    ##########################
    #Execution of Phase 1 ends
    ##########################

    #Prepare return variables
    CL_List = getListfromnpArray(CL)
    num_clusters = calcNumClusters(CL_List, num_nodes, node_codes)

    return (CL_List, num_clusters, MKNN, c_label)