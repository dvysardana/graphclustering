__author__ = 'divya'

import numpy as np
import pandas as pd
import logging

def init_read_expanded_SM(inp_filename_expanded_codes, num_nodes, log):

    #logger = log.get_logger(__name__)
    logger = logging.getLogger('root')
    logger.debug("Debugging from inside init_read_expanded_SM module")

    SMArray = np.zeros(shape=(num_nodes, num_nodes))

    print('reading the expanded relations file')
    exp_file_rels = pd.read_csv(
        filepath_or_buffer=inp_filename_expanded_codes,
        header=None,
        sep=' ')

    exp_file_rels.columns = ['node_code_1', 'node_code_2', 'edge_weight']

    for i in range(exp_file_rels.shape[0]):
        SMArray[exp_file_rels['node_code_1'][i],exp_file_rels['node_code_2'][i]] = exp_file_rels['edge_weight'][i]
        SMArray[exp_file_rels['node_code_2'][i], exp_file_rels['node_code_1'][i]] = exp_file_rels['edge_weight'][i]

    SM = np.matrix(SMArray, float)

    #set the diagonal elements of SM to 1
    SM = SM+np.matrix(np.identity(num_nodes), copy=False)

    return SM