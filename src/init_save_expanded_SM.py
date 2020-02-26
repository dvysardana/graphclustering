__author__ = 'divya'

import logging

def init_save_expanded_SM(SM, node_codes, num_nodes, inp_filename_expanded_codes, inp_filename_expanded_labels, log):

    #logger = log.get_logger(__name__)
    logger = logging.getLogger('root')
    logger.debug("Debugging from inside init_save_expanded_SM module")

    #3. Save the expanded SM(codes + labels file) for later use.
    target1 = open(inp_filename_expanded_codes, 'a')
    target2 = open(inp_filename_expanded_labels, 'a')

    for i in range(0, num_nodes):
        for j in range(0, num_nodes):
            if(i < j and SM[i, j] != -1 and SM[i, j] != 0):
                target1.write(str(i))
                target2.write(str(node_codes[i]))
                target1.write(" ")
                target2.write(" ")
                target1.write(str(j))
                target2.write(str(node_codes[j]))
                target1.write(" ")
                target2.write(" ")
                target1.write(str(SM[i, j]))
                target2.write(str(SM[i, j]))
                target1.write("\n")
                target2.write("\n")
