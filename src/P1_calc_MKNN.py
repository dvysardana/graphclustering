__author__ = 'divya'

import numpy as np
import logging

def calculate_MKNN(SM, num_nodes, K, log):


    #logger = log.get_logger(__name__)
    logger = logging.getLogger('root')
    logger.debug("Debugging from inside P1_calc_MKNN module")

    #Initialize the MKNN matrix
    MKNN = np.ones(shape=(num_nodes, K)) * -1

    SM.shape

    #Flatten the SM matrix into another edges x 1 matrix
    SM_flat= SM.flatten()
    SM_flat.shape


    #concatenate the flattened SM with Edge indices
    num_dir_edges = SM_flat.shape[1]
    x = np.array(list(range(num_nodes)), dtype=int).reshape(num_nodes, 1)

    for i in range(num_nodes):
        y= np.ones((num_nodes,1)) * i
        z = np.concatenate((y,x), axis=1)
        z.shape
        if i==0:
            final = z
        else:
            final = np.concatenate((final,z), axis=0)

    EI = np.matrix(final, float)

    SM_flat_EI = np.concatenate((EI, SM_flat.T), axis=1)


    #Sort SM as per column col
    col = 2
    SM_sort = SM_flat_EI[np.array(SM_flat_EI[:,col].argsort(axis=0)[::-1].tolist()).ravel()]

    #Iterate over sorted SM to find MKNN neighbors
    for i in range(num_dir_edges):
        row = SM_sort[i,0]
        col = SM_sort[i,1]
        edge_weight = SM_sort[i,2]

        if(row < col and edge_weight != 0):
            #check if valid row column and edge weight values
            if( -1 in list(MKNN[row,:]) and -1 in list(MKNN[col,:])):
                idx_row = list(MKNN[row,:]).index(-1)
                idx_col = list(MKNN[col,:]).index(-1)
                MKNN[row, idx_row] = col
                MKNN[col, idx_col] = row

    return np.matrix(MKNN)