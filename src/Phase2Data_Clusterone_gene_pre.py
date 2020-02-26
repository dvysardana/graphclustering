__author__ = 'divya'

from Phase2Data_Clusterone import Phase2Data_Clusterone
from CNodeData_Clusterone_gene import CNodeData_Clusterone_gene
from EdgeData import EdgeType

class Phase2Data_Clusterone_gene_pre(Phase2Data_Clusterone):
    def __init__(self, graphdata, configdata, cnodes_dict, next_cluster_label, num_clusters):
        super(Phase2Data_Clusterone_gene_pre, self).__init__(graphdata, configdata, -1, cnodes_dict, next_cluster_label, num_clusters)

    #Overriding base class method
    #Method to create a new cnode upon merging of cnodes in merger_set
    def create_merged_cnode(self, merger_set):
        self.configdata.logger.debug("Debugging from inside create_merged_cnode method.")
        #Create a new cnode object
        #cluster_label_new = self.next_cluster_label
        cluster_label_new = min(list(merger_set))

        #create new merged cnode
        cnode_data_merged = CNodeData_Clusterone_gene(cluster_label_new, -1, -1, -1, self.graphdata, self.configdata)


       #Add nodes to new cnode
        self.add_nodes_to_merged_cnode(merger_set, cnode_data_merged)

        #Add edges to new cnode
        #primary
        self.add_edges_to_merged_cnode(merger_set, cnode_data_merged, EdgeType.primary)

        #Run the clustering statistics for the new cnode
        #this also sets the active and dirty flags.
        cnode_data_merged.calculate_cnode_secondary_fields()

        return cnode_data_merged

