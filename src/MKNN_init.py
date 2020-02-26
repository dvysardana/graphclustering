__author__ = 'divya'

import os
import datetime
import logging
import pandas as pd
import numpy as np

from .init_read_file import read_rel_file
from .init_read_expanded_SM import init_read_expanded_SM
from .init_expand_sim_matrix_2 import expand_SM_2
from .init_save_expanded_SM import init_save_expanded_SM

def MKNN_init(inp_filename, nhops, log):

    ##########################################
    #Get the filenames for:
    #1. input relationships file
    #2. expanded relationships file
    #########################################
    #logger = log.get_logger(__name__)
    logger = logging.getLogger('root')
    logger.debug("Debugging from inside init_setup module")

    print("Reading the input relationships file to create SM_orig and save node codes")

    #Get input file name
    #inp_filename = init_getfilename()

    #Generate the name of this expanded input file programmatically
    # based upon inp_filename
    #This file is generated only the very first time for a dataset
    #Two files are generated
    #1. One relationship file with only codes
    #2. One relationship file with labels (in case we need to plot the expanded matrix)
    inp_filename_expanded_codes = os.path.split(inp_filename)[0] + "/expanded/" + os.path.split(inp_filename)[1].split(".")[0] + "_expanded_codes.txt"
    inp_filename_expanded_labels = os.path.split(inp_filename)[0] + "/expanded/" + os.path.split(inp_filename)[1].split(".")[0] + "_expanded_labels.txt"


    ################################################################
    #Read the file inp_filename to get the similarity matrix SM_orig
    ################################################################

    #SM = read_file(inp_file)
    rd = read_rel_file(inp_filename)
    rd.file_name
    SM = rd.read_file(log)
    num_nodes = rd.num_nodes
    node_codes = rd.node_codes

    #A step only for testing G-MKNN running on nearly
    # unweighted graphs
    #SM = misc_SM_add_unweighted(100, SM, num_nodes, 0.5)

    #Make a copy of SM before expanding it.
    SM_orig = SM.copy()

    num_nodes = int(SM.shape[0])

    print("Input file read and matrix SM_orig created.")

    print("Matrix expansion begins.")

    ##################################################
    #Expansion of SM or reading of already expanded SM
    ##################################################

    #Check for the existence of expanded file
    #if the expanded file already exists, read it,
    if(os.path.isfile(inp_filename_expanded_codes)):
        #1. Read SM from the saved expanded file.
        print("The expanded matrix is already stored in a file, reading it.")
        SM = init_read_expanded_SM(inp_filename_expanded_codes, num_nodes, log)
        print("Expanded matrix read into SM.")
    else:
        #else, call the function to expand the matrix
        #and also save the expanded matrix for later use.
        # 1. Expand SM
        starttime = datetime.datetime.now()
        print(starttime)
        print("Expand the matrix to calculate paths for nodes upto 4 hops away.")
        #matrix expansion using Djikstra's algorithm
        SM = expand_SM_2(SM, nhops, log)
        print("Matrix expanded to create SM.")
        endtime = datetime.datetime.now()
        print(endtime)

        print("Save the expanded matrix as a file for later use.")
        #2. Save the expanded SM(codes + labels file) for later use.
        init_save_expanded_SM(SM, node_codes, num_nodes, inp_filename_expanded_codes, inp_filename_expanded_labels, log)
        print("Expanded matrix SM saved as a relationship file.")

    #SM = expand_SM_2(SM, nhops, log)

    print("Matrix expansion finishes.")

    return (SM_orig, SM, num_nodes, node_codes)
