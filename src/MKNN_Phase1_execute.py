__author__ = 'divya'

import numpy as np
import logging

from .P1_transfer_cluster_membership import transfer_cluster
from .P1_check_primary_conn import check_primary

def MKNN_Phase1_execute(num_nodes, CI, K, MKNN, SM_orig, log):
    #logger = log.get_logger(__name__)
    logger = logging.getLogger('root')
    logger.debug("Debugging from inside MKNN_worker module")

    #Initialize matrices
    #Cluster label matrix
    CL = -1 * np.matrix(np.ones(shape = (num_nodes, 1)))
    #Cluster center matrix
    CC = -1 * np.matrix(np.ones(shape = (num_nodes, 1)))

    c_label = 0
    for i  in range(num_nodes):
        #i=4
        c_initiator = CI[i,0]
        print("Initiator:")
        print(c_initiator)

        if(CL[c_initiator, 0] == -1):
            #set the cluster initiator's own cluster label
            CL[c_initiator, 0] = c_label
            c_label_current = c_label
            c_label = c_label+1
            CC[c_initiator, 0] = c_initiator

            #Check cluster initiator's neighbors for cluster membership
            for j in range(K):
                #j=0
                c_initiator_MKNN = MKNN[c_initiator, j]
                print("MKNN neighbor:")
                print(c_initiator_MKNN)
                add_flag = -1

                if(c_initiator_MKNN != -1):
                    #Task 1: check for at least one primary connection with cluster
                    add_flag = check_primary(SM_orig, CL, c_initiator_MKNN, c_label_current,log)
                    #add_flag = 1 #This addition is to test the actual Zhen Hu's algorithm.
                    #It allows clusters to be formed with absolutely no primary connection among some nodes.
                    #Task2: if CL(c_initiator_MKNN) =-1, then good
                    #else SD comparison

                    if(add_flag == 0):
                        if(CL[c_initiator_MKNN, 0] == -1):
                            #the current MKNN neighbor does not belong to any cluster
                            #assign it the current cluster label
                            add_flag = 1
                        else:
                            #calculate percentage change in SD in going from one set to the other
                            #for both the set pairs

                            #compare the percentage change in SD for both the sets.
                            add_flag = transfer_cluster(SM_orig, CL, CC, c_initiator, c_initiator_MKNN, c_label_current, log)


                    if(add_flag == 1):
                        CL[c_initiator_MKNN, 0] = c_label_current
                        CC[c_initiator_MKNN, 0] = c_initiator

                #Task 3: if neighbor added sucessfully, neib of neib checking for addition.v

                #next: check for runtime error plus clustering results on very dummy matrix.

    #Phase 1 ends here
    ##############################################################################################
    return (CL, CC, c_label)
