__author__ = 'divya'

import pandas as pd
import numpy as np
import logging

def read_file(filename, log):
    ###########################
    # Read the relations file
    ###########################

    #logger = log.get_logger(__name__)
    logger = logging.getLogger('root')
    logger.debug("Debugging from inside init_readFile module")


    print('reading relations file')
    file_rels = pd.read_csv(
        filepath_or_buffer=filename,
        header=None,
        sep=' ')

    file_rels.columns = ['node1', 'node2', 'edge_weight']


    #file_rels.head()

    #################################################################
    #Iterate through file to count number of nodes and generate codes
    #################################################################


    node_codes = []

    for i in range(file_rels.shape[0]):
        ## print(A2Z_rels['edge_weight'][:i])
        # print(file_rels[['edge_weight', 'node1', 'node2']][:i])

        if node_codes.__contains__(file_rels['node1'][i]):
            print((str(i) + ":" + file_rels['node1'][i] +
                  str(node_codes.index(str(file_rels['node1'][i])))))
        else:
            node_codes.append(file_rels['node1'][i])

        if node_codes.__contains__(file_rels['node2'][i]):
            print((str(i) + ":" + file_rels['node2'][i] +
                  str(node_codes.index(str(file_rels['node2'][i])))))
        else:
            node_codes.append(file_rels['node2'][i])

    for i in node_codes:
        print((i + ":" + str(node_codes.index(i))))

    numNodes = len(node_codes)

    ##############################################################
    #Iterate through file again to create a numpy array and matrix
    ##############################################################


    SMArray = np.zeros(shape=(numNodes, numNodes))

    for i in range(file_rels.shape[0]):
        code1 = node_codes.index(str(file_rels['node1'][i]))
        code2 = node_codes.index(str(file_rels['node2'][i]))
        edge_weight = file_rels['edge_weight'][i]
        SMArray[code1, code2] = edge_weight
        SMArray[code2, code1] = edge_weight

    SM = np.matrix(SMArray, float)

    ##################
    #serializing data
    ##################

    s = SM.tostring()

    #set the diagonal elements to 1
    SM = SM+np.matrix(np.identity(numNodes), copy=False)
    return SM

    #next task: 1. set SM[i,i] = 1, 2. expand the matrix