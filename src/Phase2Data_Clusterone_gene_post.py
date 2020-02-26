__author__ = 'divya'

from Phase2Data_Clusterone import Phase2Data_Clusterone
from CNodeData_Clusterone_gene import CNodeData_Clusterone_gene
from EdgeData import EdgeType

class Phase2Data_Clusterone_gene_post(Phase2Data_Clusterone):
    def __init__(self, graphdata, configdata, cnodes_dict, next_cluster_label, num_clusters):
        super(Phase2Data_Clusterone_gene_post, self).__init__(graphdata, configdata, cnodes_dict, next_cluster_label, num_clusters)
        self.cnode_functional_sort_list = []

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

    #Calculate avg. gene pair functional similarity per cluster
    def filter_clusters(self):
        for cnode_id, cnode_data in self.cnodes_dict.items():
            if cnode_data.active == True and cnode_data.num_nodes >= 3:
                cnode_data.calculate_avg_func_gene_pair_sim()
                self.cnode_functional_sort_list.append((cnode_id, cnode_data.avg_func_gene_pair_sim))
                if cnode_data.avg_func_gene_pair_sim < self.configdata.SIM_CUTOFF:
                    cnode_data.active = False
                    self.num_clusters = self.num_clusters - 1

        self.cnode_functional_sort_list = sorted(self.cnode_functional_sort_list, key = lambda x:x[1], reverse = True)

        target1 = open("/Users/divya/Documents/output/Dissertation/manual/Semisupervised/Postprocessing/cnode_func_sim_clusterone.txt", 'a')
        for (cnode_id, func_sim) in self.cnode_functional_sort_list:
            target1.write(str(cnode_id))
            target1.write(" ")
            target1.write(str(self.cnodes_dict[cnode_id].num_nodes))
            target1.write(" ")
            target1.write(str(func_sim))
            target1.write("\n")


