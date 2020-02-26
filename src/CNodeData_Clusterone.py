__author__ = 'divya'

from CNodeData import CNodeData
from EdgeData import EdgeType

class CNodeData_Clusterone(CNodeData):
    def __init__(self, id, parent_id_1, parent_id_2, center, graphdata, configdata):
        super(CNodeData_Clusterone, self).__init__(id, parent_id_1, parent_id_2, center, graphdata, configdata)

    # def calculate_cnode_secondary_fields(self):
    #     super().calculate_cnode_secondary_fields()
    #     self.calculate_cnode_mean_bounds()


    #Method tp calculate cohesion of a cnode on node addition
    def calculate_cohesion_on_node_addition(self, node_id_prospective):
        insim_prospective = self.insim
        edgeset_insim_add = self.external_edge_dict[EdgeType.primary].intersection(self.graphdata.node_dict[node_id_prospective].node_edges_dict[EdgeType.primary])
        edgeweight_insim_add = sum([self.graphdata.edge_dict[edge_id].edge_weight for edge_id in edgeset_insim_add])
        insim_prospective = insim_prospective + edgeweight_insim_add

        outsim_prospective = self.outsim
        outsim_prospective = outsim_prospective - edgeweight_insim_add
        edgeset_outsim_add = self.graphdata.node_dict[node_id_prospective].node_edges_dict[EdgeType.primary].difference(edgeset_insim_add)
        edgeweight_outsim_add = sum([self.graphdata.edge_dict[edge_id].edge_weight for edge_id in edgeset_outsim_add])
        outsim_prospective = outsim_prospective + edgeweight_outsim_add

        cohesion_prospective = self.calculate_prospective_cohesion(insim_prospective, outsim_prospective, self.num_nodes+1)

        return cohesion_prospective

    #Method to calculate cohesion of a cnode on node removal
    def calculate_cohesion_on_node_removal(self, node_id_prospective):
        insim_prospective = self.insim
        edgeset_insim_remove = self.internal_edge_dict[EdgeType.primary].intersection(self.graphdata.node_dict[node_id_prospective].node_edges_dict[EdgeType.primary])
        edgeweight_insim_remove = sum([self.graphdata.edge_dict[edge_id].edge_weight for edge_id in edgeset_insim_remove])
        insim_prospective = insim_prospective - edgeweight_insim_remove

        outsim_prospective = self.outsim
        outsim_prospective = outsim_prospective + edgeweight_insim_remove
        edgeset_outsim_remove = self.graphdata.node_dict[node_id_prospective].node_edges_dict[EdgeType.primary].difference(edgeset_insim_remove)
        edgeweight_outsim_remove = sum([self.graphdata.edge_dict[edge_id].edge_weight for edge_id in edgeset_outsim_remove])
        outsim_prospective = outsim_prospective - edgeweight_outsim_remove

        cohesion_prospective = self.calculate_prospective_cohesion(insim_prospective, outsim_prospective, self.num_nodes-1)

        return cohesion_prospective

    #Calculate prospective cohesion
    def calculate_prospective_cohesion(self, insim_prospective, outsim_prospective, num_nodes_prospective):
        if(insim_prospective == 0 and outsim_prospective == 0):
            cohesion_prospective = 0
        else:
            cohesion_prospective = (float)(insim_prospective)/((float) (insim_prospective + outsim_prospective + self.configdata.node_penalty * num_nodes_prospective))

        return cohesion_prospective
