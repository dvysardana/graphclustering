__author__ = 'divya'

import numpy as np
import pandas as pd

import os
import datetime
import logging

from MKNN_Helper import MKNN_Helper
from NodeData import NodeData
from EdgeData import EdgeData
from EdgeData import EdgeType

############################################
#Class to hold data related to graph that is
#an input to the clustering algorithm
###########################################
class GraphData(object):
    # K
    # SM
    # numNodes
    # MKNN
    # CL_P1
    # CL_p2
    # CPStatus
    # numClusters

    def __init__(self):
        self.num_nodes = 0
        self.isDirty = True #to check if num_nodes has been calculated or not
        self.node_codes = []
        self.SM = np.matrix(np.identity(self.num_nodes), copy=False)
        self.SM_orig = np.matrix(np.identity(self.num_nodes), copy=False)
        self.logger = None
        self.helper = MKNN_Helper()

        #Dictionaries to save nodes and edges
        self.node_dict = {} #Dictionary containing node_ids along with their objects
        self.edge_dict = {} #Dictionary containing edge ids alongs with their objects
        self.next_available_edge_id = 0

        #Global graph measures
        self.graph_struct_density = 0.0
        self.graph_std = 0.0

    #set up logger
    def set_logger(self):
        #self.logger = logger
        self.logger = logging.getLogger('root')

    #create the graph similarity matrix by reading the input relationship file
    def create_SM_from_relfile(self, inp_rel_filename):

        self.set_logger()

        self.logger.info("Reading the input relationships file to create SM_orig and save node codes")

        ###########################
        # Read the relations file
        ###########################
        file_rels = pd.read_csv(
            filepath_or_buffer= inp_rel_filename,
            header=None,
            sep=' ')

        file_rels.columns = ['node1', 'node2', 'edge_weight']


        #file_rels.head()

        #################################################################
        #Iterate through file to count number of nodes and generate codes
        #################################################################


        self.node_codes = []

        for i in range(file_rels.shape[0]):
            ## print(A2Z_rels['edge_weight'][:i])
            #print(file_rels[['edge_weight', 'node1', 'node2']][:i])

            if self.node_codes.__contains__(str(file_rels['node1'][i])):
                pass
                #print(str(i) + ":" + str(file_rels['node1'][i]) +
                #      str(self.node_codes.index(str(file_rels['node1'][i]))))
            else:
                self.node_codes.append(str(file_rels['node1'][i]))

            if self.node_codes.__contains__(str(file_rels['node2'][i])):
                pass
                #print(str(i) + ":" + str(file_rels['node2'][i]) +
                #      str(self.node_codes.index(str(file_rels['node2'][i]))))
            else:
                self.node_codes.append(str(file_rels['node2'][i]))

        self.logger.debug("Printing node codes:")
        for i in self.node_codes:
            self.logger.debug(i + ":" + str(self.node_codes.index(i)))


        self.calculate_num_nodes()

        ##############################################################
        #Iterate through file again to create a numpy array and matrix
        ##############################################################


        SMArray = np.zeros(shape=(self.num_nodes, self.num_nodes))

        for i in range(file_rels.shape[0]):
            code1 = self.node_codes.index(str(file_rels['node1'][i]))
            code2 = self.node_codes.index(str(file_rels['node2'][i]))
            edge_weight = file_rels['edge_weight'][i]
            SMArray[code1, code2] = edge_weight
            SMArray[code2, code1] = edge_weight

            #create nodedata objects for code1 and code if they don't exist
            self.create_node(code1, self.node_codes[code1])
            self.create_node(code2, self.node_codes[code2])

            #create edgedata object for the edge between code1 and code2
           # self.create_edge(code1, code2, edge_weight, EdgeType.primary)

        self.SM = np.matrix(SMArray, float)

        self.SM = self.SM+np.matrix(np.identity(self.num_nodes), copy=False)

        #Make a copy of SM before expanding it.
        self.save_SM_before_expansion()

        #Calculate graph global measures (use for small graphs only)
        #NOTE: Check the method for correctness before using it.
        #self.calculate_graph_global_measures()

        self.logger.info("Input file read and matrix SM_orig created.")

    #######################################################################
    #Calculate the number of nodes based upon the length of node_codes list
    #######################################################################
    def calculate_num_nodes(self):
        self.num_nodes = len(self.node_codes)
        self.isDirty = False

    ########################################
    #Make a copy of SM and save in SM_orig
    ########################################
    def save_SM_before_expansion(self):
        self.SM_orig = self.SM.copy()

    #######################################################
    #Expand SM based upon the nhops
    ########################################################
    def setup_expanded_SM(self, nhops, inp_rel_filename):
        self.logger.info("Matrix expansion begins.")

        #Read the names for expanded input relationship file
        inp_filename_expanded_codes = os.path.split(inp_rel_filename)[0] + "/expanded/" + os.path.split(inp_rel_filename)[1].split(".")[0] + "_expanded_codes.txt"
        inp_filename_expanded_labels = os.path.split(inp_rel_filename)[0] + "/expanded/" + os.path.split(inp_rel_filename)[1].split(".")[0] + "_expanded_labels.txt"
        inp_filename_node_codes = os.path.split(inp_rel_filename)[0] + "/expanded/" + os.path.split(inp_rel_filename)[1].split(".")[0] + "_node_codes.txt"


        #Expansion of SM or reading of already expanded SM

        #Check for the existence of expanded file
        #if the expanded file already exists, read it,
        if(os.path.isfile(inp_filename_expanded_codes)):
            #1. Read SM from the saved expanded file.
            self.logger.debug("The expanded matrix is already stored in a file, reading it.")
            self.read_expanded_SM(inp_filename_expanded_codes)
            self.logger.debug("Expanded matrix read into SM.")
        else:
            #else, call the function to expand the matrix
            #and also save the expanded matrix for later use.
            # 1. Expand SM
            starttime = datetime.datetime.now()
            self.logger.debug(starttime)
            self.logger.debug("Expand the matrix to calculate paths for nodes upto 4 hops away.")
            #matrix expansion using Djikstra's algorithm
            self.expand_SM(nhops)
            self.logger.debug("Matrix expanded to create SM.")
            endtime = datetime.datetime.now()
            self.logger.debug(endtime)

            self.logger.debug("Save the expanded matrix as a file for later use.")
            #2. Save the expanded SM(codes + labels file) for later use.
            self.save_expanded_SM(inp_filename_expanded_codes, inp_filename_expanded_labels, inp_filename_node_codes)
            self.logger.debug("Expanded matrix SM saved as a relationship file.")

        self.logger.info("Matrix expansion finishes.")

    ########################################################
    #Read already expanded and stored SM
    #######################################################
    def read_expanded_SM(self, inp_filename_expanded_codes):
        self.logger.debug("Debugging from inside read_expanded_SM method")

        SMArray = np.zeros(shape=(self.num_nodes, self.num_nodes))

        self.logger.info('reading the expanded relations file')
        exp_file_rels = pd.read_csv(
            filepath_or_buffer=inp_filename_expanded_codes,
            header=None,
            sep=' ')

        exp_file_rels.columns = ['node_code_1', 'node_code_2', 'edge_weight']

        for i in range(exp_file_rels.shape[0]):
            SMArray[exp_file_rels['node_code_1'][i],exp_file_rels['node_code_2'][i]] = exp_file_rels['edge_weight'][i]
            SMArray[exp_file_rels['node_code_2'][i], exp_file_rels['node_code_1'][i]] = exp_file_rels['edge_weight'][i]

        self.SM = np.matrix(SMArray, float)

        #set the diagonal elements of SM to 1
        self.SM = self.SM+np.matrix(np.identity(self.num_nodes), copy=False)

    ##########################################################
    #Expand SM (using Dijkstra algorithm)
    #########################################################
    def expand_SM(self, nhops):

        self.logger.debug("Debugging from inside init_expand_sim_matrix_2 module")

        SM_expanded_array = np.zeros(shape = (self.num_nodes, self.num_nodes))

        #Calculate similarity upto  four hop neighbors for all the nodes in the graph
        for i in range(0, self.num_nodes):
            #source = i
            source=i
            #Get a four hop neighbor matrix SM_n for s along with a mapping matrix for all members of SM_n

            (SM_n, Mapping_n) = self.get_n_hop_neighbors(source, nhops)

            #SM_n
            #Mapping_n

            #Apply Dijkstra algorithm on the matrix generated above to update the
            #similarities/distances
            SM_expanded_array = self.dijkstra_imp(SM_n, np.where(Mapping_n==source)[0][0], Mapping_n, SM_expanded_array)

        self.SM = np.matrix(SM_expanded_array)

    #######################################################################
    #Save the expanded SM into a file for later use
    ######################################################################
    def save_expanded_SM(self, inp_filename_expanded_codes, inp_filename_expanded_labels, inp_filename_node_codes):
        #logger = log.get_logger(__name__)
        logger = logging.getLogger('root')
        logger.debug("Debugging from inside init_save_expanded_SM module")

        #3. Save the expanded SM(codes + labels file) for later use.
        target1 = open(inp_filename_expanded_codes, 'a')
        target2 = open(inp_filename_expanded_labels, 'a')
        target3 = open(inp_filename_node_codes, 'a')

        for i in range(0, self.num_nodes):
            target3.write(str(i))
            target3.write(" ")
            target3.write(str(self.node_codes[i]))
            target3.write("\n")
            for j in range(0, self.num_nodes):
                if(i < j and self.SM[i, j] != -1 and self.SM[i, j] != 0):
                    target1.write(str(i))
                    target2.write(str(self.node_codes[i]))
                    target1.write(" ")
                    target2.write(" ")
                    target1.write(str(j))
                    target2.write(str(self.node_codes[j]))
                    target1.write(" ")
                    target2.write(" ")
                    target1.write(str(self.SM[i, j]))
                    target2.write(str(self.SM[i, j]))
                    target1.write("\n")
                    target2.write("\n")


    ###########################################################
    #Get nhop neighbors for a source node in SM
    ###########################################################
    def get_n_hop_neighbors(self, source, nhops):
        self.logger.debug("Debugging from inside P1_get_n_hop_neighbors module")

        #num_nodes_nhops  = nhops+1

        #Generate a mapping for all neighbors to 0,1,2,,3,...
        neighbors = []
        temp = []
        allNeighbors = []
        #allNeighbors.append(source)
        node = source
        neighbors += np.array(np.nonzero(self.SM[node,:])[1]).tolist()
        allNeighbors += neighbors

        hop =1
        while (hop <= nhops):
            for neighbor in neighbors:
                temp = self.helper.union(temp,np.array(np.nonzero(self.SM[neighbor,:])[1]).tolist())
            allNeighbors = self.helper.union(allNeighbors,temp)
            neighbors = temp
            hop = hop +1
            temp = []

        #Get all similarities to 4 hop neighbors inside an array
        m=0
        n=0
        Mapping_n = np.array(allNeighbors)
        SM_n = np.zeros(shape= (len(allNeighbors), len(allNeighbors)))
        for i in allNeighbors:
            for j in allNeighbors:
                SM_n[m,n] = self.SM[i,j]
                #print(i)
                #print(j)
                n=n+1

            m=m+1
            n=0

        return (SM_n, Mapping_n)


    # ###########################################################
    # #Get nhop neighbors for a source node in SM
    # ###########################################################
    # def get_n_hop_neighbors(self, source, nhops):
    #     self.logger.debug("Debugging from inside P1_get_n_hop_neighbors module")
    #
    #     #num_nodes_nhops  = nhops+1
    #
    #     #Generate a mapping for all neighbors to 0,1,2,,3,...
    #     neighbors = []
    #     temp = []
    #     allNeighbors = []
    #     #allNeighbors.append(source)
    #     node = source
    #     print(str(node))
    #     print(str(self.SM[node,:]))
    #     print(str(np.array(np.nonzero(self.SM[node,:])[1]).tolist()[0]))
    #     neighbors += np.array(np.nonzero(self.SM[node,:])[1]).tolist()[0]
    #     allNeighbors += neighbors
    #
    #     hop =1
    #     while (hop <= nhops):
    #         for neighbor in neighbors:
    #             temp = self.helper.union(temp,np.array(np.nonzero(self.SM[neighbor,:])[1]).tolist()[0])
    #         allNeighbors = self.helper.union(allNeighbors,temp)
    #         neighbors = temp
    #         hop = hop +1
    #         temp = []
    #
    #     #Get all similarities to 4 hop neighbors inside an array
    #     m=0
    #     n=0
    #     Mapping_n = np.array(allNeighbors)
    #     SM_n = np.zeros(shape= (len(allNeighbors), len(allNeighbors)))
    #     for i in allNeighbors:
    #         for j in allNeighbors:
    #             SM_n[m,n] = self.SM[i,j]
    #             #print(i)
    #             #print(j)
    #             n=n+1
    #
    #         m=m+1
    #         n=0
    #
    #     return (SM_n, Mapping_n)


    #############################################################
    #Implementation of Dijkstra algorithm in order to expand SM
    #############################################################
    def dijkstra_imp(self, SM_n, source, Mapping_n, SM_expanded_array):
        self.logger.debug("Debugging from inside P1_calc_DijkstraSim module")

        num_nodes_nhops = int(SM_n.shape[0])


        # in SM convert all similarities to distances
        #Set adjacency distance matrix as 1-similarity matrix
        adjM = 1 - SM_n


        #Assign a temporary source
        s = source

        #Assign a set for all the nodes whose shortest distance from the source has
        #  been finalized
        list_found_nodes = [-1] * num_nodes_nhops;
        list_found_dist = [1] * num_nodes_nhops;

        #Assign a distance list dist (priority queue)
        list_nodes = list(range(0, num_nodes_nhops))
        #list_dist =  [adjM[s, n] for n in list_nodes]
        list_dist = [1] * num_nodes_nhops
        list_dist[s] = 0.0



        while abs(sum(list_dist)) != num_nodes_nhops:

            #Extract the node u with the minimum distance so far from the source, also save its distance u_dist
            sorted_nodes_dist = [[x, y] for (x, y) in sorted(zip(list_dist, list_nodes), key=lambda pair: pair[0])]
            u = sorted_nodes_dist[0][1]
            u_dist = sorted_nodes_dist[0][0]

            #u's shortest distance from the source is final, so add it in the found list
            list_found_dist[u] = u_dist
            list_found_nodes[u] = u


            #adjM

            a=[adjM[u, n] for n in range(0, num_nodes_nhops)]
            #Get the nodes adjacent to u
            u_adj = np.array(adjM[u, :]).flatten()
            u_adj_nodes_tmp = list(np.nonzero(u_adj != 1)[0])
            #7/9/15: Line below added to not include nodes for which shortest
            #distance has already been found.
            #u_adj_nodes = [x for x in u_adj_nodes if x not in list_found_nodes or u_adj_nodes.remove(x)]
            u_adj_nodes = [x for x in u_adj_nodes_tmp if x not in list_found_nodes]

            #u_adj_nodes = np.where(np.array(adjM[u,:]).flatten() != 1.0)[1].tolist()

            #u_adj_nodes_all = np.array(adjM[u,:]).tolist()[0]
            #u_adj_nodes = [i for i,e in enumerate(u_adj_nodes_all) if e!=1]

            for adj_node in u_adj_nodes:
                tmp_dist = u_dist + adjM[u, adj_node]
                if ( tmp_dist < list_dist[adj_node]):
                #adjM[s,adj_node] = tmp_dist
                #adjM[adj_node, s] = tmp_dist
                    list_dist[adj_node] = tmp_dist

            #Remove s's distance from the list of all candidate nodes.
            list_dist[u] = 1  #a value to represent that the shortest distance to u has been found])


        #transfer all the shortest distances back to DM and then to SM
        #SM_expanded_array[s,:] = np.array([1-i for i in list_found_dist])

        for i in range(num_nodes_nhops):
            SM_expanded_array[Mapping_n[s], Mapping_n[i]] = 1 - list_found_dist[i]
            #SM_expanded_array[Mapping_n[i], Mapping_n[s]] = SM_expanded_array[Mapping_n[s], Mapping_n[i]]


        return SM_expanded_array

    #Create a node object and add it to dictionary
    def create_node(self, node_id, node_code):
        if((node_id not in self.node_dict)):
            nodedata = NodeData(node_id, node_code, self)
            self.node_dict.update({node_id:nodedata})

    #Create an edge object and add it to dictionary
    def create_edge(self, node1_id, node2_id, edge_weight, edge_type):
        #Create an edgedata object
        edgedata = EdgeData(self.next_available_edge_id, node1_id, node2_id, edge_weight, edge_type)
        self.edge_dict.update({edgedata.edge_id:edgedata})

        #Increment the next available edge_id
        self.increment_next_available_edge_id()

        #Add the edge to both node's sets
        self.node_dict[node1_id].add_edge_to_set(edgedata.edge_id, edge_type)
        self.node_dict[node2_id].add_edge_to_set(edgedata.edge_id, edge_type)

    def increment_next_available_edge_id(self):
        self.next_available_edge_id = self.next_available_edge_id + 1

    #Create edge objects for all primary and secondary edges
    def create_edge_objects(self):
        if self.isDirty == True:
            self.calculate_num_nodes()

        #SM_secondary = self.SM - self.SM_orig
        #Create a secondary edge for each non zero entry in this matrix.
        for i in range(0, self.num_nodes):
            for j in range(0, self.num_nodes):
                if(i < j):
                    if self.SM_orig[i, j] == 0 and self.SM[i,j] != 0:
                        self.create_edge(i, j, self.SM[i,j], EdgeType.secondary)
                    elif self.SM_orig[i,j] != 0:
                        self.create_edge(i, j, self.SM_orig[i,j], EdgeType.primary)


    #Calculate global measures for the graph
    def calculate_graph_global_measures(self):
        self.calculate_graph_struct_density()
        self.calculate_graph_standard_deviation()

    def calculate_graph_struct_density(self):
        SM_temp = self.SM_orig - np.matrix(np.identity(self.num_nodes), copy=False)

        #Calculate structural density for the whole graph
        self.graph_struct_density = (np.count_nonzero(SM_temp)) / float(( self.num_nodes * (self.num_nodes - 1) )/ 2)
        #print("Structural density of graph %s \n" % self.graph_struct_density)

    def calculate_graph_standard_deviation(self):
        SM_temp = self.SM_orig - np.matrix(np.identity(self.num_nodes), copy=False)

        #Calculate standard deviation of the whole graph
        non_zero_edges = SM_temp.ravel()[np.flatnonzero(SM_temp)]
        self.graph_std = np.std(non_zero_edges)
        #self.graph_struct_density = np.shape(non_zero_edges)[0]
        #print("Standard deviation of graph %s \n" % self.graph_std)

