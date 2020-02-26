__author__ = 'divya'


from Phase1Data_Clusterone_CP import Phase1Data_Clusterone_CP
from AlgorithmName import AlgorithmName
from EdgeData import EdgeType

from CNodeData_Clusterone_CP import CNodeData_Clusterone_CP
from EvaluationData_Clusterone_CP import EvaluationData_Clusterone_CP

class Phase1Data_Clusterone_CP_Overlapping(Phase1Data_Clusterone_CP):
    def __init__(self, graphdata, configdata):
        super(Phase1Data_Clusterone_CP_Overlapping, self).__init__(graphdata, configdata)


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
                        self.prune_cnode(cnode_data_current, nodeset_prospective_remove, clabel_current, c_initiator_node.node_id)

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
