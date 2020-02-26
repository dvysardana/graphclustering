__author__ = 'divya'

from ClusteringData import ClusteringData
from CNodeData import CNodeData
from EdgeData import EdgeType
from ClusteringVisualizer import ClusteringVisualizer
from EvaluationData import EvaluationData
from ClusteringPrinter import ClusteringPrinter
from AlgorithmName import AlgorithmName


import numpy as np

class Phase2Data(ClusteringData):
    def __init__(self, graphdata, configdata, K, cnodes_dict, next_cluster_label, num_clusters):
        #Call the super class's init function
        super(Phase2Data, self).__init__(graphdata, configdata, K, cnodes_dict, next_cluster_label, num_clusters)
        #data specific to phase 2 of clustering

        self.c_SM = [] #cluster similarity matrix
        self.c_SM_sort = [] #sorted cluster similarity matrix
        self.cnode_num_nodes = [] #Number of nodes per cnode
                                  # matrix as a 2 dimensional list

        #Zhen Hu's algorithm's specific data
        self.outreachM = [] #Outreach matrix as a 2D list
        self.projectionM = [] #Projection matrix as a 2D list

        #evaluation related data
        self.phase = 2
        self.phase2_evaluation_data = None

        #CP algorithm's specific data
        self.inter_cnode_linkage = []
        self.phase2_cnode_MKNN_radius = []
        self.phase2_cluster_initiator_list = []
        self.next_cnode_cluster_label = 0


        #Data for checking structural similarity
        self.inter_cluster_num_primary = [] #Matrix to store number of primary connections
                                            # between two clusters
        self.inter_cluster_percentage_primary = [] #Matrix to store percentage of nodes
                                                   # involved in primary

        #Data for checking edge density similarity
        self.inter_cluster_mean_difference = []
        self.inter_cluster_between_mean_difference = []

        #Data for storing the merge/core periphery decision number
        self.inter_cluster_merge_decision = []

        #Data specific for core periphery
        self.core_periphery_status_list = [] #see if we need this, as each
                                             #cluster data has a field
                                             #core_periphery_status
        self.core_periphery_relations = []
        self.core_periphery_score = []



    def initialize_phase(self):
        self.configdata.logger.debug("Debugging from inside Phase2Data initialize_phase method.")

        #Calculate inter cnode similarity matrix,
        #projection matrix and outreach matrix
        self.calculate_c_SM()

        #Sort inter_cnode_similarity matrix.
        self.sort_c_SM()

    def execute_phase(self):
        self.configdata.logger.debug("Debugging from inside Phase2Data execute_phase method.")

        #execute phase
        self.MKNN_phase2_execute()


    def evaluate_phase(self):
        self.configdata.logger.debug("Debugging from inside Phase2Data evaluate_phase method.")
        self.phase2_evaluation_data = EvaluationData(self.graphdata, self.configdata, self.K, self.phase, self.num_clusters, self.cnodes_dict, AlgorithmName.GMKNN_ZhenHu)
        self.phase2_evaluation_data.calculate_evaluation_measures_for_one_K()

    def visualize_phase(self):
        self.configdata.logger.debug("Debugging from inside Phase2Data visualize_phase method.")
        cluster_label_list = self.generate_cluster_label_list(AlgorithmName.GMKNN_ZhenHu)

        #Graph of clusters
        visualizer = ClusteringVisualizer(self.graphdata, self.configdata, self.K, self.phase, self.num_clusters, cluster_label_list, AlgorithmName.GMKNN_ZhenHu)
        visualizer.visualize_clusters()
        #visualizer.visualize_specific_clusters([2,3])
        #For GMKNN-CP:Krogan
        #visualizer.visualize_specific_clusters([1747, 1807, 1815, 1788, 237])
        #For A2Zsim
        #visualizer.visualize_specific_clusters([17,21,19])
        #visualizer.visualize_specific_clusters([16, 21, 20])
        visualizer.visualize_specific_clusters([20, 25])
        #For A2Zsim1
        #visualizer.visualize_specific_clusters([18,17,15,12,19])

        #For les miserables dataset.
        #visualizer.visualize_specific_clusters([0, 53])
        #print clusters in csv format
        printer = ClusteringPrinter(self.configdata, self.graphdata, self.phase, self.K, cluster_label_list, AlgorithmName.GMKNN_ZhenHu)
        printer.printClusters()




    def calculate_c_SM(self):
        self.configdata.logger.debug("Debugging from inside calculate_c_SM method.")

        #initialize c_SM
        self.c_SM = [[-1] * self.num_clusters for i in range(self.num_clusters)]
        self.projectionM = [[-1] * self.num_clusters for i in range(self.num_clusters)]
        self.outreachM = [[-1] * self.num_clusters for i in range(self.num_clusters)]
        #print(self.num_clusters)
        #print(self.next_cluster_label)

        for i in range(0, self.next_cluster_label-1):
            for j in range(i+1, self.next_cluster_label):
                cnode_i = self.cnodes_dict[i]
                cnode_j = self.cnodes_dict[j]

                projectionij = 0
                projectionji = 0
                projectionji_set = set()
                outreach = 0

                if cnode_i.isDirty == True:
                    cnode_i.calculate_cnode_secondary_fields()

                if cnode_j.isDirty == True:
                    cnode_j.calculate_secondary_fields()

                if(cnode_i.active == True and cnode_j.active == True):
                    for node in cnode_i.node_set:
                        (projection_increment_ij,
                         projection_increment_ji_set,
                         outreach_increment) = self.is_linked(node, cnode_j)

                        projectionij = projectionij + projection_increment_ij
                        if(projection_increment_ji_set != None):
                            projectionji_set = projectionji_set | projection_increment_ji_set
                        outreach = outreach + outreach_increment

                    projectionji = len(projectionji_set)

                    self.projectionM[i][j] = projectionij
                    self.projectionM[j][i] = projectionji
                    self.outreachM[i][j] = outreach
                    self.outreachM[j][i] = outreach

                    self.c_SM[i][j] = (float)(self.outreachM[i][j] * self.projectionM[i][j])/ (float)(cnode_i.num_nodes * cnode_i.num_nodes * cnode_j.num_nodes)
                    self.c_SM[j][i] = (float)(self.outreachM[j][i] * self.projectionM[j][i])/ (float)(cnode_i.num_nodes * cnode_j.num_nodes * cnode_j.num_nodes)


    #Method to check if a node is linked to a cnode
    #A node is linked to a cnode if this node has at
    #at least one MKNN neighbor which lies in cnode.
    def is_linked(self, node_id, cnode_data):
        self.configdata.logger.debug("Debugging from inside is_linked method")

        #cnode_data = self.cnodes_dict[cnode_id]
        cnode_node_set = cnode_data.node_set

        node_MKNN_set = set(self.graphdata.node_dict[node_id].MKNN_list)
        intersection_set = node_MKNN_set.intersection(cnode_node_set)
        len_set = len(intersection_set)
        if len_set != 0:
            projection_increment_ij = 1

            projection_increment_ji_set = intersection_set
            #An intersection of all intersection sets
            #will give a set: its length = projection_ji

            #no. of MKNN relationships this node is part of
            outreach_increment = len_set
        else:
            projection_increment_ij = 0
            projection_increment_ji_set = set()
            outreach_increment = 0

        return (projection_increment_ij, projection_increment_ji_set, outreach_increment)

    #Method to sort c_SM
    def sort_c_SM(self):

        self.configdata.logger.debug("Debugging from inside sort_CM method.")

        #Flatten CM to get a vector of all CM values

        num_rows_CM = len(self.c_SM)
        #print('num rows CM')
        #print(num_rows_CM)

        #Flatten CM to get all values in a flat list
        CM_flat = np.array(self.c_SM).flatten()
        CM_values = CM_flat.reshape(CM_flat.shape[0],1)

        #Create an array of 0 to num_rows_CM
        y = np.array(list(range(0,num_rows_CM)), dtype=int).reshape(num_rows_CM, 1)


        #Create a placeholder for the final sorted array
        CM_indices = np.zeros(shape=(1,2), dtype=int)
        #CM_indices = np.zeros(shape=(1,2), dtype=[('x',int), ('y', int)])


        for i in range(0, num_rows_CM):
            #Create an array of all i's
            x = i * np.ones(shape=(num_rows_CM), dtype=int).reshape(num_rows_CM, 1)

            #Concatenate y with x to form the row and column combinations for CM_sort
            z = np.concatenate((x,y), axis=1)

            #Store z in CM_sort
            CM_indices = np.concatenate((CM_indices, z), axis=0)

        #Delete the first row in CM_sort
        CM_indices = np.delete(CM_indices, (0), axis=0)
        #print("Shape c_SM")
        #print(np.shape(np.array(self.c_SM)))
        #print("Shape CM_indices")
        #print(np.shape(CM_indices))
        #print("Shape CM_values")
        #print(np.shape(CM_values))


        #Concatenate CM_Flat with CM_sort now
        CM_sort = np.concatenate((CM_indices, CM_values), axis=1)

        #sort the matrix based upon column 2 (the column containing the CM values
        col=2
        #CM_sort = np.array(self.c_SM).sort[np.array(CM_sort[:,col].argsort(axis=0)[::-1].tolist()).reshape(-1)]
        CM_sort = CM_sort[np.array(CM_sort[:,col].argsort(axis=0)[::-1].tolist()).reshape(-1)]

        self.c_SM_sort = np.array(CM_sort).tolist()
        #return np.array(self.c_SM_sort).tolist()

    #Method to execute Phase 2 of GMKNN algorithm.
    def MKNN_phase2_execute(self):
        self.configdata.logger.debug("Debugging from inside the method MKNN_Phase2_execute")

        merging_row_num = 0
        #Keep merging the clusters until either
        #a.) The desired number of clusters is obtained
        #b.) There is no CM_sort value left which is greater than 0
        while (self.num_clusters > self.configdata.max_num_clusters and self.c_SM_sort[merging_row_num][2] > 0):
            cnode_id_1 = (int) (self.c_SM_sort[merging_row_num][0])
            cnode_id_2 = (int) (self.c_SM_sort[merging_row_num][1])

            #Check if the c_SM value between the two cnodes is not= -1
            #meaning that the merge already took place between the two
            #or both ids belong to the same cluster.
            if(self.c_SM[cnode_id_1][cnode_id_2] > 0):
                self.configdata.logger.debug("Inside the if part where merging of cnodes takes place:")
                self.configdata.logger.debug(cnode_id_1)
                self.configdata.logger.debug(" and ")
                self.configdata.logger.debug(cnode_id_2)

                cluster_label_new = self.next_cluster_label

                ##Merge cnodes 1 and 2.
                self.merge_cnodes(cnode_id_1, cnode_id_2, cluster_label_new)

                #update number of clusters and next_cluster_label
                self.update_clustering_statistics()

                merging_row_num = 0

                #Generate c_SM_sort again as c_SM has changed now.
                #self.helper.print_list(self.c_SM)
                self.sort_c_SM()
            else:
                self.configdata.logger.debug("Inside the else part where no merging takes place.")
                #merging_row_num remains equal to 0
                merging_row_num = merging_row_num + 1
                #num_clusters remains the same as before


    def merge_cnodes(self, cnode_id_1, cnode_id_2, cluster_label_new):
        #create merged cnode
        self.create_merged_cnode(cnode_id_1, cnode_id_2, cluster_label_new)

        #deactivate the merging cnodes
        self.deactivate_merging_cnodes(cnode_id_1, cnode_id_2)

        #update matrices Projection, Outreach and c_SM
        self.update_phase2_matrices(cnode_id_1, cnode_id_2, cluster_label_new)


    #Method to create merged cnode upon merging of two separate cnodes.
    def create_merged_cnode(self, cnode_id_1, cnode_id_2, cluster_label_new):
        self.configdata.logger.debug("Debugging from inside create_merged_cnode method.")

        #Create a new cnode object
        cnode_data_merged = CNodeData(cluster_label_new, cnode_id_1, cnode_id_2, -1, self.graphdata, self.configdata)

        #Add the new cnode object to cnodes_dict
        self.cnodes_dict[cluster_label_new] = cnode_data_merged

        # #Add nodes to the new cnode
        self.add_nodes_to_merged_cnode(cnode_id_1, cnode_id_2, cluster_label_new)

        #Add edges to the new cnode
        #primary
        self.add_edges_to_merged_cnode(cnode_id_1, cnode_id_2, cluster_label_new, EdgeType.primary)
                                                                                        #symmetric difference gives those elements in one of the two sets and not in both.
        #secondary
        self.add_edges_to_merged_cnode(cnode_id_1, cnode_id_2, cluster_label_new, EdgeType.secondary)

        #Run clustering statistics for the new cnode
        #this also sets the active and dirty flags.
        cnode_data_merged.calculate_cnode_secondary_fields()

    #Method to update phase 2 matrices upon creation of a merged cnode
    def update_phase2_matrices(self, cnode_id_1, cnode_id_2, cluster_label_new):
        #************************
        #Update Matrices
        #************************
        cnode_merged_data = self.cnodes_dict[cluster_label_new]
        if(cnode_merged_data.isDirty == True):
            cnode_merged_data.calculate_cnode_secondary_fields()

        #Update ProjectionM and OutreachM and CM
        projection_new_row = []
        #projection_new_column = []

        outreach_new_row = []

        CM_new_row = []

        #print("Shape c-SM before phase 2 execute loop starts")
        #print(np.shape(np.array(self.c_SM)))
        #Update value of projection, outreach and CM for each currently existing cluster
        for cnode_current_id in range(0, len(self.c_SM)):
            cnode_current_data = self.cnodes_dict[cnode_current_id]
            #num_nodes_current_cluster = NumNodesM_List[current_cluster_no][0]

            if(cnode_current_data.active == True):
                if(cnode_current_data.isDirty == True):
                    cnode_current_data.calculate_cnode_secondary_fields()


                ##############################################
                #Updates for Projection List (Inside the loop)
                #############################################

                #Create a new row for new cluster label and for column: current cluster label
                #This new row will be fully built first in the loop and then added as a whole outside the loop.
                #A special case: Merged cluster's Projection value with cluster label 1 and cluster label 2 to
                # be set to 0 manually.
                projection_new_row_value = self.projectionM[cnode_id_1][cnode_current_id] + self.projectionM[cnode_id_2][cnode_current_id]
                if projection_new_row_value < 0 or cnode_current_id == cnode_id_1 or cnode_current_id == cnode_id_2:
                    projection_new_row_value = -1

                projection_new_row.append(projection_new_row_value)
                #projection_new_column.append(ProjectionM_List[current_cluster_no][cluster_label_1] + ProjectionM_List[current_cluster_no][cluster_label_2])

                #Add new projection value in the new column for new cluster label and row: current_cluster_label
                #This new column. row value will be added in the for loop one by one.
                projection_new_column_value = self.projectionM[cnode_current_id][cnode_id_1] + self.projectionM[cnode_current_id][cnode_id_2]
                if projection_new_column_value < 0 or cnode_current_id == cnode_id_1 or cnode_current_id == cnode_id_2:
                    projection_new_column_value = -1

                self.projectionM[cnode_current_id].append(projection_new_column_value)


                ############################################
                #Updates for Outreach List (Inside the loop)
                ############################################
                #Calculate the new outreach value between the current cluster and the new cluster
                #A special case: Outreach value between new cluster and cluster label 1 and
                #cluster label 2 needs to be set manually= -1
                outreach_new_value = self.outreachM[cnode_id_1][cnode_current_id] + self.outreachM[cnode_id_2][cnode_current_id]

                if outreach_new_value < 0 or cnode_current_id == cnode_id_1 or cnode_current_id == cnode_id_2:
                    outreach_new_value = -1

                outreach_new_row.append(outreach_new_value)
                self.outreachM[cnode_current_id].append(outreach_new_value)

                ###############################################
                #Updates for CM List (Inside the loop)
                ###############################################
                if outreach_new_value == -1 or projection_new_row_value == -1:
                    CM_new_row_value = -1
                else:
                    CM_new_row_value = (outreach_new_value * projection_new_row_value)/(((float)(cnode_merged_data.num_nodes * (float)(cnode_merged_data.num_nodes) * (float) (cnode_current_data.num_nodes))))

                if outreach_new_value == -1 or projection_new_column_value == -1:
                    CM_new_column_value = -1
                else:
                    CM_new_column_value = (outreach_new_value * projection_new_column_value)/ ((float) (cnode_current_data.num_nodes * cnode_current_data.num_nodes * cnode_merged_data.num_nodes))

                CM_new_row.append(CM_new_row_value)
                self.c_SM[cnode_current_id].append(CM_new_column_value)

            elif(cnode_current_data.active == False):
                #The current cnode is not active
                #most probably because it has already merged to form
                #some new cnode.

                projection_new_row_value = -1
                projection_new_row.append(projection_new_row_value)
                projection_new_column_value = -1
                self.projectionM[cnode_current_id].append(projection_new_column_value)

                outreach_new_value = -1
                outreach_new_row.append(outreach_new_value)
                self.outreachM[cnode_current_id].append(outreach_new_value)

                CM_new_row_value = -1
                CM_new_column_value = -1
                CM_new_row.append(CM_new_row_value)
                self.c_SM[cnode_current_id].append(CM_new_column_value)



            #Nullify values for matrices for cnode_id_1 and cnode_id_2
            #with all other cnodes as the new merged cnode represents them
            #both now
            self.projectionM[cnode_id_1][cnode_current_id] = -1
            self.projectionM[cnode_id_2][cnode_current_id] = -1
            self.projectionM[cnode_current_id][cnode_id_1] = -1
            self.projectionM[cnode_current_id][cnode_id_2] = -1

            self.outreachM[cnode_id_1][cnode_current_id] = -1
            self.outreachM[cnode_id_2][cnode_current_id] = -1
            self.outreachM[cnode_current_id][cnode_id_1] = -1
            self.outreachM[cnode_current_id][cnode_id_2] = -1

            self.c_SM[cnode_id_1][cnode_current_id] = -1
            self.c_SM[cnode_id_2][cnode_current_id] = -1
            self.c_SM[cnode_current_id][cnode_id_1] = -1
            self.c_SM[cnode_current_id][cnode_id_2] = -1


        ###############################################
        #Updates for Projection List (Outside the loop)
        ###############################################

        projection_new_row.append(-1) #Projection of new cluster with self = -1
        #Add the row for the new cluster to ProjectionM
        self.projectionM.append(projection_new_row)


        ###############################################
        #Updates for Outreach List (Outside the loop)
        ###############################################
        outreach_new_row.append(-1) #Outreach of new cluster with itself
        #Add the new row for the new cluster to OutreachM
        self.outreachM.append(outreach_new_row)

        #############################################
        #Updates for CM (Outside the loop)
        #############################################
        CM_new_row.append(-1)
        #Add the row for the new cluster to CM
        self.c_SM.append(CM_new_row)




    #Method to deactivate the merging cnodes.
    def deactivate_merging_cnodes(self, cnode_id_1, cnode_id_2):
        cnode_data_1 = self.cnodes_dict[cnode_id_1]
        cnode_data_2 = self.cnodes_dict[cnode_id_2]
        self.deactivate_cnode(cnode_data_1)
        self.deactivate_cnode(cnode_data_2)

    def deactivate_cnode(self, cnode_data):
        cnode_data.deactivate_cnode()

    #Method to update clustering statistics after each merging in phase 2
    def update_clustering_statistics(self):
        self.num_clusters = self.num_clusters - 1
        self.next_cluster_label = self.next_cluster_label + 1



    #Method to add nodes to the merged cnode formed by merging of two cnodes
    def add_nodes_to_merged_cnode(self, cnode_id_1, cnode_id_2, cluster_label_new):
        cnode_data_1 = self.cnodes_dict[cnode_id_1]
        cnode_data_2 = self.cnodes_dict[cnode_id_2]
        cnode_data_merged = self.cnodes_dict[cluster_label_new]
        #Add nodes to the new cnode
        cnode_data_merged.node_set = cnode_data_1.node_set | cnode_data_2.node_set

        #Update cluster membership of each node in the new nodeset
        for node_id in cnode_data_1.node_set:
            node = self.graphdata.node_dict[node_id]
            del node.GMKNN_clabel_dict[cnode_id_1]
            node.GMKNN_clabel_dict[cluster_label_new] = cnode_id_1
                      #For each node (in phase 2), now the cluster center
                      #holds the cnode_id they come from in the big merged
                      #cnode. In phase 2, it was holding the actual cluster
                      #center node_id.

        for node_id in cnode_data_2.node_set:
            node = self.graphdata.node_dict[node_id]
            del node.GMKNN_clabel_dict[cnode_id_2]
            node.GMKNN_clabel_dict[cluster_label_new] = cnode_id_2

    #Method to add edges to the merged cnode (both primary/secondary)
    def add_edges_to_merged_cnode(self, cnode_id_1, cnode_id_2, cluster_label_new, edge_type):
        cnode_data_1 = self.cnodes_dict[cnode_id_1]
        cnode_data_2 = self.cnodes_dict[cnode_id_2]
        cnode_data_merged = self.cnodes_dict[cluster_label_new]

        temp_set = self.get_edgeset_between_cnodes(cnode_data_1, cnode_data_2, edge_type)
        cnode_data_merged.internal_edge_dict[edge_type] = cnode_data_1.internal_edge_dict[edge_type] | cnode_data_2.internal_edge_dict[edge_type] | temp_set
        cnode_data_merged.external_edge_dict[edge_type] = cnode_data_1.external_edge_dict[edge_type].symmetric_difference(cnode_data_2.external_edge_dict[edge_type])
                                                                                                #(in one of the two, not both)
    #Method to get the edgeset shared between two cnodes
    def get_edgeset_between_cnodes(self, cnode_data_1, cnode_data_2, edge_type):
        temp_set = cnode_data_1.external_edge_dict[edge_type].intersection(cnode_data_2.external_edge_dict[edge_type])
        return temp_set


class InterCNodeRelationType(object):
    none = 0
    cluster = 1
    coreperiphery = 2
    sibling = 3
    nevermerge = 4 #None of structure or edge weight
                   #criteria satisfied..so we want to
                   #save this decision so that even the
                   #children of these clusters can learn
                   #from these clusters when forming MKNN
                   #neighbors (check later)
