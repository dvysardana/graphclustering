__author__ = 'divya'

from CNodeData import CNodeData
from EdgeData import EdgeType

class CNodeData_WI(CNodeData):
    def __init__(self, id, parent_id_1, parent_id_2, center, graphdata, configdata):
        super(CNodeData_WI, self).__init__(id, parent_id_1, parent_id_2, center, graphdata, configdata)
        self.cnode_GMKNN_clabel_dict = dict()
        self.cnode_MKNN_list = []
        self.member_cnode_set = set()

        #self.boundary_cnode_dict_ycohesion_nsd = dict()
        self.boundary_cnode_dict_ycohesion_nsd_low = dict()
        self.boundary_cnode_dict_ycohesion_nsd_high = dict()
        self.boundary_cnode_dict_ncohesion_ysd = dict()
        self.boundary_cnode_dict_ncohesion_nsd_low = dict()
        self.boundary_cnode_dict_ncohesion_nsd_high = dict()
        self.boundary_cnode_dict_ycohesion_ysd_pp = dict()

        self.periphery_cnode_dict = dict() # stores cnode_id and CNodeRelationshipScore object.



    def initialize_MKNN(self, K):
        self.cnode_MKNN_list = [-1]*K


    def check_structure_edge_weight_constraint(self, cnode_data_2, MEAN_DIFF):
        self.configdata.logger.debug("Debugging from inside check_structure_edge_weight_constraint method of CNodeData_WI class.")
        edgeset_shared = self.calculate_shared_edge_set(cnode_data_2)
        structure_constraint = self.check_structure_constraint(cnode_data_2, edgeset_shared)
        #edge_weight_constraint = self.check_edge_weight_constraint(cnode_data_2, edgeset_shared, MEAN_DIFF)
        edge_weight_constraint = self.check_edge_weight_constraint_1(cnode_data_2, edgeset_shared, MEAN_DIFF)

        return(structure_constraint, edge_weight_constraint)

    def check_structure_constraint(self, cnode_data_2, edgeset_shared):
        cnode_id_2 = cnode_data_2.cnode_id
        #Possibilities:
        #At least one primary edge
        #At least 25% of the nodes in both clusters involved in primary connection
        #Cohesion of the final cluster increases on merging the two clusters

        self.configdata.logger.debug("Debugging from inside check_structure_constraint method of CNodeData_WI class")
        structure_constraint = 0
        edgeset_proposed_to_add = cnode_data_2.internal_edge_dict[EdgeType.primary].union(edgeset_shared)

        if(edgeset_shared != None and len(edgeset_shared) != 0):
            edgeset_shared_sum = self.calculate_sum_edgeset(edgeset_shared)
            insim_prospective = self.insim + cnode_data_2.insim + edgeset_shared_sum
            outsim_prospective = self.outsim + cnode_data_2.outsim - 2 * edgeset_shared_sum
            num_nodes_prospective = self.num_nodes + cnode_data_2.num_nodes
            cohesion_prospective = self.calculate_prospective_cohesion(insim_prospective, outsim_prospective, num_nodes_prospective)
            if cnode_data_2.cnode_id == 9 and self.cnode_id == 21:
                print("cohesion before:")
                print(str(self.cohesion))
                print("cohesion after:")
                print(str(cohesion_prospective))

            if cohesion_prospective > self.cohesion:
                structure_constraint = 1

        return structure_constraint

    #Method used in Evaluation Phase
    #Added: 7/4/2017
    def get_prospective_cohesion_diff(self, cnode_data_2):
        edgeset_shared = self.calculate_shared_edge_set(cnode_data_2)
        cnode_id_2 = cnode_data_2.cnode_id
        #Possibilities:
        #At least one primary edge
        #At least 25% of the nodes in both clusters involved in primary connection
        #Cohesion of the final cluster increases on merging the two clusters

        self.configdata.logger.debug("Debugging from inside check_structure_constraint method of CNodeData_WI class")
        structure_constraint = 0
        edgeset_proposed_to_add = cnode_data_2.internal_edge_dict[EdgeType.primary].union(edgeset_shared)

        if(edgeset_shared != None and len(edgeset_shared) != 0):
            edgeset_shared_sum = self.calculate_sum_edgeset(edgeset_shared)
            insim_prospective = self.insim + cnode_data_2.insim + edgeset_shared_sum
            outsim_prospective = self.outsim + cnode_data_2.outsim - 2 * edgeset_shared_sum
            num_nodes_prospective = self.num_nodes + cnode_data_2.num_nodes
            cohesion_prospective = self.calculate_prospective_cohesion(insim_prospective, outsim_prospective, num_nodes_prospective)
            if cnode_data_2.cnode_id == 9 and self.cnode_id == 21:
                print("cohesion before:")
                print(str(self.cohesion))
                print("cohesion after:")
                print(str(cohesion_prospective))

            if cohesion_prospective > self.cohesion:
                structure_constraint = 1

        return self.cohesion - cohesion_prospective



    def check_edge_weight_constraint(self, cnode_data_2, edgeset_shared, MEAN_DIFF):
        #Among the edges to be added proposed, the number of in range, small or large edges.
        #These edges will be calculated based upon the connection edges as well as the other cluster edges

        #OR take the difference in mean of 1-2, 2-3 and 1-3: all should be greater than 0.2.
        #
        # cnode_id_1 = self.cnode_id
        # cnode_id_2 = cnode_data_2.cnode_id

        self.configdata.logger.debug("Debugging from inside check_edge_weight_constraint method of CNodeData_WI class.")
        edge_weight_constraint_1 = 0
        edge_weight_constraint_2 = 0
        edgeset_cnode_2 = cnode_data_2.internal_edge_dict[EdgeType.primary]

        (UPPER_BOUND, LOWER_BOUND) = self.calculate_cnode_edge_weight_bounds(MEAN_DIFF)

        edge_weight_constraint_1 = self.check_edgeset_edge_weight_constraint(edgeset_shared, UPPER_BOUND, LOWER_BOUND)
        if cnode_data_2.num_nodes != 1:
            edge_weight_constraint_2 = self.check_edgeset_edge_weight_constraint(edgeset_cnode_2, UPPER_BOUND, LOWER_BOUND)
            if edge_weight_constraint_1 == 1 and edge_weight_constraint_2 == 1:
                return 1
            elif edge_weight_constraint_2 == 2:
                return 2
            elif edge_weight_constraint_2 == 3:
                return 3

        else: #If cnode_2 has only one node.
            edge_weight_constraint_2 = 1
            if edge_weight_constraint_1 == 1 and edge_weight_constraint_2 == 1:
                return 1
            elif edge_weight_constraint_1 == 2:
                return 2
            elif edge_weight_constraint_1 == 3:
                return 3

        # if(edgeset_proposed_to_add != None):
        #     print("Edgeset proposed to add:")
        #     self.helper.print_set(edgeset_proposed_to_add)
        #
        #     (num_edges_long, num_edges_short, num_edges_inrange) = self.categorize_node_edgeset(edgeset_proposed_to_add, UPPER_BOUND, LOWER_BOUND)
        #
        #     if num_edges_inrange >= (num_edges_short + num_edges_long):
        #         edge_weight_constraint = 1
        #     elif num_edges_short >= (num_edges_inrange + num_edges_long):
        #         edge_weight_constraint = 2
        #     elif num_edges_long >= (num_edges_inrange + num_edges_short):
        #         edge_weight_constraint = 3

        return 0

    #Method to calculate edge weight constraint based upon mean difference.
    def check_edge_weight_constraint_1(self, cnode_data_2, edgeset_shared, MEAN_DIFF):
        #Among the edges to be added proposed, the number of in range, small or large edges.
        #These edges will be calculated based upon the connection edges as well as the other cluster edges

        #OR take the difference in mean of 1-2, 2-3 and 1-3: all should be greater than 0.2.
        #
        # cnode_id_1 = self.cnode_id
        # cnode_id_2 = cnode_data_2.cnode_id

        self.configdata.logger.debug("Debugging from inside check_edge_weight_constraint method of CNodeData_WI class.")
        edge_weight_constraint_1 = 0
        edge_weight_constraint_2 = 0
        edgeset_cnode_2 = cnode_data_2.internal_edge_dict[EdgeType.primary]

        cnode1_mean = self.mean_edges
        cnode2_mean = cnode_data_2.mean_edges
        edgeset_shared_mean = self.calculate_mean_edgeset(edgeset_shared)

        print("cnode1_mean")
        print(str(cnode1_mean))
        print("cnode2_mean")
        print(str(cnode2_mean))
        print("Edgeset shared _mean")
        print(str(edgeset_shared_mean))

        mean_diff_12 = abs(cnode1_mean - cnode2_mean)
        mean_diff_13 = abs(cnode1_mean - edgeset_shared_mean)
        mean_diff_23 = abs(cnode2_mean - edgeset_shared_mean)

        (UPPER_BOUND, LOWER_BOUND) = self.calculate_cnode_edge_weight_bounds(MEAN_DIFF)

        edge_weight_constraint_1 = self.check_edgeset_edge_weight_constraint(edgeset_shared, UPPER_BOUND, LOWER_BOUND)
        if cnode_data_2.num_nodes != 1:
            edge_weight_constraint_2 = self.check_edgeset_edge_weight_constraint(edgeset_cnode_2, UPPER_BOUND, LOWER_BOUND)
            #if edge_weight_constraint_1 == 1 and edge_weight_constraint_2 == 1:
            if mean_diff_12 < MEAN_DIFF and mean_diff_13 < MEAN_DIFF and mean_diff_23 < MEAN_DIFF:
                return 1
            elif edge_weight_constraint_2 == 2:
                return 2
            elif edge_weight_constraint_2 == 3:
                return 3

        else: #If cnode_2 has only one node.
            edge_weight_constraint_2 = 1
            if mean_diff_13 < MEAN_DIFF:
            #if edge_weight_constraint_1 == 1 and edge_weight_constraint_2 == 1:
                return 1
            elif edge_weight_constraint_1 == 2:
                return 2
            elif edge_weight_constraint_1 == 3:
                return 3

        # if(edgeset_proposed_to_add != None):
        #     print("Edgeset proposed to add:")
        #     self.helper.print_set(edgeset_proposed_to_add)
        #
        #     (num_edges_long, num_edges_short, num_edges_inrange) = self.categorize_node_edgeset(edgeset_proposed_to_add, UPPER_BOUND, LOWER_BOUND)
        #
        #     if num_edges_inrange >= (num_edges_short + num_edges_long):
        #         edge_weight_constraint = 1
        #     elif num_edges_short >= (num_edges_inrange + num_edges_long):
        #         edge_weight_constraint = 2
        #     elif num_edges_long >= (num_edges_inrange + num_edges_short):
        #         edge_weight_constraint = 3

        return 0


    #Method to calculate the edge weight bounds for a cnode for
    #calculating refined_propective_nodeset_add.
    def calculate_cnode_edge_weight_bounds(self, MEAN_DIFF):
        self.configdata.logger.debug("Debugging from inside calculate_cnode_edge_weight_bounds  method of CNodeData_WI class.")
        #Get secondary data of current cnode
        cnode_standard_deviation = self.standard_deviation_edges
        cnode_mean = self.mean_edges
        cnode_num_nodes = self.num_nodes

        if cnode_num_nodes != 1:
            #LOWER_BOUND = cnode_mean - cnode_standard_deviation - self.NODE_PENALTY_2 * (1/cnode_num_nodes)
            #UPPER_BOUND = cnode_mean + cnode_standard_deviation + self.NODE_PENALTY_2 * (1/cnode_num_nodes)
            # LOWER_BOUND = cnode_mean - 0.2
            # UPPER_BOUND = cnode_mean + 0.2
            LOWER_BOUND = cnode_mean - MEAN_DIFF
            UPPER_BOUND = cnode_mean + MEAN_DIFF

        else:
            LOWER_BOUND = 0
            UPPER_BOUND = 1
        return(UPPER_BOUND, LOWER_BOUND)

    #Method to categorize node's edges as being long, short, inrange
    #and return the counts of such categories.
    def categorize_node_edgeset(self, node_edgeset, UPPER_BOUND, LOWER_BOUND):
        self.configdata.logger.debug("Debugging from inside categorize_node_edgeset method of CNodeData_WI class.")
        num_edges_long = sum([1 if self.graphdata.edge_dict[edge_id].edge_weight > UPPER_BOUND else 0 for edge_id in node_edgeset])
        num_edges_short = sum([1 if self.graphdata.edge_dict[edge_id].edge_weight < LOWER_BOUND else 0 for edge_id in node_edgeset])
        num_edges_inrange = len(node_edgeset) - (num_edges_long + num_edges_short)
        # print("Number of long edges")
        # print(str(num_edges_long))
        # print("Number of inrange edges")
        # print(str(num_edges_inrange))
        return (num_edges_long, num_edges_short, num_edges_inrange)

    def check_edgeset_edge_weight_constraint(self, edgeset, UPPER_BOUND, LOWER_BOUND):
        self.configdata.logger.debug("Debugging from inside check_edgeset_edge_weight_constraint method of class CNodeData_WI.")
        edge_weight_constraint = 0
        if(edgeset != None and len(edgeset) != 0):
            #print("Edgeset proposed to add:")
            #self.helper.print_set(edgeset)

            (num_edges_long, num_edges_short, num_edges_inrange) = self.categorize_node_edgeset(edgeset, UPPER_BOUND, LOWER_BOUND)

            if num_edges_inrange >= (num_edges_short + num_edges_long):
                edge_weight_constraint = 1
            elif num_edges_short >= (num_edges_inrange + num_edges_long):
                edge_weight_constraint = 2
            elif num_edges_long >= (num_edges_inrange + num_edges_short):
                edge_weight_constraint = 3
        return edge_weight_constraint

    #method to calculate the edgeset shared between two cnodes
    # def calculate_shared_edge_set(self, cnode_data, cnode_merger_set):
    #     for cnode_id in cnode_merger_set:
    #
    #     set_shared = self.external_edge_dict[EdgeType.primary].intersection(cnode_data.external_edge_dict[EdgeType.primary])
    #     return set_shared
