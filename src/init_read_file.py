__author__ = 'divya'


import pandas as pd
import numpy as np
import logging

class read_rel_file:


    node_codes = []
    num_nodes = 0
    file_name =""

    def __init__(self, filename):
        self.file_name = filename

    def read_file(self, log):
        #logger = log.get_logger(__name__)
        logger = logging.getLogger('root')
        logger.debug("Debugging from inside init_read_file module")

        ###########################
        # Read the relations file
        ###########################

        #self.file_name = filename
        print('reading relations file')
        file_rels = pd.read_csv(
            filepath_or_buffer= self.file_name,
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

            if node_codes.__contains__(str(file_rels['node1'][i])):
                print((str(i) + ":" + str(file_rels['node1'][i]) +
                      str(node_codes.index(str(file_rels['node1'][i])))))
            else:
                node_codes.append(str(file_rels['node1'][i]))

            if node_codes.__contains__(str(file_rels['node2'][i])):
                print((str(i) + ":" + str(file_rels['node2'][i]) +
                      str(node_codes.index(str(file_rels['node2'][i])))))
            else:
                node_codes.append(str(file_rels['node2'][i]))

        for i in node_codes:
            print((i + ":" + str(node_codes.index(i))))

        self.node_codes = node_codes

        numNodes = len(node_codes)
        self.num_nodes = numNodes

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


        SM = SM+np.matrix(np.identity(numNodes), copy=False)
        return SM

