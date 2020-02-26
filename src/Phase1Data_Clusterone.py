__author__ = 'divya'

from Phase1Data import Phase1Data
from AlgorithmName import AlgorithmName
from EdgeData import EdgeType
from EvaluationData_Clusterone import EvaluationData_Clusterone
from ClusteringVisualizer import ClusteringVisualizer
from ClusteringPrinter import ClusteringPrinter

from CNodeData_Clusterone import CNodeData_Clusterone

class Phase1Data_Clusterone(Phase1Data):
    def __init__(self, graphdata, configdata):
        K = -1
        super(Phase1Data_Clusterone, self).__init__(graphdata, configdata, K)

        self.radius_dict = {}
        self.cluster_initiator_list = []
        #Evaluation related data
        self.phase = 1
        self.phase1_evaluation_data = None
        self.outlier_nodeset = set()

    #Method to initialize phase 1 of clusterone
    def initialize_phase(self):
        #1. Calculate radius for each node.
        #2. Based upon radius, calculate the cluster initiator order.
        self.configdata.logger.debug("Debugging from inside initialize_phase method")

        #Reset all cluster labels of nodes to -1
        self.initialize_node_cluster_labels()

        #Calculate each node's degree and radius list
        self.calculate_node_statistics()

        #Calculate cluster initiator order using radius
        self.calculate_cluster_initiator_order()

    #Method to execute phase 1 of clusterone
    def execute_phase(self):
        self.configdata.logger.debug("Debugging from inside the execute_phase method")

        #execute phase
        self.clusterone_phase1_execute()

    def evaluate_phase(self):
        self.phase1_evaluation_data = EvaluationData_Clusterone(self.graphdata, self.configdata, self.K, self.phase, self.num_clusters, self.cnodes_dict, AlgorithmName.Clusterone)
        self.phase1_evaluation_data.calculate_evaluation_measures_for_one_K()


    def visualize_phase(self):
        cluster_label_list = self.generate_cluster_label_list(AlgorithmName.Clusterone)

        #Graph of clusters
        visualizer = ClusteringVisualizer(self.graphdata, self.configdata, self.K, self.phase, self.num_clusters, cluster_label_list, AlgorithmName.Clusterone)
        visualizer.visualize_clusters()
        visualizer.visualize_specific_clusters([2,3])

        #print clusters in csv format
        printer = ClusteringPrinter(self.configdata, self.graphdata, self.phase, self.K, cluster_label_list, AlgorithmName.Clusterone)
        printer.printClusters()

    #Calculate Node statistics
    def calculate_node_statistics(self):
        self.configdata.logger.debug("Debugging from inside calculate_node_statistics method")
        for i in range(self.graphdata.num_nodes):
            #Calculate degree of each node
            self.graphdata.node_dict[i].calculate_primary_degree()
            self.graphdata.node_dict[i].calculate_primary_weighted_degree()
            #Calculate MKNN_radius of each node.
            self.calculate_node_radius(i)

    #Calculate node radius as its degree
    def calculate_node_radius(self, node_id):
        self.configdata.logger.debug("Debbuging from inside calculate_node_radius method")
        #self.radius_dict[node_id] = self.graphdata.node_dict[node_id].degree
        self.radius_dict[node_id] = self.graphdata.node_dict[node_id].weighted_degree


    #######################################################
    #Initialize: Calculate ClusterInitiator(CI) matrix
    #This matrix contains and ordered dictionary of nodes
    #based upon their radius
    #######################################################
    def calculate_cluster_initiator_order(self):
        #sort the node_dict, based upon the radius value of its objects.
        self.cluster_initiator_list = [key for (key, value) in sorted(iter(self.radius_dict.items()), reverse=True, key=lambda k_v: (k_v[1],k_v[0]))]

    #This method implements the execute phase of clusterone
    def clusterone_phase1_execute(self):
        #1. Access the nodes in cluster initiator order
        #Check for greedy growth:
        self.configdata.logger.debug("Debugging from inside clusterone_phase1_execute method")

        c_label = 0
        for i in range(self.graphdata.num_nodes):
            c_initiator = self.cluster_initiator_list[i]
            c_initiator_node = self.graphdata.node_dict[c_initiator]

            self.configdata.logger.debug("Initiator:")
            print("Initiator:" + str(self.graphdata.node_dict[c_initiator].node_code));
            self.configdata.logger.debug(c_initiator)
            self.configdata.logger.debug(self.graphdata.node_dict[c_initiator].node_code)

            if(len(c_initiator_node.clusterone_clabel_dict) == 0):
                self.configdata.logger.debug("Initiator's cluster label is not yet set,"
                                             " so it will initiate the clustering growth"
                                             " process:")
                #print("Initiator:")
                #print(str(self.graphdata.node_dict[c_initiator].node_code))

                #Update cluster membership for c_initiator (algorithm_name = 1)
                self.update_node_cluster_membership(c_initiator_node, -1, self.next_cluster_label, c_initiator, AlgorithmName.Clusterone)

                #Update cluster label
                clabel_current = self.next_cluster_label
                self.next_cluster_label = self.next_cluster_label+1

                #update number of clusters
                self.num_clusters = self.num_clusters + 1

                #Greedy Growth process
                #0. Let Vt be the set of vertices before the start of growth process
                #for cnode_initiator
                #1. Calculate Cohesion of cnode for clabel_current
                #2. Get nodes incident on at least one external edge of cnode_initiator
                #3. For each such vertex
                    #a. check cohesion change on add_vertex(node, cnode)
                    #b. Choose the vertex with the maximum increase in cohesion on addition.
                    #c. If no increase in cohesion:??: Nothing
                #4. Get a set of nodes internal to cnode but incident on one
                #of the external edges
                #5. For each such vertex
                    #a. Check cohesion change on remove_vertex(node, cnode)
                    #b. Choose the vertex which cause maximum increase in cohesion on removal.
                    #c, What if no increase in cohesion on node removal?: Nothing
                    #d. Here caution to be taken to make sure that if the cluster initiator node
                    #itself gets removed, then what?
                #6. Decide whether to add or remove a node from the cnode.
                #6. Let Vt+1 be the set of vertices now in cnode_initiator
                #7. If Vt = Vt+1, stop the iteration, move to the next cluster initiator
                #else continue the greedy growth process with the current initiator itself.

                cnode_data_current = self.cnodes_dict[clabel_current]
                #nodeset_current = cnode_data_current.node_set

                continue_growth_flag = True

                while continue_growth_flag == True:
                    #calculate current cohesion
                    cnode_data_current.calculate_cnode_secondary_fields()
                    cohesion_current = cnode_data_current.cohesion

                    #Get Prospective nodesets for node addition and node removal
                    (nodeset_prospective_add, nodeset_prospective_remove) = self.get_prospective_node_sets(cnode_data_current)

                    #Check for node addition
                    cohesion_max_increase = cohesion_current
                    (nodeid_chosen_to_add, cohesion_max_increase) = self.check_for_node_addition(cnode_data_current, cohesion_max_increase, nodeset_prospective_add)

                    #Check for node removal
                    cohesion_max_decrease = cohesion_max_increase
                    (nodeid_chosen_to_add, nodeid_chosen_to_remove, cohesion_max_decrease) = self.check_for_node_removal(cnode_data_current, cohesion_max_decrease, nodeset_prospective_remove, nodeid_chosen_to_add)

                    #Line below only for experimenting
                    #nodeid_chosen_to_remove = -1

                    #Check the outcome: whether to add a node or delete a node.
                    if nodeid_chosen_to_remove != -1:
                        #remove node from cnode

                        self.greedy_growth_remove_node_from_cnode(nodeid_chosen_to_remove, clabel_current, c_initiator_node.node_id)

                    elif nodeid_chosen_to_add != -1:
                        #Add node to cnode
                        self.greedy_growth_add_node_to_cnode(nodeid_chosen_to_add, clabel_current)

                    else:
                        #stop the growth process
                        continue_growth_flag = False

        # print("num clusters after phase 1")
        # print(str(self.num_clusters))
        # print("length of cnodes_dict after phase 1")
        # print(str(len(self.cnodes_dict)))

    # #Method to get the propsective node_set for growthphase
    # def get_prospective_node_sets(self, cnode_data_current):
    #
    #     nodeset_current = cnode_data_current.node_set
    #
    #     #Get nodes incident on at least one external edge of cnode_current for addition
    #     #Plus, get nodes incident on at least one boundar vertex for removal
    #     external_edgeset = cnode_data_current.external_edge_dict[EdgeType.primary]
    #
    #     nodeset_prospective = set()
    #     for edge_id in external_edgeset:
    #         edge_data = self.graphdata.edge_dict[edge_id]
    #         nodeset_prospective.add(edge_data.node1_id)
    #         nodeset_prospective.add(edge_data.node2_id)
    #
    #
    #     nodeset_prospective_add = nodeset_prospective.difference(nodeset_current)
    #     nodeset_prospective_remove = nodeset_prospective.intersection(nodeset_current)
    #
    #     return (nodeset_prospective_add, nodeset_prospective_remove)

    #Method to get the propsective node_set for growthphase
    def get_prospective_node_sets(self, cnode_data_current):
        self.configdata.logger.debug("Debugging from inside get_prospective_node_sets method of Phase1Data_Clusterone.")
        cnode_nodeset_current = cnode_data_current.node_set

        #Get nodes incident on at least one external edge of cnode_current for addition
        #Plus, get nodes incident on at least one boundar vertex for removal
        cnode_edgeset_external = cnode_data_current.external_edge_dict[EdgeType.primary]

        nodeset_prospective = set()
        for edge_id in cnode_edgeset_external:
            edge_data = self.graphdata.edge_dict[edge_id]
            nodeset_prospective.add(edge_data.node1_id)
            nodeset_prospective.add(edge_data.node2_id)


        nodeset_prospective_add = nodeset_prospective.difference(cnode_nodeset_current)
        nodeset_prospective_remove = nodeset_prospective.intersection(cnode_nodeset_current)

        return (nodeset_prospective_add, nodeset_prospective_remove)


    #Check the possibility of adding a vertex to a growing cluster
    def check_for_node_addition(self, cnode_data_current, cohesion_max_increase,  nodeset_prospective_add):
        self.configdata.logger.debug("Debugging from inside check_for_node_addition method of Phase1Data_Clusterone.")
        nodeid_chosen_to_add = -1

        #Check for node addition
        #cohesion_max_increase = cohesion_current
        for nodeid_prospective_add in nodeset_prospective_add:
            #Below if only for testing non overlapping clusterone.
            #if(len(self.graphdata.node_dict[nodeid_prospective_add].clusterone_clabel_dict) == 0):
            cohesion_prospective_add = cnode_data_current.calculate_cohesion_on_node_addition(nodeid_prospective_add)
            if cohesion_prospective_add > cohesion_max_increase:
                nodeid_chosen_to_add = nodeid_prospective_add
                cohesion_max_increase = cohesion_prospective_add

        return (nodeid_chosen_to_add, cohesion_max_increase)

    #Check the possibility of removing a vertex from a growing cluster
    def check_for_node_removal(self, cnode_data_current, cohesion_max_decrease, nodeset_prospective_remove, nodeid_chosen_to_add):
        self.configdata.logger.debug("Debugging from inside check_for_node_removal method of Phase1Data_Clusterone.")
        nodeid_chosen_to_remove = -1
        #Check for node removal
        #cohesion_max_decrease = cohesion_max_increase
        for nodeid_prospective_remove in nodeset_prospective_remove:
            cohesion_prospective_remove = cnode_data_current.calculate_cohesion_on_node_removal(nodeid_prospective_remove)
            if cohesion_prospective_remove > cohesion_max_decrease:
                nodeid_chosen_to_remove = nodeid_prospective_remove
                nodeid_chosen_to_add = -1
                cohesion_max_decrease = cohesion_prospective_remove

        return(nodeid_chosen_to_add, nodeid_chosen_to_remove, cohesion_max_decrease)

    #Method to add remove node from a cnode during greedy growth process
    def greedy_growth_remove_node_from_cnode(self, nodeid_chosen_to_remove, clabel_current, c_initiator_node_id):
        self.configdata.logger.debug("Debugging from inside greedy_growth_remove_node_from_cnode method of Phase1Data_Clusterone.")
        #remove node form cnode
        self.update_node_cluster_membership(self.graphdata.node_dict[nodeid_chosen_to_remove], clabel_current, -1, -1, AlgorithmName.Clusterone)
        #What if c_initiator_node gets removed?..need to consider it in the end
        #print("Remove:")
        #print(str(self.graphdata.node_dict[nodeid_chosen_to_remove].node_code))

        if nodeid_chosen_to_remove == c_initiator_node_id:
            self.outlier_nodeset.add(nodeid_chosen_to_remove)

    #Method to add node to a cnode during greedy growth process
    def greedy_growth_add_node_to_cnode(self, nodeid_chosen_to_add, clabel_current):
        self.configdata.logger.debug("Debugging from inside greedy_growht_add_node_to_cnode method of Phase1Data_Clusterone.")
        self.update_node_cluster_membership(self.graphdata.node_dict[nodeid_chosen_to_add], -1, clabel_current, -1, AlgorithmName.Clusterone)
        #print("Add:")
        #print(str(self.graphdata.node_dict[nodeid_chosen_to_add].node_code))
        #print("Testing class deriving")
        #print(self.cnodes_dict[clabel_current].cnode_mean_lower_bound)

    #Overriding base class method
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
            cnode = CNodeData_Clusterone(cluster_label, -1, -1, cluster_center, self.graphdata, self.configdata)

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
