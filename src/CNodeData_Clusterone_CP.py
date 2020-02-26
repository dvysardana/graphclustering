__author__ = 'divya'

from CNodeData_Clusterone import CNodeData_Clusterone

class CNodeData_Clusterone_CP(CNodeData_Clusterone):

    def __init__(self, id, parent_id_1, parent_id_2, center, graphdata, configdata):
        super(CNodeData_Clusterone_CP, self).__init__(id, parent_id_1, parent_id_2, center, graphdata, configdata)

        self.cnode_node_dict = dict()

        self.cnode_mean_offset = 0
        self.cnode_mean_lower_bound = 1
        self.cnode_mean_upper_bound = 0
        self.overlapping_node_dict = dict() #follow both cohesion and mean constraint
                                            #Plus external edges also don't follow
                                            #mean constraint.
        self.periphery_node_dict = dict() #follow cohesion, not mean constraint
        self.other_node_dict = dict() #don't follow cohesion, don't follow mean constraint
        self.friend_node_dict = dict() #don't follow cohesion, follow mean constrain

        self.boundary_node_dict_ycohesion_nsd = dict()
        self.boundary_node_dict_ncohesion_ysd = dict()
        self.boundary_node_dict_ncohesion_nsd_low = dict()
        self.boundary_node_dict_ncohesion_nsd_high = dict()

        self.periphery_cnode_dict = dict() # stores cnode_id and CNodeRelationshipScore object.


    def calculate_cnode_secondary_fields(self):
        super().calculate_cnode_secondary_fields()
        self.calculate_cnode_mean_bounds()


    #Method to calculate upper and lower mean bounds of the cnode.
    def calculate_cnode_mean_bounds(self):

        if self.num_nodes != 1:
            #LOWER_BOUND = cnode_mean - cnode_standard_deviation - self.NODE_PENALTY_2 * (1/cnode_num_nodes)
            #UPPER_BOUND = cnode_mean + cnode_standard_deviation + self.NODE_PENALTY_2 * (1/cnode_num_nodes)
            #self.cnode_mean_offset = 0.2
            self.cnode_mean_offset = self.configdata.mean_diff
            self.cnode_mean_lower_bound = self.mean_edges - self.cnode_mean_offset
            self.cnode_mean_upper_bound = self.mean_edges + self.cnode_mean_offset


        else:
            self.cnode_mean_offset = 1 #check this.
            LOWER_BOUND = 0
            UPPER_BOUND = 1
