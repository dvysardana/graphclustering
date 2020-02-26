__author__ = 'divya'

import math
from EdgeData import EdgeType
from MKNN_Helper import MKNN_Helper

class CNodeData(object):

    def __init__(self, id, parent_id_1, parent_id_2, center, graphdata, configdata):
        #For use in phase 1
        self.cnode_id = id
        self.cluster_center = center
        self.cnode_parent_id_1 = parent_id_1
        self.cnode_parent_id_2 = parent_id_2
        self.graphdata = graphdata
        self.configdata = configdata
        self.internal_edge_dict = {}
        self.internal_edge_dict[EdgeType.primary] = set()
        self.internal_edge_dict[EdgeType.secondary] = set()
        self.external_edge_dict = {}
        self.external_edge_dict[EdgeType.primary] = set()
        self.external_edge_dict[EdgeType.secondary] = set()
        self.node_set = set()
        self.num_nodes = -1
        self.num_internal_primary_edges = -1
        self.num_external_primary_edges = -1

        #For use in phase 2
        #self.cnode_GMKNN_clabel_dict = dict() #Need to check later if a cnode level clabel
                                              #is required or not. I think this clabel is
                                              #different than a node level clabel.
        self.insim = -1
        self.outsim = -1
        self.cohesion = -1
        self.standard_deviation_edges = -1 #SD of internal_primary_edges
        self.mean_edges = -1 #mean of internal primary edges

        #self.cnode_MKNN_list = []
        self.cnode_CP_status = ClusterStatus.none #save core periphery status
        self.active = False #A flag to store status if the object is still in use
                            #or perhaps the cluster has merged to form a new object
        self.isDirty = True #A flag to set if any new edge has been added to cluster
                            #If this is flag, then all the summary data can be used
                            #Else, repopulate all the summary data from the master
                            #data, that is
                            # a.) internal_edge_dict and
                            # b.) external_edge_dict

        self.helper = MKNN_Helper()

        #used in evaluation
        self.struct_density = 0.0
        self.weighted_struct_density = 0.0
        self.avg_evol_rate = 0.0
        self.perc_essential_genes = 0.0
        self.avg_phyletic_age = 0.0

        # #Used in clusterone core-periphery code
        # self.cnode_mean_offset = 0
        # self.cnode_mean_lower_bound = 0
        # self.cnode_mean_upper_bound = 0
        # self.overlapping_node_dict = dict() #follow both cohesion and mean constraint
        #                                     #Plus external edges also don't follow
        #                                     #mean constraint.
        # self.periphery_node_dict = dict() #follow cohesion, not mean constraint
        # self.other_node_dict = dict() #don't follow cohesion, don't follow mean constraint
        # self.friend_node_dict = dict() #don't follow cohesio, follow mean constrain

    def calculate_cnode_secondary_fields(self):
        self.calculate_cnode_num_nodes()
        self.calculate_cnode_num_internal_primary_edges()
        self.calculate_cnode_num_external_primary_edges()
        self.calculate_cnode_insim()
        self.calculate_cnode_outsim()
        self.calculate_cnode_cohesion()
        self.calculate_cnode_mean_edges()
        self.calculate_cnode_standard_deviation_edges()
        self.calculate_cnode_struct_density()
        self.active = True
        self.isDirty = False

    def deactivate_cnode(self):
        self.active = False
        self.isDirty = True

    def calculate_cnode_node_set(self):
        pass

    def calculate_cnode_num_nodes(self):
        if not self.node_set:
            self.num_nodes = 0
        else:
            self.num_nodes = len(self.node_set)

    def calculate_cnode_num_internal_primary_edges(self):
        if not self.internal_edge_dict[EdgeType.primary]:
            self.num_internal_primary_edges = 0
        else:
            self.num_internal_primary_edges = len(self.internal_edge_dict[EdgeType.primary])

    def calculate_cnode_num_external_primary_edges(self):
        self.num_external_primary_edges = len(self.external_edge_dict[EdgeType.primary])

    def calculate_cnode_insim(self):
        #self.insim = sum(self.internal_edge_dict[EdgeType.primary])
        self.insim = sum(self.graphdata.edge_dict[x].edge_weight for x in self.internal_edge_dict[EdgeType.primary])

    def calculate_cnode_outsim(self):
        #self.outsim = sum(self.external_edge_dict[EdgeType.primary])
        self.outsim = sum(self.graphdata.edge_dict[x].edge_weight for x in self.external_edge_dict[EdgeType.primary])

    def calculate_cnode_standard_deviation_edges(self):
        if self.num_internal_primary_edges == 0:
            self.standard_deviation_edges = 0
        else:
            #sum_squares = sum({((x - self.mean_edges) * (x - self.mean_edges)) for x in self.internal_edge_dict[EdgeType.primary]})
            sum_squares = sum({((self.graphdata.edge_dict[x].edge_weight - self.mean_edges) * (self.graphdata.edge_dict[x].edge_weight - self.mean_edges)) for x in self.internal_edge_dict[EdgeType.primary]})
            self.standard_deviation_edges = math.sqrt((float) (sum_squares)/ (float) (self.num_internal_primary_edges))

    def calculate_cnode_mean_edges(self):
        if self.num_internal_primary_edges == 0:
            self.mean_edges = 0
        else:
            self.mean_edges = (float) (self.insim) / (float) (self.num_internal_primary_edges)

    def calculate_cnode_cohesion(self):
        self.cohesion = (float)(self.insim)/ (float) (self.insim + self.outsim + self.configdata.node_penalty * self.num_nodes)

    def calculate_SD_on_node_removal(self, node_to_be_removed):
        edge_set_proposed = self.calculate_internal_edge_set_on_node_removal(node_to_be_removed)
        sd_proposed = self.calculate_SD_edgeset(edge_set_proposed)
        return (sd_proposed, len(edge_set_proposed))

    def calculate_SD_on_node_addition(self, node_to_be_added):
        edge_set_proposed = self.calculate_internal_edge_set_on_node_addition(node_to_be_added)
        sd_proposed = self.calculate_SD_edgeset(edge_set_proposed)
        return (sd_proposed, len(edge_set_proposed))

    def calculate_internal_edge_set_on_node_addition(self, node_to_be_added):
        set_temp = self.external_edge_dict[EdgeType.primary].intersection(node_to_be_added.node_edges_dict[EdgeType.primary])
        edge_set_current_proposed = self.internal_edge_dict[EdgeType.primary].union(set_temp)
        return edge_set_current_proposed

    def calculate_internal_edge_set_on_node_removal(self, node_to_be_removed):
        set_temp = self.internal_edge_dict[EdgeType.primary].intersection(node_to_be_removed.node_edges_dict[EdgeType.primary])
        edge_set_other_proposed = self.internal_edge_dict[EdgeType.primary].difference(set_temp)
        return edge_set_other_proposed

    def calculate_cnode_struct_density(self):
        num_possible_edges = ((self.num_nodes) * (self.num_nodes-1))/2
        if self.num_internal_primary_edges != 0:
            self.struct_density = (float)(self.num_internal_primary_edges)/ (float)(num_possible_edges)
            self.weighted_struct_density = (float)(self.insim)/ (float)(num_possible_edges)
        else:
            self.struct_density = 0.0

    #method to calculate sum of an edge set
    def calculate_sum_edgeset(self, edge_set):
        if len(edge_set) == 0:
            sum_set = 0
        else:
            sum_set = (float)(sum(self.graphdata.edge_dict[x].edge_weight for x in edge_set))
        return sum_set

    #method to calculate mean of an edge set
    def calculate_mean_edgeset(self, edge_set):
        if len(edge_set) == 0:
            mean_set = 0
        else:
            mean_set = (float)(sum(self.graphdata.edge_dict[x].edge_weight for x in edge_set))/ (float) (len(edge_set))
        return mean_set

    #method to calculate Standard deviation of an edgeset
    def calculate_SD_edgeset(self, edge_set):
        mean_set = self.calculate_mean_edgeset(edge_set)
        if len(edge_set) == 0:
            standard_deviation_edges = 0
        else:
            sum_squares = sum({((self.graphdata.edge_dict[x].edge_weight - mean_set) * (self.graphdata.edge_dict[x].edge_weight - mean_set)) for x in edge_set})
            standard_deviation_edges = (float) (math.sqrt((float) (sum_squares)/ (float) (len(edge_set))))
        return standard_deviation_edges

    #method to calculate structural density of an edgeset
    def calculate_struct_density_edgeset(self, num_nodes, num_internal_primary_edges):
        num_possible_edges = ((num_nodes) * (num_nodes-1))/2
        if num_internal_primary_edges != 0:
            struct_density = (float)(num_internal_primary_edges)/ (float)(num_possible_edges)
            #self.weighted_struct_density = (float)(self.insim)/ (float)(num_possible_edges)
        else:
            struct_density = 0.0

        return struct_density

    #method to calculate the edgeset shared between two cnodes
    def calculate_shared_edge_set(self, cnode_data):
        set_shared = self.external_edge_dict[EdgeType.primary].intersection(cnode_data.external_edge_dict[EdgeType.primary])
        return set_shared

    #Calculate prospective cohesion
    def calculate_prospective_cohesion(self, insim_prospective, outsim_prospective, num_nodes_prospective):
        self.configdata.logger.debug("Debugging from inside calculate_prospective_cohesion method of CNodeData_WI class.")
        if(insim_prospective == 0 and outsim_prospective == 0):
            cohesion_prospective = 0
        else:
            cohesion_prospective = (float)(insim_prospective)/((float) (insim_prospective + outsim_prospective + self.configdata.node_penalty * num_nodes_prospective))

        return cohesion_prospective

    def set_cnode_CP_status(self, CP_status):
        cnode_current_status = self.cnode_CP_status
        if cnode_current_status == ClusterStatus.none:
            self.cnode_CP_status = CP_status
        elif cnode_current_status == ClusterStatus.core:
            if CP_status == ClusterStatus.periphery:
                # print('set coreandperiphery')
                # print(str(self.cnode_id))
                self.cnode_CP_status = ClusterStatus.coreandperiphery
        elif cnode_current_status == ClusterStatus.periphery:
            if CP_status == ClusterStatus.core:
                # print('set coreandperiphery')
                # print(str(self.cnode_id))
                self.cnode_CP_status = ClusterStatus.coreandperiphery
        elif cnode_current_status == ClusterStatus.coreandperiphery:
            pass
            # print('status is coreandperiphery')
            # print(str(self.cnode_id))

class ClusterStatus(object):
    none = 'none'
    core = 'core'
    periphery = 'periphery'
    coreandperiphery = 'coreandperiphery'


