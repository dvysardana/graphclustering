__author__ = 'divya'

from Phase1Data_Clusterone import Phase1Data_Clusterone
from AlgorithmName import AlgorithmName
from EdgeData import EdgeType

from CNodeData_Clusterone_CP import CNodeData_Clusterone_CP
from EvaluationData_Clusterone_CP import EvaluationData_Clusterone_CP

class Phase1Data_Clusterone_CP(Phase1Data_Clusterone):
    def __init__(self, graphdata, configdata):
        super(Phase1Data_Clusterone_CP, self).__init__(graphdata, configdata)
        self.NODE_PENALTY_2 = configdata.node_penalty_2
        self.MEAN_DIFF = configdata.mean_diff
        self.periphery_ycohesion_nsd_dict = dict() #nodes which satisfy cohesion, not sd
        self.periphery_ncohesion_ysd_dict = dict() #nodes which dont satisfy cohesion, satisfy sd
        self.periphery_ncohesion_nsd_low_dict = dict() #nodes which dont satisfy cohesion and sd, lower mean than core
        self.periphery_ncohesion_nsd_high_dict = dict() #nodes which dont satisfy cohesion and sd, higher mean than core

    def evaluate_phase(self):
        self.phase1_evaluation_data = EvaluationData_Clusterone_CP(self.graphdata, self.configdata, self.K, self.phase, self.num_clusters, self.cnodes_dict, None, AlgorithmName.Clusterone)
        self.phase1_evaluation_data.calculate_evaluation_measures_for_one_K()

    #This method implements the execute phase of clusterone
    def clusterone_phase1_execute(self):
        #1. Access the nodes in cluster initiator order
        #Check for greedy growth:
        self.configdata.logger.debug("Debugging from inside clusterone_phase1_execute method")

        c_label = 0
        #Order in which a node is added to a cnode
        cnode_inclusion_order = 0
        for i in range(self.graphdata.num_nodes):
            c_initiator = self.cluster_initiator_list[i]
            c_initiator_node = self.graphdata.node_dict[c_initiator]

            self.configdata.logger.debug("Initiator:")
            self.configdata.logger.debug(c_initiator)
            self.configdata.logger.debug(self.graphdata.node_dict[c_initiator].node_code)

            core_cnode_dict = dict()
            core_node_set = set()

            if(len(c_initiator_node.clusterone_clabel_dict) == 0):
                self.configdata.logger.debug("Initiator's cluster label is not yet set,"
                                             " so it will initiate the clustering growth"
                                             " process:")
                print("Initiator:")
                print(str(self.graphdata.node_dict[c_initiator].node_code))

                #Update cluster membership for c_initiator (algorithm_name = 1)
                self.update_node_cluster_membership(c_initiator_node, -1, self.next_cluster_label, c_initiator, AlgorithmName.Clusterone)


                #Update cluster label
                clabel_current = self.next_cluster_label
                self.next_cluster_label = self.next_cluster_label+1

                #Maintain the order in which the cnode was added.
                self.cnodes_dict[clabel_current].cnode_node_dict[c_initiator] = cnode_inclusion_order
                cnode_inclusion_order = cnode_inclusion_order + 1

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

                #Get the core nodes for which the initiator is a boundary node
                (core_cnode_dict, core_node_set) = self.is_node_in_core_boundary(c_initiator, core_cnode_dict, core_node_set)
                print("Core node set")
                self.helper.print_set_codes(core_node_set, self.graphdata.node_dict)

                #Nodeset to hold nodes which have been rejected for addition
                #because of non matching standard deviation in one of the
                #previous iterations.
                #These nodes wont be considered again in the future iterations
                #even if they satisfy the cohesion criterion.

                #nodes which satisfied cohesion criterion
                #but not the refined set. They, however,
                #satisfied the overlapping set criterion.
                rejected_nodeset_A = set()

                #nodes which satisfied cohesion criterion,
                #nut not in refined set or even the overlapping set
                rejected_nodeset_B = set()

                while continue_growth_flag == True:
                    #calculate current cohesion
                    cnode_data_current.calculate_cnode_secondary_fields()
                    cohesion_current = cnode_data_current.cohesion

                    #Get Prospective nodesets for node addition and node removal
                    (nodeset_prospective_add, nodeset_prospective_remove) = self.get_prospective_node_sets(cnode_data_current)

                    #Remove the coe node set from nodeset_prospective_add
                    nodeset_prospective_add = nodeset_prospective_add.difference(core_node_set)

                    #Subtract the rejected_nodeset from prospective_nodeset
                    #nodeset_prospective_add.difference_update(rejected_nodeset_A)
                    #nodeset_prospective_add.difference_update(rejected_nodeset_B)

                    #Refine the prospective nodeset in order to take edge weights into account
                    #ALso, generate a prospective overlapping nodeset for this cnode
                    (refined_nodeset_prospective_add, nodeset_prospective_overlapping) = self.refine_nodeset_prospective_add(cnode_data_current, nodeset_prospective_add)

                    #Check for node addition
                    cohesion_max_increase = cohesion_current
                    (nodeid_chosen_to_add, cohesion_max_increase) = self.check_for_node_addition(cnode_data_current, cohesion_max_increase, nodeset_prospective_add)

                    #Check for node removal
                    cohesion_max_decrease = cohesion_max_increase
                    (nodeid_chosen_to_add, nodeid_chosen_to_remove, cohesion_max_decrease) = self.check_for_node_removal(cnode_data_current, cohesion_max_decrease, nodeset_prospective_remove, nodeid_chosen_to_add)

                    #Line below only for experimenting.
                    #only adding nodes for now in the experiment.
                    nodeid_chosen_to_remove = -1

                    #Check the outcome: whether to add a node or delete a node.
                    if nodeid_chosen_to_remove != -1:
                        #remove node from cnode
                        self.greedy_growth_remove_node_from_cnode(nodeid_chosen_to_remove, clabel_current, c_initiator_node.node_id)

                        (core_cnode_dict, core_node_set) = self.remove_core_nodes_for_boundary_node(nodeid_chosen_to_remove, core_cnode_dict, core_node_set)

                    elif nodeid_chosen_to_add != -1:

                        self.greedy_growth_add_node_to_cnode(nodeid_chosen_to_add, clabel_current)

                        #Maintain the order in which the cnode was added.
                        self.cnodes_dict[clabel_current].cnode_node_dict[nodeid_chosen_to_add] = cnode_inclusion_order
                        cnode_inclusion_order = cnode_inclusion_order + 1

                        #Check if node is a boundary node for any cores
                        (core_cnode_dict, core_node_set) = self.is_node_in_core_boundary(nodeid_chosen_to_add, core_cnode_dict, core_node_set)


                        ##############################################
                        #Code being added for core periphery increment
                        ##############################################
                        #Check of the node chosen to add as per cohesion criterion
                        #also satisfies the standard deviation criterion


                        # if nodeid_chosen_to_add in refined_nodeset_prospective_add:
                        #     self.update_node_cluster_membership(self.graphdata.node_dict[nodeid_chosen_to_add], -1, clabel_current, -1, AlgorithmName.Clusterone)
                        #     self.configdata.logger.debug("Add this node:")
                        #     self.configdata.logger.debug(str(self.graphdata.node_dict[nodeid_chosen_to_add].node_code))
                        # #else check if node qualifies to be an overlapping node.
                        # elif nodeid_chosen_to_add in nodeset_prospective_overlapping:
                        #     cnode_data_current.overlapping_node_dict[nodeid_chosen_to_add] = 0
                        #     self.configdata.logger.debug("Put this node to overlapping nodeset of the cnode.")
                        #     #Put this node in rejected_nodeset
                        #     rejected_nodeset_A.add(nodeid_chosen_to_add)
                        # #this case is blank for now, later, could extract periphery nodes from here.
                        # else:
                        #     self.configdata.logger.debug("Both nodeids chosen to add and remove = -1")
                        #     rejected_nodeset_B.add(nodeid_chosen_to_add)


                        # ##############################################

                        # self.update_node_cluster_membership(self.graphdata.node_dict[nodeid_chosen_to_add], -1, clabel_current, -1, AlgorithmName.Clusterone)
                        # print("Add:")
                        # print(str(self.graphdata.node_dict[nodeid_chosen_to_add].node_code))

                    else:

                        #Prune the cnode based upon standard deviation
                        #set to consider for pruning:
                        #self.prune_cnode(cnode_data_current, nodeset_prospective_remove, clabel_current, c_initiator_node.node_id)

                        #Calculate the prospective nodeset_add again and remove pruned nodes from it
                        (nodeset_prospective_add, nodeset_prospective_remove) = self.get_prospective_node_sets(cnode_data_current)
                        nodeset_prospective_add.difference_update(set(cnode_data_current.boundary_node_dict_ycohesion_nsd.keys()))
                     #Use the latest prospective nodeset_add to identify different types of boundary nodes.
                        self.cnode_extract_boundary_nodes(cnode_data_current, nodeset_prospective_add, clabel_current)

                        #stop the growth process
                        continue_growth_flag = False

        # print("num clusters after phase 1")
        # print(str(self.num_clusters))
        # print("length of cnodes_dict after phase 1")
        # print(str(len(self.cnodes_dict)))





    # #Method to get the propsective node_set for growthphase
    # def get_prospective_node_sets(self, cnode_data_current):
    #
    #     cnode_nodeset_current = cnode_data_current.node_set
    #
    #     #Get nodes incident on at least one external edge of cnode_current for addition
    #     #Plus, get nodes incident on at least one boundar vertex for removal
    #     cnode_edgeset_external = cnode_data_current.external_edge_dict[EdgeType.primary]
    #
    #     nodeset_prospective = set()
    #     for edge_id in cnode_edgeset_external:
    #         edge_data = self.graphdata.edge_dict[edge_id]
    #         nodeset_prospective.add(edge_data.node1_id)
    #         nodeset_prospective.add(edge_data.node2_id)
    #
    #
    #     nodeset_prospective_add = nodeset_prospective.difference(cnode_nodeset_current)
    #     nodeset_prospective_remove = nodeset_prospective.intersection(cnode_nodeset_current)
    #
    #     return (nodeset_prospective_add, nodeset_prospective_remove)

    #Categorize the prospective nodeset as
    # short: (Nodes which contribute majority of short internal edges)
    #long: (Nodes which contribute majority of long internal edges)
    #inrange: (Nodes which contribute majority of inrange internal edges)
    #overlapping: (Nodes whose external edges are mostly long or mostly short but not mostly inrange)

    #Method to calculate a refined_prospective_nodeset based upon edge_weight criteria.
    #Also, generate a prospective_nodeset_overlapping
    def refine_nodeset_prospective_add(self, cnode_data_current, nodeset_prospective_add):
        self.configdata.logger.debug("Debugging from inside refine_nodeset_prospective_add  method of Phase1Data_Clusterone_CP.")
        cnode_nodeset_current = cnode_data_current.node_set
        cnode_edgeset_external = cnode_data_current.external_edge_dict[EdgeType.primary]

        #Calculate upper and lower bounds for categorizing edge weights
        #(UPPER_BOUND, LOWER_BOUND) = self.calculate_cnode_edge_weight_bounds(cnode_data_current)
        UPPER_BOUND = cnode_data_current.cnode_mean_upper_bound
        LOWER_BOUND = cnode_data_current.cnode_mean_lower_bound

        #Generate the refined prospective nodeset_add and prospective overlapping nodeset
        refined_prospective_nodeset_add = set()
        prospective_nodeset_overlapping = set()

        for node_id in nodeset_prospective_add:
            #Get the edgeset around a node
            node_edgeset = self.graphdata.node_dict[node_id].node_edges_dict[EdgeType.primary]

            #Get the share of node's edgeset shared with the cnode
            node_edgeset_internal = node_edgeset.intersection(cnode_edgeset_external)

            #Get the share of node's edgeset not shared with the cnode
            node_edgeset_external = node_edgeset.difference(cnode_edgeset_external)

            #Get number of long, short and inrange edges for node_edgeset_internal
            (num_internal_edges_long, num_internal_edges_short, num_internal_edges_inrange) = self.categorize_node_edgeset(node_edgeset_internal, UPPER_BOUND, LOWER_BOUND)

            #Get num of long, short and inrange edges for node_edgeset_external
            (num_external_edges_long, num_external_edges_short, num_external_edges_inrange) = self.categorize_node_edgeset(node_edgeset_external, UPPER_BOUND, LOWER_BOUND)

            #Is node)id eligible for mean_refined nodeset?
            if num_internal_edges_inrange > (num_internal_edges_long + num_internal_edges_short):
                refined_prospective_nodeset_add.add(node_id)

            #Is node id eligible for overlapping_nodeset
            #This node may or may not be refined, but satisfies cohesion.
            if num_external_edges_inrange < (num_external_edges_long + num_external_edges_short):
                prospective_nodeset_overlapping.add(node_id)

        #self.helper.print_set(refined_prospective_nodeset_add)
        return (refined_prospective_nodeset_add, prospective_nodeset_overlapping)

    #Method to calculate the edge weight bounds for a cnode for
    #calculating refined_propective_nodeset_add.
    def calculate_cnode_edge_weight_bounds(self, cnode_data_current):
        self.configdata.logger.debug("Debugging from inside calculate_cnode_edge_weight_bounds  method of Phase1Data_Clusterone_CP.")
        #Get secondary data of current cnode
        cnode_standard_deviation = cnode_data_current.standard_deviation_edges
        cnode_mean = cnode_data_current.mean_edges
        cnode_num_nodes = cnode_data_current.num_nodes

        if cnode_num_nodes != 1:
            #LOWER_BOUND = cnode_mean - cnode_standard_deviation - self.NODE_PENALTY_2 * (1/cnode_num_nodes)
            #UPPER_BOUND = cnode_mean + cnode_standard_deviation + self.NODE_PENALTY_2 * (1/cnode_num_nodes)
            # LOWER_BOUND = cnode_mean - 0.2
            # UPPER_BOUND = cnode_mean + 0.2
            LOWER_BOUND = cnode_mean - self.MEAN_DIFF
            UPPER_BOUND = cnode_mean + self.MEAN_DIFF

        else:
            LOWER_BOUND = 0
            UPPER_BOUND = 1
        return(UPPER_BOUND, LOWER_BOUND)

    #Method to categorize node's edges as being long, short, inrange
    #and return the counts of such categories.
    def categorize_node_edgeset(self, node_edgeset, UPPER_BOUND, LOWER_BOUND):
        self.configdata.logger.debug("Debugging from inside categorize_node_edgeset method of Phase1Data_Clusterone_CP.")
        num_edges_long = sum([1 if self.graphdata.edge_dict[edge_id].edge_weight > UPPER_BOUND else 0 for edge_id in node_edgeset])
        num_edges_short = sum([1 if self.graphdata.edge_dict[edge_id].edge_weight < LOWER_BOUND else 0 for edge_id in node_edgeset])
        num_edges_inrange = len(node_edgeset) - (num_edges_long + num_edges_short)
        # print("Number of long edges")
        # print(str(num_edges_long))
        # print("Number of inrange edges")
        # print(str(num_edges_inrange))
        return (num_edges_long, num_edges_short, num_edges_inrange)


    #Prune a cnode based upon standard deviation criterion.
    def prune_cnode(self, cnode_data_current, nodeset_prospective_remove, clabel_current, c_initiator_node_id):
        self.configdata.logger.debug("Debugging from inside prune_cnode method of Phase1Data_Clusterone_CP.")

        #Get the inclusion orders for nodes in nodeset_prospective_remove
        nodelist_prospective_remove = [(cnode_data_current.cnode_node_dict[node_id], node_id) for node_id in nodeset_prospective_remove]
        #sort nodelist_prospective_remove as per the node inclusion order
        nodelist_prospective_remove.sort()
        #Reverse the list to get the last included node first in the list
        nodelist_prospective_remove.reverse()

        cnode_data_current.calculate_cnode_secondary_fields()
        #cohesion_before = cnode_data_current.cohesion
        for order, nodeid_prospective_remove in nodelist_prospective_remove:
        #for nodeid_prospective_remove in nodeset_prospective_remove:
            #cnode_data_current.calculate_cnode_secondary_fields()
            cohesion_before = cnode_data_current.cohesion
            (prune_decision, mean_diff) = self.check_node_for_pruning(cnode_data_current, nodeid_prospective_remove)
            if(True == prune_decision):
                print("Greedy remove")
                print(str(self.graphdata.node_dict[nodeid_prospective_remove].node_code))
                self.greedy_growth_remove_node_from_cnode(nodeid_prospective_remove, clabel_current, c_initiator_node_id)
                cnode_data_current.calculate_cnode_secondary_fields()
                cohesion_after = cnode_data_current.cohesion
                cohesion_diff = cohesion_before - cohesion_after #It should be a positive entity (based upon algorithm construction)
                periphery_score = self.calculate_periphery_score(cohesion_diff, mean_diff)
                cnode_data_current.boundary_node_dict_ycohesion_nsd[nodeid_prospective_remove] = periphery_score

                #Add node. cnode combination to global periphery dict
                self.add_node_cnode_to_periphery_dict(nodeid_prospective_remove, self.periphery_ycohesion_nsd_dict, clabel_current)
                # if(nodeid_prospective_remove not in self.periphery_ycohesion_nsd_dict):
                #     self.periphery_ycohesion_nsd_dict[nodeid_prospective_remove] = set()
                # self.periphery_ycohesion_nsd_dict[nodeid_prospective_remove].add(clabel_current)


        #cnode_data_current.calculate_cnode_secondary_fields()

    #Method to check if a node can be pruned from a cnode
    def check_node_for_pruning(self, cnode_data_current, nodeid_prospective_remove):
        self.configdata.logger.debug("Debugging from inside check_node_for_pruning method of Phase1Data_Clusterone_CP.")
        node_prospective_remove = self.graphdata.node_dict[nodeid_prospective_remove]

        cnode_internal_edgeset_proposed = cnode_data_current.calculate_internal_edge_set_on_node_removal(node_prospective_remove)
        node_edgeset_proposed_to_remove = cnode_data_current.internal_edge_dict[EdgeType.primary].difference(cnode_internal_edgeset_proposed)
        mean_proposed = cnode_data_current.calculate_mean_edgeset(cnode_internal_edgeset_proposed)
        mean_proposed_to_remove = cnode_data_current.calculate_mean_edgeset(node_edgeset_proposed_to_remove)
        cnode_current_mean = cnode_data_current.mean_edges
        mean_diff = mean_proposed - mean_proposed_to_remove
        if(abs(mean_diff) >= cnode_data_current.cnode_mean_offset and cnode_data_current.num_nodes > 2 and mean_proposed != 0):
            return (True, mean_diff)
        else:
            return (False, mean_diff)


    #Add node, cnode combination to periphery dict
    def add_node_cnode_to_periphery_dict(self, node_id, periphery_dict, cnode_id):
        self.configdata.logger.debug("Debugging from inside add_node_cnode_to_periphery_dict.")
        if(node_id not in periphery_dict):
            periphery_dict[node_id] = set()
        periphery_dict[node_id].add(cnode_id)


    #Method to extract boundary nodes in the neighborhood of a cnode.
    def cnode_extract_boundary_nodes(self, cnode_data_current, nodeset_prospective_add, clabel_current):
        self.configdata.logger.debug("Debugging from inside extract_boundary_nodes method of Phase1Data_Clusterone_CP.")

        cnode_data_current.calculate_cnode_secondary_fields()
        cnode_mean = cnode_data_current.mean_edges
        UPPER_BOUND = cnode_data_current.cnode_mean_upper_bound
        LOWER_BOUND = cnode_data_current.cnode_mean_lower_bound

        for nodeid_prospective_add in nodeset_prospective_add:
            node_edgeset_proposed_to_add = cnode_data_current.external_edge_dict[EdgeType.primary].intersection(self.graphdata.node_dict[nodeid_prospective_add].node_edges_dict[EdgeType.primary])
            mean_proposed_to_add = cnode_data_current.calculate_mean_edgeset(node_edgeset_proposed_to_add)
            mean_difference_1 = cnode_mean - mean_proposed_to_add

            # node_edgeset_not_proposed_to_add = self.graphdata.node_dict[nodeid_prospective_add].node_edges_dict[EdgeType.primary].difference_update(node_edgeset_proposed_to_add)
            # mean_not_proposed_to_add = cnode_data_current.calculate_mean_edgeset(node_edgeset_not_proposed_to_add)
            # mean_difference_2 = cnode_mean - mean_not_proposed_to_add

            periphery_score = self.calculate_periphery_score(0, mean_difference_1)
            #Get number of long, short and inrange edges for node_edgeset_proposed_to_add
            (num_edges_long, num_edges_short, num_edges_inrange) = self.categorize_node_edgeset(node_edgeset_proposed_to_add, UPPER_BOUND, LOWER_BOUND)

            if num_edges_inrange >= (num_edges_short + num_edges_long):
                cnode_data_current.boundary_node_dict_ncohesion_ysd[nodeid_prospective_add] = periphery_score
                #self.periphery_ncohesion_ysd_dict[nodeid_prospective_add] = clabel_current
                self.add_node_cnode_to_periphery_dict(nodeid_prospective_add, self.periphery_ncohesion_ysd_dict, clabel_current)
            elif num_edges_short > (num_edges_long + num_edges_inrange):
                cnode_data_current.boundary_node_dict_ncohesion_nsd_low[nodeid_prospective_add] = periphery_score
                #self.periphery_ncohesion_nsd_low_dict[nodeid_prospective_add] = clabel_current
                self.add_node_cnode_to_periphery_dict(nodeid_prospective_add, self.periphery_ncohesion_nsd_low_dict, clabel_current)
            elif num_edges_long > (num_edges_short + num_edges_short):
                cnode_data_current.boundary_node_dict_ncohesion_nsd_high[nodeid_prospective_add] = periphery_score
                #self.periphery_ncohesion_nsd_high_dict[nodeid_prospective_add] = clabel_current
                self.add_node_cnode_to_periphery_dict(nodeid_prospective_add, self.periphery_ncohesion_nsd_high_dict, clabel_current)


    #Calculate periphery score for a boundary node
    def calculate_periphery_score_1(self, cohesion_diff, mean_diff1, mean_diff2):
        self.configdata.logger.debug("Debugging from inside calculate_periphery_score method of Phase1Data_Clusterone_CP class.")
        periphery_score = (float)(1 + cohesion_diff)/(float)(mean_diff1 + mean_diff2)
        return periphery_score

        #Calculate periphery score for a boundary node
    def calculate_periphery_score_first(self, cohesion_diff, mean_diff):
        self.configdata.logger.debug("Debugging from inside calculate_periphery_score method of Phase1Data_Clusterone_CP class.")
        periphery_score = (float)(1 + cohesion_diff)/(float)(mean_diff)
        return periphery_score

        #Calculate periphery score for a boundary node
    def calculate_periphery_score_2(self, cohesion_diff, mean_diff):
        self.configdata.logger.debug("Debugging from inside calculate_periphery_score method of Phase1Data_Clusterone_CP class.")
        periphery_score = (float)(1 + cohesion_diff)/(float)(abs(mean_diff))
        return periphery_score

        #Calculate periphery score for a boundary node
    def calculate_periphery_score_3(self, cohesion_diff, mean_diff):
        self.configdata.logger.debug("Debugging from inside calculate_periphery_score method of Phase1Data_Clusterone_CP class.")
        periphery_score = (float)(abs(mean_diff))/(float)(1 + cohesion_diff)
        return periphery_score


        #Calculate periphery score for a boundary node
    def calculate_periphery_score(self, cohesion_diff, mean_diff):
        self.configdata.logger.debug("Debugging from inside calculate_periphery_score method of Phase1Data_Clusterone_CP class.")
        periphery_score = (float)(abs(mean_diff))/(float)(1 + 2* cohesion_diff)
        return periphery_score

    #Method to check if a node lies in the boundary of any core cnodes.
    #If yes, return the set of core cnodes as well as the set of nodes in the cores.
    def is_node_in_core_boundary(self, node_id, core_cnode_dict, core_node_set):
        self.configdata.logger.debug("Debugging from inside is_node_in_core_boundary method of Phase1Data_Clusterone_CP class.")

        (core_cnode_dict, core_node_set) = self.is_node_in_boundary_dict(node_id, self.periphery_ycohesion_nsd_dict, core_cnode_dict, core_node_set)
        # if node_id in self.periphery_ycohesion_nsd_dict:
        #     cnode_id = self.periphery_ycohesion_nsd_dict[node_id]
        #     core_cnode_set.add(cnode_id)
        #     core_node_set.update(self.cnodes_dict[cnode_id].node_set)

        (core_cnode_dict, core_node_set) = self.is_node_in_boundary_dict(node_id, self.periphery_ncohesion_nsd_low_dict, core_cnode_dict, core_node_set)
        #
        # if node_id in self.periphery_ncohesion_nsd_low_dict:
        #     cnode_id = self.periphery_ncohesion_nsd_low_dict[node_id]
        #     core_cnode_set.add(cnode_id)
        #     core_node_set.update(self.cnodes_dict[cnode_id].node_set)

        return (core_cnode_dict, core_node_set)

    #Method to check if a node lies in a boundary dict for a core cnode.
    def is_node_in_boundary_dict(self, node_id, boundary_dict, core_cnode_dict, core_node_set):
        self.configdata.logger.debug("Debugging from inside is_node_in_boundary_dict method of Phase1Data_Clusterone_CP class.")

        if node_id in boundary_dict:
            cnode_set = boundary_dict[node_id]
            for cnode_id in cnode_set:
                #cnode_id = boundary_dict[node_id]
                if cnode_id not in core_cnode_dict:
                    core_cnode_dict[cnode_id] = set()
                core_cnode_dict[cnode_id].add(node_id)
                core_node_set.update(self.cnodes_dict[cnode_id].node_set)

        return (core_cnode_dict, core_node_set)

    #Method to remove core nodes for a node currently being removed from a cnode in the growth process
    def remove_core_nodes_for_boundary_node(self, node_id, core_cnode_dict, core_node_set):
        self.configdata.logger.debug("Debugging from inside remove_core_nodes_for_boundary_node method of Phase1Data_Clusterone_CP class.")

        (core_cnode_dict, core_node_set) = self.check_boundary_dict_for_core_removal(node_id, self.periphery_ycohesion_nsd_dict, core_cnode_dict, core_node_set)

        (core_cnode_dict, core_node_set) = self.check_boundary_dict_for_core_removal(node_id, self.periphery_ncohesion_nsd_low_dict, core_cnode_dict, core_node_set)

        return (core_cnode_dict, core_node_set)

    #Method to check if a node exists in boundary dict
    #If it does, remove its core cnodes and corresponding nodes.
    def check_boundary_dict_for_core_removal(self, node_id, boundary_dict, core_cnode_dict, core_node_set):
        self.configdata.logger.debug("Debugging from inside check_boundary_dict_for_core_removal method of Phase1Data_Clusterone_CP class.")

        if node_id in boundary_dict:
            cnode_set = boundary_dict[node_id]
            for cnode_id in cnode_set:
                #cnode_id = boundary_dict[node_id]
                core_cnode_dict[cnode_id].discard(node_id)
                #If node_id was the only node having cnode_id as core
                if(len(core_cnode_dict[cnode_id]) == 0):
                    del core_cnode_dict[cnode_id]
                    #Construct the nodeset again
                    core_node_set = set()
                    for cnode_other_id, node_set in core_cnode_dict.items():
                        core_node_set.update(node_set)
                    #core_node_set.difference_update(self.cnodes_dict[cnode_id].node_set)

        return (core_cnode_dict, core_node_set)

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
            cnode = CNodeData_Clusterone_CP(cluster_label, -1, -1, cluster_center, self.graphdata, self.configdata)

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
