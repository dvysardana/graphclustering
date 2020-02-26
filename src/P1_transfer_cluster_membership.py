__author__ = 'divya'


import numpy as np
import logging
from .P1_calc_std_node_set import calculate_std_node_set

#function to calculate the set of edges between two sets
def transfer_cluster(SM_orig, CL, CC, c_initiator, c_initiator_MKNN, c_label_current, log):

    #logger = log.get_logger(__name__)
    logger = logging.getLogger('root')
    logger.debug("Debugging from inside P1_transfer_cluster_membership module")

    add_flag = 0
    #the current MKNN neighbor belongs to an existing cluster
    #comapare the variance
    c_label_other = CL[c_initiator_MKNN, 0]
    #c_label_other = -1

    c_center_other = CC[c_initiator_MKNN, 0]
    c_center_current = c_initiator

    #make the four sets
    c_members_other = np.where(CL[:]==c_label_other)[0].T
    c_members_current = np.where(CL[:]==c_label_current)[0].T
    c_members_current_proposed = np.concatenate((c_members_current, [[int(c_initiator_MKNN)]]), axis=0, )
    c_members_other_proposed = c_members_other[c_members_other != c_initiator_MKNN].T

    #calculate Standard deviation of edges in each set
    SD_other = calculate_std_node_set(SM_orig, c_members_other, log)
    SD_current = calculate_std_node_set(SM_orig, c_members_current, log)
    SD_current_proposed = calculate_std_node_set(SM_orig, c_members_current_proposed, log)
    SD_other_proposed = calculate_std_node_set(SM_orig, c_members_other_proposed, log)

    #calculate and compare the change in Standard Deviation
    if(c_members_current.shape[0] != 1 and c_members_other_proposed.shape[0] != 1):
        change_SD_current = abs(SD_current_proposed - SD_current)
        change_SD_other = abs(SD_other - SD_other_proposed)
        if(change_SD_current < change_SD_other):
            #do the transfer of cluster membership
            add_flag = 1
            #CL[c_initiator_MKNN, 0] = c_label_current
            #CC[c_initiator_MKNN, 0] = c_initiator

    return add_flag
