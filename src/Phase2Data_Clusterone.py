__author__ = 'divya'

from ClusteringData_Clusterone import ClusteringData_Clusterone
from Phase2Data import Phase2Data
from CNodeData_Clusterone import CNodeData_Clusterone
from EdgeData import EdgeType
from AlgorithmName import AlgorithmName
from ClusteringVisualizer import ClusteringVisualizer
from ClusteringPrinter import ClusteringPrinter
from EvaluationData_Clusterone import EvaluationData_Clusterone

class Phase2Data_Clusterone(Phase2Data):
    def __init__(self, graphdata, configdata, cnodes_dict, next_cluster_label, num_clusters):
        super(Phase2Data_Clusterone, self).__init__(graphdata, configdata, -1, cnodes_dict, next_cluster_label, num_clusters)

        #evaluation related data
        self.phase = 2
        self.phase2_evaluation_data = None

        self.OVERLAP_THRESHOLD = self.configdata.overlap_threshold
        self.DENSITY_THRESHOLD = self.configdata.density_threshold

    #1. Construct an overlap matrix among all cnodes from phase1
    #2. Find out group of cnodes (could be more that a pair)
    #that are connected by one edge or a (path of edges??).
    #Merge such cnodes to form complexes.
    #If a group has no connection to other groups, it is promoted to
    #being a final cluster.

    def initialize_phase(self):
        self.configdata.logger.debug("Debugging from inside initialize_phase method of Phase2Data_Clusterone.")

        #Calculate inter cluster overlap matrix
        self.calculate_c_SM()

        #sort the overlap matrix
        #self.sort_c_SM()

    def execute_phase(self):
        self.configdata.logger.debug("Debugging from inside execute_phase method of Phase2Data_Clusterone.")
        self.clusterone_phase2_execute()

    def prune_phase(self):
        self.configdata.logger.debug("Debugging from inside prune_phae of Phase2Data_Clusterone")
        for cnode_id, cnode_data in self.cnodes_dict.items():
            if cnode_data.active == True:
                if cnode_data.isDirty == True:
                    cnode_data.calculate_cnode_secondary_fields()
                if cnode_data.weighted_struct_density < self.DENSITY_THRESHOLD:
                    self.deactivate_cnode(cnode_data)

    def evaluate_phase(self):
        self.configdata.logger.debug("Debugging from inside evaluate_phase method of Phase2Data_Clusterone.")
        self.phase1_evaluation_data = EvaluationData_Clusterone(self.graphdata, self.configdata, self.K, self.phase, self.num_clusters, self.cnodes_dict, AlgorithmName.Clusterone)
        self.phase1_evaluation_data.calculate_evaluation_measures_for_one_K()

    def visualize_phase(self):
        self.configdata.logger.debug("Debugging from inside visualize_phase method of Phase2Data_Clusterone.")
        cluster_label_list = self.generate_cluster_label_list(AlgorithmName.Clusterone)

        #Graph of clusters
        visualizer = ClusteringVisualizer(self.graphdata, self.configdata, self.K, self.phase, self.num_clusters, cluster_label_list, AlgorithmName.Clusterone)
        visualizer.visualize_clusters()
        #visualizer.visualize_specific_clusters([0,5,3,7])
        #For Krogan full for Clusterone CP.
        #visualizer.visualize_specific_clusters([26, 50, 29, -3])
        #For A2Zsim
        visualizer.visualize_specific_clusters([0, 3, 4, 6, -3])
        #For A2Zsim1
        #visualizer.visualize_specific_clusters([1, 2, 4, 5, 9, -2])
        #For A2Zsim1
        #visualizer.visualize_specific_clusters([0, 3, 5, 9, -2])
        #For A2Zsim1
        #visualizer.visualize_specific_clusters([2, 6, 9, 4, -2])
        #print clusters in csv format
        printer = ClusteringPrinter(self.configdata, self.graphdata, self.phase, self.K, cluster_label_list,  AlgorithmName.Clusterone)
        printer.printClusters()

    #Method to calculate the overlap matrix
    def calculate_c_SM(self):
        self.configdata.logger.debug("Debugging from inside calculate_c_SM method.")

        #initialize c_SM
        self.c_SM = [[-1] * self.num_clusters for i in range(self.num_clusters)]

        for i in range(0, self.next_cluster_label-1):
            for j in range(i+1, self.next_cluster_label):
                cnode_i = self.cnodes_dict[i]
                cnode_j = self.cnodes_dict[j]

                overlapij_numerator = (float) ((len(cnode_i.node_set.intersection(cnode_j.node_set)))*(len(cnode_i.node_set.intersection(cnode_j.node_set))))
                overlapij_denominator = (float)(cnode_i.num_nodes * cnode_j.num_nodes)
                self.c_SM[i][j] = overlapij_numerator/overlapij_denominator
                self.c_SM[j][i] = self.c_SM[i][j]

    #Method for execute phase of clusterone
    def clusterone_phase2_execute(self):
        self.configdata.logger.debug("Debugging from inside clusterone_phase2_execute method.")
        #Create a dictionary of sets containing set of cnodes to be
        #merged together based upon the overlap matrix.
        sets_dict = self.create_merger_set_dict()

        #merge the cnodes in the sets defined by sets_dict
        #all at once.
        for set_num, merger_set in sets_dict.items():
            #print("set number")
            #print(str(set_num))
            #print("merger sets")
            self.merge_cnodes(merger_set)
            #for cnode_i in merger_set:
                #print(str(cnode_i))



    #Method to create a dictionary of sets containing
    #set of cnodes to be merged together based upon
    # the overlap matrix.
    def create_merger_set_dict(self):
        self.configdata.logger.debug("Debugging from inside create_merger_set_dict method.")
        membership_dict = {}
        sets_dict = {}
        next_available_set_num = 0
        set_i = -1
        for cnode_i in range(0, self.num_clusters):
            #Decide self set membership of cnode_i
            if(cnode_i in membership_dict):
                #Get the set to which node_i currently belongs to
                set_i = membership_dict[cnode_i]
            else:
                membership_dict[cnode_i] = next_available_set_num
                set_i = next_available_set_num
                merger_sets = set()
                merger_sets.add(cnode_i)
                sets_dict[set_i] = merger_sets
                next_available_set_num = next_available_set_num + 1

            #Based upon self set membership,
            #update the set membership of all its cnode neighbors
            #where overlap>=0.8
            for cnode_j in range(0, self.num_clusters):
                if(self.c_SM[cnode_i][cnode_j] >= self.OVERLAP_THRESHOLD):
                    if(cnode_j in membership_dict):
                        set_j = membership_dict[cnode_j]
                        if set_i != set_j:
                            merger_sets_j = sets_dict[set_j]
                            for cnode_k in merger_sets_j:
                                membership_dict[cnode_k] = set_i
                                #merge set_j into set_i
                                sets_dict[set_i].add(cnode_k)
                            #merge set_j into set_i
                            #set_i = set_i.union(set_j)
                            del sets_dict[set_j]
                    else:
                        membership_dict[cnode_j] = set_i
                        sets_dict[set_i].add(cnode_j)

        return sets_dict

    #Merge a set of cnodes into a new cnode.
    def merge_cnodes(self, merger_set):
        self.configdata.logger.debug("Debugging from inside merge_cnodes method.")
        #no merging needed for a single cnode.
        if(len(merger_set) != 1):
            #create merged cnode
            cnode_data_merged = self.create_merged_cnode(merger_set)

            #No need to update phase 2 matrices here as all the mergings are taking place all at once.

            #deactivate merging cnodes and remove them from self.cnodes_dict.
            self.deactivate_merging_cnodes(merger_set)

            #Add the new cnode object to cnodes_dict
            self.cnodes_dict[cnode_data_merged.cnode_id] = cnode_data_merged

            self.update_clustering_statistics(len(merger_set))

    #Overriding base class method
    #Method to create a new cnode upon merging of cnodes in merger_set
    def create_merged_cnode(self, merger_set):
        self.configdata.logger.debug("Debugging from inside create_merged_cnode method.")
        #Create a new cnode object
        #cluster_label_new = self.next_cluster_label
        cluster_label_new = min(list(merger_set))

        #create new merged cnode
        cnode_data_merged = CNodeData_Clusterone(cluster_label_new, -1, -1, -1, self.graphdata, self.configdata)


       #Add nodes to new cnode
        self.add_nodes_to_merged_cnode(merger_set, cnode_data_merged)

        #Add edges to new cnode
        #primary
        self.add_edges_to_merged_cnode(merger_set, cnode_data_merged, EdgeType.primary)

        #Run the clustering statistics for the new cnode
        #this also sets the active and dirty flags.
        cnode_data_merged.calculate_cnode_secondary_fields()

        return cnode_data_merged

    #Method to deactivate the merging cnodes.
    def deactivate_merging_cnodes(self, merger_set):
        for cnode_i in merger_set:
            cnode_data_i = self.cnodes_dict[cnode_i]
            self.deactivate_cnode(cnode_data_i)

            #Remove cnode_i from cnodes_dict
            del self.cnodes_dict[cnode_i]

    #Method to update clustering statistics after each merging in phase 2
    def update_clustering_statistics(self, size_set):
        self.num_clusters = self.num_clusters - size_set + 1
        self.next_cluster_label = self.next_cluster_label + 1

    #Method to add nodes to merged cnode
    def add_nodes_to_merged_cnode(self, merger_set, cnode_data_merged):
        self.configdata.logger.debug("Debugging from inside add_nodes_to_merged_cnode method.")
        #cnode_data_merged = self.cnodes_dict[cluster_label_new]
        cluster_label_new = cnode_data_merged.cnode_id
        for cnode_i in merger_set:
            cnode_data_i = self.cnodes_dict[cnode_i]
            cnode_data_merged.node_set = cnode_data_merged.node_set | cnode_data_i.node_set
           #Update cluster membership of each node in the new nodeset
            for node_id in cnode_data_i.node_set:
                node = self.graphdata.node_dict[node_id]
                del node.clusterone_clabel_dict[cnode_i]
                node.clusterone_clabel_dict[cluster_label_new] = cnode_i
                          #For each node (in phase 2), now the cluster center
                          #holds the cnode_id they come from in the big merged
                          #cnode. In phase 2, it was holding the actual cluster
                          #center node_id.

    # #Method to add edges to merged cnode
    # def add_edges_to_merged_cnode(self, merger_set, cnode_data_merged, edge_type):
    #     self.configdata.logger.debug("Debugging from inside add_edges_to_merged_cnode.")
    #     #cnode_data_merged = self.cnodes_dict[cluster_label_new]
    #     cluster_label_new = cnode_data_merged.cnode_id
    #     other_set = merger_set.copy()
    #     temp_set = set()
    #     for cnode_i in merger_set:
    #         cnode_data_i = self.cnodes_dict[cnode_i]
    #         cnode_data_merged.internal_edge_dict[edge_type].update(cnode_data_i.internal_edge_dict[edge_type])
    #         cnode_data_merged.external_edge_dict[edge_type].update(cnode_data_i.external_edge_dict[edge_type])
    #
    #         other_set.discard(cnode_i)
    #         for cnode_j in other_set:
    #             cnode_data_j = self.cnodes_dict[cnode_j]
    #             temp_set = temp_set | self.get_edgeset_between_cnodes(cnode_data_i, cnode_data_j, EdgeType.primary)
    #
    #     cnode_data_merged.internal_edge_dict[edge_type].update(temp_set)
    #     cnode_data_merged.external_edge_dict[edge_type].difference_update(temp_set)

    #Method to add edges to merged cnode
    def add_edges_to_merged_cnode(self, merger_set, cnode_data_merged, edge_type):
        self.configdata.logger.debug("Debugging from inside add_edges_to_merged_cnode.")
        #cnode_data_merged = self.cnodes_dict[cluster_label_new]
        cluster_label_new = cnode_data_merged.cnode_id
        other_set = merger_set.copy()
        temp_set = set()
        for cnode_i in merger_set:
            cnode_data_i = self.cnodes_dict[cnode_i]
            cnode_data_merged.internal_edge_dict[edge_type].update(cnode_data_i.internal_edge_dict[edge_type])
            cnode_data_merged.external_edge_dict[edge_type].update(cnode_data_i.external_edge_dict[edge_type])


        #cnode_data_merged.internal_edge_dict[edge_type].update(temp_set)
        nodeset = cnode_data_merged.external_edge_dict[edge_type].intersection(cnode_data_merged.internal_edge_dict[edge_type])
        #if(len(nodeset) != 0):
        #    print("Set intersection between internal and external edgeset is not null.")
        cnode_data_merged.external_edge_dict[edge_type].difference_update(cnode_data_merged.internal_edge_dict[edge_type])