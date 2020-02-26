__author__ = 'divya'

import numpy as np
from ClusteringData import ClusteringData
from CNodeData import CNodeData
from EdgeData import EdgeData
from EdgeData import EdgeType
from ClusteringVisualizer import ClusteringVisualizer
from EvaluationData import EvaluationData
from ClusteringPrinter import ClusteringPrinter
from AlgorithmName import AlgorithmName

#from sets import Set

class Phase1Data(ClusteringData):
    def __init__(self, graphdata, configdata, K):
        #Call the super class's init function
        super(Phase1Data, self).__init__(graphdata, configdata, K, {}, 0, 0)
        #Deg = np.matrix(np.zeros(shape = (self.graphdata.num_nodes, 1)))

        self.MKNN_radius_dict = {}
        self.cluster_initiator_list = [] #A list containing node_ids in cluster initiator order

        self.phase = 1
        self.phase1_evaluation_data = None

    ####################################
    #Initialize phase1 of clustering
    ###################################
    def initialize_phase(self):

        self.configdata.logger.debug("Debugging from inside Phase1Data initialize_phase")

        #Reset all cluster labels of nodes to -1
        self.initialize_node_cluster_labels()

        #Calculate the MKNN list for each node
        self.calculate_MKNN()

        #Calculate each node's degree and MKNN radius list
        self.calculate_node_statistics()

        #Calculate cluster initiator order using MKNN_rad
        self.calculate_cluster_initiator_order()

    ######################################
    #Execute phase1 of GMKNN clustering
    ######################################
    def execute_phase(self):
        self.configdata.logger.debug("Debugging from inside Phase1Data execute_phase")

        #Execute Phase1
        self.MKNN_phase1_execute()

    #############################################
    #Generate Phase specific evaluation measures
    #############################################
    def evaluate_phase(self):
        self.phase1_evaluation_data = EvaluationData(self.graphdata, self.configdata, self.K, self.phase, self.num_clusters, self.cnodes_dict, AlgorithmName.GMKNN_ZhenHu)
        self.phase1_evaluation_data.calculate_evaluation_measures_for_one_K()


    #Generate Phase specific visualization graphs and
    #printing of clustering results
    def visualize_phase(self):
        cluster_label_list = self.generate_cluster_label_list(AlgorithmName.GMKNN_ZhenHu)

        #Graph of clusters
        visualizer = ClusteringVisualizer(self.graphdata, self.configdata, self.K, self.phase, self.num_clusters, cluster_label_list, AlgorithmName.GMKNN_ZhenHu)
        visualizer.visualize_clusters()
        visualizer.visualize_specific_clusters([3, 5, 11])

        #print clusters in csv format
        printer = ClusteringPrinter(self.configdata, self.graphdata, self.phase, self.K, cluster_label_list, AlgorithmName.GMKNN_ZhenHu)
        printer.printClusters()

    ######################################
    #Initialize: Calculate MKNN matrix
    ######################################
    def calculate_MKNN(self):

        self.configdata.logger.debug("Debugging from inside calculate_MKNN method.")

        #Initialize the MKNN matrix
        #MKNN = np.ones(shape=(self.graphdata.num_nodes, self.K)) * -1

        #SM.shape

        #Flatten the SM matrix into another edges x 1 matrix
        SM_flat= self.graphdata.SM.flatten()
        #SM_flat.shape


        #concatenate the flattened SM with Edge indices
        num_dir_edges = SM_flat.shape[1]
        x = np.array(list(range(self.graphdata.num_nodes)), dtype=int).reshape(self.graphdata.num_nodes, 1)

        for i in range(self.graphdata.num_nodes):
            y= np.ones((self.graphdata.num_nodes,1)) * i
            z = np.concatenate((y,x), axis=1)
            z.shape
            if i==0:
                final = z
            else:
                final = np.concatenate((final,z), axis=0)

            #Initialize the MKNN list of  node i
            self.graphdata.node_dict[i].initialize_MKNN(self.K)

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
                MKNN_list_row = self.graphdata.node_dict[row].MKNN_list
                MKNN_list_col = self.graphdata.node_dict[col].MKNN_list
                if( -1 in MKNN_list_row and -1 in MKNN_list_col):
                    idx_row = MKNN_list_row.index(-1)
                    idx_col = MKNN_list_col.index(-1)
                    MKNN_list_row[idx_row] = col
                    MKNN_list_col[idx_col] = row

        #self.MKNN = np.matrix(MKNN)

    #Calculate Node statistics
    def calculate_node_statistics(self):
        self.configdata.logger.debug("Debugging from inside calculate_node_statistics method")
        for i in range(self.graphdata.num_nodes):
            #Calculate degree of each node
            self.graphdata.node_dict[i].calculate_primary_degree()

            #Calculate MKNN_radius of each node.
            self.calculate_node_radius_ver_1(i)
            #self.calculate_node_radius_ver_2(i)
    # #######################################################
    # #Initialize: Calculate Degree of each node in the graph
    # #######################################################
    # def calculate_degree(self, node):
    #     self.configdata.logger.debug("Debugging from inside calculate_degree.")
    #
    #     #Deg = np.zeros(shape = (self.graphdata.num_nodes, 1))
    #     for i in range(self.graphdata.num_nodes):
    #         self.graphdata.node_dict[i].degree = np.count_nonzero(self.graphdata.SM_orig[i,:])-1



    #################################################################
    #Initialize: Calculate Radius(version1) for node_id in the graph
    #################################################################
    def calculate_node_radius_ver_1(self, node_id):

        self.configdata.logger.debug("Debugging from inside calculate_radius_ver_1 method")

        #all MKNN neighbors of node i
        a = self.graphdata.node_dict[node_id].MKNN_list
        a = [x for x in a if x != -1]
        type(a)

        #number of non -1 neighbors
        num_row = len(a)


        sum_row = sum((self.graphdata.SM[node_id,int(e)]) for e in a) #version 1

        #normalize sum_row
        if(num_row != 0):
            sum_row = sum_row/num_row

        #self.graphdata.node_dict[node_id].MKNN_radius = sum_row
        self.MKNN_radius_dict[node_id] = sum_row

    #################################################################
    #Initialize: Calculate Radius(version2) of each node in the graph
    #################################################################
    def calculate_node_radius_ver_2(self, node_id):

        self.configdata.logger.debug("Debugging from inside P1_calc_radius_ver_2 method.")

        #all MKNN neighbors of node i
        a = self.graphdata.node_dict[node_id].MKNN_list
        a = [x for x in a if x != -1]
        type(a)

        #number of non -1 neighbors
        num_row = len(a)


        #sum_row = sum((self.Deg[int(e),0] * self.graphdata.SM[i,int(e)]) for e in a) #version 2
        sum_row = sum((self.graphdata.node_dict[int(e)].degree * self.graphdata.SM[node_id,int(e)]) for e in a) #version 2


        #normalize sum_row
        if(num_row != 0):
            sum_row = sum_row/num_row

        #self.graphdata.node_dict[node_id].MKNN_radius = sum_row
        self.MKNN_radius_dict[node_id] = sum_row


    #######################################################
    #Initialize: Calculate ClusterInitiator(CI) matrix
    #This matrix contains and ordered dictionary of nodes
    #based upon their radius
    #######################################################
    def calculate_cluster_initiator_order(self):
        #sort the node_dict, based upon the radius value of its objects.
        self.cluster_initiator_list = [key for (key, value) in sorted(iter(self.MKNN_radius_dict.items()), reverse=True, key=lambda k_v: (k_v[1],k_v[0]))]

    ##############################################
    #Execute Phase 1
    ##############################################
    def MKNN_phase1_execute(self):

        self.configdata.logger.debug("Debugging from inside MKNN_Phase1_execute method")

        #Initialize matrices
        #Cluster label matrix
        #CL = -1 * np.matrix(np.ones(shape = (num_nodes, 1)))
        #Cluster center matrix
        #CC = -1 * np.matrix(np.ones(shape = (num_nodes, 1)))

        c_label = 0
        for i  in range(self.graphdata.num_nodes):
            #i=4
            c_initiator = self.cluster_initiator_list[i] #initiator id
            c_initiator_node = self.graphdata.node_dict[c_initiator] #node object
                                                        #for initiator
            self.configdata.logger.debug("Initiator:")
            self.configdata.logger.debug(c_initiator)
            self.configdata.logger.debug(self.graphdata.node_dict[c_initiator].node_code)

            # print("initiator")
            # print(self.graphdata.node_dict[c_initiator].node_code)
            # print("MKNNs")
            # self.helper.print_list_codes(c_initiator_node.MKNN_list, self.graphdata.node_dict)

            #if(c_initiator_node.GMKNN_clabel == -1):
            #if c_initiator does not already belong to a cluster
            if(len(c_initiator_node.GMKNN_clabel_dict) == 0):

                self.configdata.logger.debug("Initiator's cluster label is not yet set,"
                                             " so it will initiate clustering:")
                #Update cluster membership for c_initiator (algorithm_name = 0)
                self.update_node_cluster_membership(c_initiator_node, -1, self.next_cluster_label, c_initiator, AlgorithmName.GMKNN_ZhenHu)

                #Update cluster label
                clabel_current = self.next_cluster_label
                self.next_cluster_label = self.next_cluster_label+1

                #update number of clusters
                self.num_clusters = self.num_clusters + 1

                #Check cluster initiator's neighbors for cluster membership
                for j in range(self.K):
                    #j=0
                    c_initiator_MKNN = c_initiator_node.MKNN_list[j]



                    add_flag = -1

                    if(c_initiator_MKNN != -1):
                        self.configdata.logger.debug("MKNN neighbor:")
                        self.configdata.logger.debug(c_initiator_MKNN)
                        self.configdata.logger.debug(self.graphdata.node_dict[c_initiator_MKNN].node_code)
                        #CHECK for structural similarity
                        #Task 1: check for at least one primary connection with cluster
                        c_initiator_MKNN_node = self.graphdata.node_dict[c_initiator_MKNN]
                        add_flag = self.check_for_primary_connection(c_initiator_MKNN_node, clabel_current)
                        #add_flag = 1 #This addition is to test the actual Zhen Hu's algorithm.
                        #It allows clusters to be formed with absolutely no primary connection among some nodes.
                        #Task2: if CL(c_initiator_MKNN) =-1, then good
                        #else SD comparison

                        #CHECK for edge weight similarity ONLY if structural similarity is good
                        #i.e. add_flag=0 .
                        if(add_flag == 0):
                            if(len(c_initiator_MKNN_node.GMKNN_clabel_dict) == 0):
                                #the current MKNN neighbor does not belong to any cluster
                                #assign it the current cluster label
                                clabel_other = -1
                                add_flag = 1
                            else:
                                #calculate percentage change in SD in going from one set to the other
                                #for both the set pairs
                                clabel_other = list(c_initiator_MKNN_node.GMKNN_clabel_dict.keys())[0]
                                #compare the percentage change in SD for both the sets.
                                if clabel_other != clabel_current:
                                    #(the two cluster labels might be same if
                                    # code for MKNN MKNN neighbor is activated.)
                                    #Check for standard deviation
                                    add_flag_1 = self.check_for_MKNN_neighbor_transfer_cluster(c_initiator, c_initiator_MKNN, clabel_current)
                                    #Check for similarity from cluster center
                                    add_flag_2 = self.check_for_MKNN_neighbor_transfer_cluster_1(c_initiator, c_initiator_MKNN, clabel_current)
                                    #check for structure (no. of shared edges
                                    add_flag_3 = self.check_for_MKNN_neighbor_transfer_cluster_2(c_initiator, c_initiator_MKNN, clabel_current)
                                    add_flag_2 = 1
                                    add_flag_3 = 1
                                    add_flag = add_flag_1 and add_flag_3
                        elif(add_flag == -1):
                            self.configdata.logger.debug("Primary connection check failed")

                        #If both structure and edge weight checks are satisfied,
                        #then, add c_initiator_MKNN to the current cluster.
                        if(add_flag == 1):
                            #Update cluster membership for c_initiator_MKNN_Node
                            self.update_node_cluster_membership(c_initiator_MKNN_node, clabel_other, clabel_current, c_initiator, AlgorithmName.GMKNN_ZhenHu)

                           # self.graphdata.node_dict[c_initiator_MKNN, 0]
                            #CL[c_initiator_MKNN, 0] = c_label_current
                            #CC[c_initiator_MKNN, 0] = c_initiator

                            #Task 3: if neighbor added sucessfully, an optional
                            #neighbor of neighbor checking for addition based upon
                            #standard deviation check (i.e. add MKNN MKNN neighbor
                            #if it decreases the standard deviation of addition
                            ###########################################
                            #self.perform_MKNN_MKNN_neighbor_addition(c_initiator, c_initiator_MKNN_node, clabel_current)
                            ###########################################


                    #next: check for runtime error plus clustering results on very dummy matrix.

        #Phase 1 ends here
        ######u########################################################################################


    #Move node's from old cluster to new cluster
    def update_node_cluster_membership(self, node, old_cluster_label, new_cluster_label, new_cluster_center, algorithm_name):
        self.configdata.logger.debug("Debugging from inside update_cluster_membership method")

        if(old_cluster_label != -1):
            #Remove node from old_cluster_label
            self.remove_node_from_cluster_label(node, old_cluster_label, algorithm_name)

        if(new_cluster_label != -1):
            #Add node to new_cluster
            self.add_node_to_cluster_label(node, new_cluster_label, new_cluster_center, algorithm_name)


    ##################################################
    #Method to update the cluster membership of a node
    ##################################################
    def add_node_to_cluster_label(self, node, cluster_label, cluster_center, algorithm_name):
        self.configdata.logger.debug("Debugging from inside add_node_cluster_label method")

        #set the node's cluster label and cluster center in the dict
        if(algorithm_name == 0):
            node.GMKNN_clabel_dict[cluster_label] = cluster_center
        elif(algorithm_name == 1):
            node.clusterone_clabel_dict[cluster_label] = cluster_center

        # case: cluster_label does not exist in clusters dictionary
        #create a cnode object and add it to the dictionary
        if(self.cnodes_dict.get(cluster_label) == None):
            #Create a new cnode
            cnode = CNodeData(cluster_label, -1, -1, cluster_center, self.graphdata, self.configdata)

            # #cluster.num_nodes = 1
            # cnode.node_set.add(node.node_id)
            # #Add edges to cluster's external edge dicts.
            # cnode.external_edge_dict[EdgeType.primary].update(node.node_edges_dict[EdgeType.primary])
            # cnode.external_edge_dict[EdgeType.secondary].update(node.node_edges_dict[EdgeType.secondary])

            #Add node to cnode
            self.add_node_to_cnode(node, cnode)
            #Add cnode to cnodes_dict
            self.cnodes_dict[cluster_label] = cnode


        #case: cluster_label already exists there, add the node id
        #to the corresponding c-node
        else:
            #Get all members of cluster_label
            cnode = self.cnodes_dict[cluster_label]

            #Add node to cnode
            self.add_node_to_cnode(node, cnode)

        cnode.isDirty = True
        cnode.active = True

    ##########################################
    #Method to add a node to an existing cnode
    ##########################################
    def add_node_to_cnode(self, node, cnode):
        #Add node to cnode's nodeset.
        cnode.node_set.add(node.node_id)

        #Add node's edges to cnode's internal and external
        #(primary/secondary) edge sets

        #Step 1:
        #ADD node's contribution to the cluster's internal edges.
        #REMOVE it from cluster's external edges

        #update cnode's internal primary edge set
        set_temp = cnode.external_edge_dict[EdgeType.primary].intersection(node.node_edges_dict[EdgeType.primary])
        cnode.internal_edge_dict[EdgeType.primary].update(set_temp)

        #update cnode's external primary edge set
        cnode.external_edge_dict[EdgeType.primary].difference_update(node.node_edges_dict[EdgeType.primary])

        #update cnode's internal secondary edge set
        set_temp = cnode.external_edge_dict[EdgeType.secondary].intersection(node.node_edges_dict[EdgeType.secondary])
        cnode.internal_edge_dict[EdgeType.secondary].update(set_temp)

        #update cnode's external secondary edge set
        cnode.external_edge_dict[EdgeType.secondary].difference_update(node.node_edges_dict[EdgeType.secondary])

        #Step 2:
        #ADD node's contribution to cluster's external edges

        #update cnode's external primary edge set
        set_temp = node.node_edges_dict[EdgeType.primary].difference(cnode.internal_edge_dict[EdgeType.primary])
        cnode.external_edge_dict[EdgeType.primary].update(set_temp)

        #update cnode's external secondary edge set
        set_temp = node.node_edges_dict[EdgeType.secondary].difference(cnode.internal_edge_dict[EdgeType.secondary])
        cnode.external_edge_dict[EdgeType.secondary].update(set_temp)


    ##################################################
    #Method to update the cluster membership of a node
    ##################################################
    def remove_node_from_cluster_label(self, node, cluster_label, algorithm_name):
        #Remove the node's entry for old cluster label in the clabel dict
        if(algorithm_name == 0):
            del node.GMKNN_clabel_dict[cluster_label]
        elif(algorithm_name == 1):
            del node.clusterone_clabel_dict[cluster_label]

        #Get cnode corresponding to cluster_label
        cnode = self.cnodes_dict[cluster_label]

        #remove node from cnode
        self.remove_node_from_cnode(node, cnode)

        cnode.isDirty = True
        #Check if cnode has 0 nodes now
        if len(cnode.node_set) == 0:
            #Delete the cnode for this cluster_label
            del self.cnodes_dict[cluster_label]


    ###############################################
    #Method to remove a node from an existing cnode
    ###############################################
    def remove_node_from_cnode(self, node, cnode):
        #Remove node from cnode's nodeset.
        cnode.node_set.remove(node.node_id)

        #Step 1:
        #REMOVE node's contribution to cnode's external edges

        #update cnode's external primary edge set
        cnode.external_edge_dict[EdgeType.primary].difference_update(node.node_edges_dict[EdgeType.primary])

        #update cnode's external secondary edge set
        cnode.external_edge_dict[EdgeType.secondary].difference_update(node.node_edges_dict[EdgeType.secondary])

        #Step 2:
        #REMOVE node's contribution to cnode's internal edges
        #ADD it to cnode's external edges

        #update cnode's internal primary edge set
        set_temp = cnode.internal_edge_dict[EdgeType.primary].intersection(node.node_edges_dict[EdgeType.primary])
        cnode.internal_edge_dict[EdgeType.primary].difference_update(set_temp)

        #update cnode's external primary edge dict
        cnode.external_edge_dict[EdgeType.primary].update(set_temp)

        #update cnode's internal secondary edge set
        set_temp = cnode.internal_edge_dict[EdgeType.secondary].intersection(node.node_edges_dict[EdgeType.secondary])
        cnode.internal_edge_dict[EdgeType.secondary].difference_update(set_temp)

        #update cnode's external secondary edge set
        cnode.external_edge_dict[EdgeType.secondary].update(set_temp)

    ###################################################################
    #Method to check for at least one primary connection between a node
    # and a cnode
    #Return -1 if no primary connection.
    #Return 0 if at least one primary connection is present.
    ###################################################################
    def check_for_primary_connection(self, node, cluster_label):

        #Get cnode corresponding to cluster_label
        cnode = self.cnodes_dict[cluster_label]

        set_temp = cnode.external_edge_dict[EdgeType.primary].intersection(node.node_edges_dict[EdgeType.primary])
        if(len(set_temp) == 0):
            return -1
        else:
            return 0

    #
    # #function to check for at least one primary connection between two sets
    # def check_for_primary_connection(self, SM_orig, CL, c_initiator_MKNN, c_label_current, log):
    #     self.configdata.logger.debug("Debugging from inside check_for_primary_connection module")
    #
    #     add_flag = -1
    #     c_members_current = np.where(CL[:]==c_label_current)[0].T
    #     #c_members_current =
    #     edge_set = calculate_edge_set(SM_orig, c_members_current, np.matrix([[int(c_initiator_MKNN)]]), False, log)
    #     edge_set = edge_set[edge_set !=0]
    #     if(edge_set.size):
    #         add_flag = 0
    #     return add_flag

    ##########################################
    #Execute: Check for transfer of cluster membership
    ##########################################
    def check_for_MKNN_neighbor_transfer_cluster(self, c_initiator, c_initiator_MKNN, clabel_current):
        self.configdata.logger.debug("Debugging from inside check_for_transfer_cluster_membership method")
        add_flag = self.check_for_sd_change(c_initiator, c_initiator_MKNN, clabel_current)
        return add_flag

    #This version of the method is based upon what
    #is implemented in Zhen Hu's paper
    def check_for_MKNN_neighbor_transfer_cluster_1(self, c_initiator, c_initiator_MKNN, c_label_current):
        c_initiator_node = self.graphdata.node_dict[c_initiator]
        c_initiator_MKNN_node = self.graphdata.node_dict[c_initiator_MKNN]
        c_label_other = list(c_initiator_MKNN_node.GMKNN_clabel_dict.keys())[0]
                                        #The above line of code works as there should
                                        #be only one cluster label in the dictionary.

        cnode_other = self.cnodes_dict[c_label_other]
        cnode_other_center_node = self.graphdata.node_dict[cnode_other.cluster_center]

        if(self.graphdata.SM[c_initiator_node.node_id,c_initiator_MKNN_node.node_id] > self.graphdata.SM[c_initiator_MKNN_node.node_id,cnode_other_center_node.node_id]):
            add_flag = True
        else:
            add_flag = False

        return add_flag

    #This version of the method is based upon number of
    #edges (in turn no. of shared neighbors between the node and the
    #two clusters in question
    def check_for_MKNN_neighbor_transfer_cluster_2(self, c_initiator, c_initiator_MKNN, c_label_current):
        c_initiator_node = self.graphdata.node_dict[c_initiator]
        cnode_current = self.cnodes_dict[c_label_current]
        c_initiator_MKNN_node = self.graphdata.node_dict[c_initiator_MKNN]
        c_label_other = list(c_initiator_MKNN_node.GMKNN_clabel_dict.keys())[0]
                                        #The above line of code works as there should
                                        #be only one cluster label in the dictionary.

        cnode_other = self.cnodes_dict[c_label_other]

        num_common_edges_current = len(c_initiator_MKNN_node.node_edges_dict[EdgeType.primary].intersection(cnode_current.external_edge_dict[EdgeType.primary]))
        num_common_edges_other = len(c_initiator_MKNN_node.node_edges_dict[EdgeType.primary].intersection(cnode_other.internal_edge_dict[EdgeType.primary]))

        if num_common_edges_current > num_common_edges_other:
            add_flag = True
        else:
            add_flag = False

        return add_flag




    ###########################################
    #Check if the standard deviation change is better for
    # the c_initiator or not upon adding c_initiator_MKNN
    #than c_initiator_MKNN's current cluster.
    ###########################################
    def check_for_sd_change(self, c_initiator, c_initiator_MKNN, c_label_current):
        add_flag = 0

        c_initiator_node = self.graphdata.node_dict[c_initiator]
        c_initiator_MKNN_node = self.graphdata.node_dict[c_initiator_MKNN]
        cnode_current = self.cnodes_dict[c_label_current]

        c_label_other = list(c_initiator_MKNN_node.GMKNN_clabel_dict.keys())[0]
                                        #The above line of code works as there should
                                        #be only one cluster label in the dictionary.

        cnode_other = self.cnodes_dict[c_label_other]

        cnode_current.calculate_cnode_secondary_fields()
        cnode_other.calculate_cnode_secondary_fields()

        sd_current = (float)(cnode_current.standard_deviation_edges)
        sd_other = (float)(cnode_other.standard_deviation_edges)

        (sd_current_proposed, edgeset_current_proposed_length) = cnode_current.calculate_SD_on_node_addition(c_initiator_MKNN_node)

        (sd_other_proposed, edgeset_other_proposed_length) = cnode_other.calculate_SD_on_node_removal(c_initiator_MKNN_node)

        #calculate and compare the change in Standard Deviation
        #if(cnode_current.num_internal_primary_edges != 1 and edgeset_other_proposed_length != 1):
        #If the current cluster doing the pull is at at least 2 nodes large
        #and the cluster from which we are pulling is at least 3 nodes large
        if(cnode_current.num_nodes > 1 and (cnode_other.num_nodes - 1) > 1):
            change_SD_current = abs(sd_current_proposed - sd_current)
            change_SD_other = abs(sd_other - sd_other_proposed)
            if(change_SD_current < change_SD_other):
                #the transfer of cluster membership can be done
                add_flag = 1

        return add_flag

    def perform_MKNN_MKNN_neighbor_addition(self, c_initiator, c_initiator_MKNN_node, clabel_current):
        for l in range(self.K):
            c_initiator_MKNN_MKNN = c_initiator_MKNN_node.MKNN_list[l]
            add_flag = -1

            if(c_initiator_MKNN_MKNN != -1):
                self.configdata.logger.debug("MKNN MKNN neighbor:")
                self.configdata.logger.debug(c_initiator_MKNN_MKNN)
                self.configdata.logger.debug(self.graphdata.node_dict[c_initiator_MKNN_MKNN].node_code)
                #CHECK for structural similarity
                #Task 1: check for at least one primary connection with cluster
                c_initiator_MKNN_MKNN_node = self.graphdata.node_dict[c_initiator_MKNN_MKNN]
                add_flag = self.check_for_primary_connection(c_initiator_MKNN_MKNN_node, clabel_current)
                #add_flag = 1 #This addition is to test the actual Zhen Hu's algorithm.
                #It allows clusters to be formed with absolutely no primary connection among some nodes.
                #Task2: if CL(c_initiator_MKNN) =-1, then good
                #else SD comparison

                #CHECK for edge weight similarity ONLY if structural similarity is good
                #i.e. add_flag=0 .
                if(add_flag == 0):
                    if(len(c_initiator_MKNN_MKNN_node.GMKNN_clabel_dict) == 0):
                        #the current MKNN MKNN neighbor does not belong to any cluster
                        #assign it the current cluster label
                        #only if on its addition, standard deviation doesn't increase
                        clabel_other = -1
                        add_flag = self.check_for_MKNN_MKNN_neighbor_addition(c_initiator, c_initiator_MKNN_MKNN, clabel_current)
                    else:
                        #the current MKNN MKNN neighbor
                        #will not be checked for addition.
                        pass
                elif(add_flag == -1):
                    self.configdata.logger.debug("Primary connection check failed for MKNN MKNN neighbor")

                #If both structure and edge weight checks are satisfied,
                #then, add c_initiator_MKNN to the current cluster.
                if(add_flag == 1):
                    #Update cluster membership for c_initiator_MKNN_Node
                    self.update_node_cluster_membership(c_initiator_MKNN_MKNN_node, clabel_other, clabel_current, c_initiator, AlgorithmName.GMKNN_ZhenHu)


    #Method to check if it is feasible to add MKNN MKNN neighbor
    #based upon standard deviation check
    def check_for_MKNN_MKNN_neighbor_addition(self, c_initiator, c_initiator_MKNN_MKNN, c_label_current):
        add_flag = 0
        self.configdata.logger.debug("Debugging from inside check for MNN MKNN neighbor additon method")
        c_initiator_node = self.graphdata.node_dict[c_initiator]
        c_initiator_MKNN_MKNN_node = self.graphdata.node_dict[c_initiator_MKNN_MKNN]
        cnode_current = self.cnodes_dict[c_label_current]

        cnode_current.calculate_cnode_secondary_fields()

        sd_current = (float)(cnode_current.standard_deviation_edges)

        (sd_current_proposed, edgeset_current_proposed_length) = cnode_current.calculate_SD_on_node_addition(c_initiator_MKNN_MKNN_node)

        #calculate and compare the change in Standard Deviation
        #if the current cnode has at least 3 nodes and sd on addition is
        #less than the sd on before, then add.
        if(cnode_current.num_nodes > 2 and sd_current_proposed < sd_current):
            add_flag = 1

        return add_flag

    # def check_for_sd_change(self, c_initiator, c_initiator_MKNN, c_label_current):
    #
    #     self.configdata.logger.debug("Debugging from inside check_for_sd_change method")
    #
    #     add_flag = 0
    #     #the current MKNN neighbor belongs to an existing cluster
    #     #comapare the variance
    #     c_label_other = self.node_dict[c_initiator_MKNN].GMKNN_clabel_dict
    #     #c_label_other = -1
    #
    #     c_center_other = self.node_dict[c_initiator_MKNN].cluster_center
    #     c_center_current = c_initiator
    #
    #     #make the four sets
    #     # c_members_other = np.where(CL[:]==c_label_other)[0].T
    #     # c_members_current = np.where(CL[:]==c_label_current)[0].T
    #     # c_members_current_proposed = np.concatenate((c_members_current, [[int(c_initiator_MKNN)]]), axis=0, )
    #     # c_members_other_proposed = c_members_other[c_members_other != c_initiator_MKNN].T
    #
    #     c_members_other = self.cluster_members_dict.get(c_label_other)
    #     c_members_current = self.cluster_members_dict.get(c_label_current)
    #
    #     if(c_members_current != None):
    #         c_members_current_proposed = c_members_current.add(int(c_initiator_MKNN))
    #     if(c_members_other != None):
    #         c_members_other_proposed = c_members_other.remove(c_initiator_MKNN)
    #
    #
    #     #calculate Standard deviation of edges in each set
    #     SD_other = calculate_std_node_set(SM_orig, c_members_other, log)
    #     SD_current = calculate_std_node_set(SM_orig, c_members_current, log)
    #     SD_current_proposed = calculate_std_node_set(SM_orig, c_members_current_proposed, log)
    #     SD_other_proposed = calculate_std_node_set(SM_orig, c_members_other_proposed, log)
    #
    #     #calculate and compare the change in Standard Deviation
    #     if(c_members_current.shape[0] != 1 and c_members_other_proposed.shape[0] != 1):
    #         change_SD_current = abs(SD_current_proposed - SD_current)
    #         change_SD_other = abs(SD_other - SD_other_proposed)
    #         if(change_SD_current < change_SD_other):
    #             #do the transfer of cluster membership
    #             add_flag = 1
    #             #CL[c_initiator_MKNN, 0] = c_label_current
    #             #CC[c_initiator_MKNN, 0] = c_initiator
    #
    #     return add_flag
    #
    #
    #
    # ########################################################
    # #function to calculate SD of a set of edges
    # ########################################################
    # def calculate_std_node_set(self, SM_orig, set_input, log):
    #     self.configdata.logger.debug("Debugging from inside calc_std_node_set method")
    #
    #     set_edges = calculate_edge_set(SM_orig, set_input, set_input, True, log)
    #     SD = np.std(set_edges[set_edges!=0])
    #     return SD
    #
    # #########################################################
    # #function to calculate the set of edges between two sets
    # #########################################################
    # def calculate_edge_set(self, SM_orig, set_input1, set_input2, same, log):
    #     self.configdata.logger.debug("Debugging from inside calculate_edge_set method")
    #
    #
    #     #set_input1 = np.matrix([[2]])
    #     #set_input2 = np.matrix([[3]])
    #     #same = False
    #     set_edges = []
    #     for i in range(np.shape(set_input1)[0]):
    #         for j in range(np.shape(set_input2)[0]):
    #             if(same==True):
    #                 if(i < j):
    #                     set_edges.append(float(SM_orig[set_input1[i], set_input2[j]]))
    #             else:
    #                 set_edges.append(float(SM_orig[set_input1[i], set_input2[j]]))
    #     matrix_edges = np.matrix(set_edges)
    #     #returns 0 as well if an edge weight = 0
    #     return  matrix_edges
    #
