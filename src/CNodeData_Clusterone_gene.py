__author__ = 'divya'

from CNodeData_Clusterone import CNodeData_Clusterone

class CNodeData_Clusterone_gene(CNodeData_Clusterone):
    def __init__(self, id, parent_id_1, parent_id_2, center, graphdata, configdata):
        super(CNodeData_Clusterone_gene, self).__init__(id, parent_id_1, parent_id_2, center, graphdata, configdata)

        #Input for gene enrichment
        self.node_gene_id_locustag_dict = dict()

        #Enriched GO terms dict associated with this CNode
        self.gene_GO_terms_dict = {}

        #Avg. Functional Similarity of gene pairs in this cluster.
        self.avg_func_gene_pair_sim = 0.0

        #self.gene_GO_terms_dict[GO_term_type.BP] = []
        #self.gene_GO_terms_dict[GO_term_type.CC] = []
        #self.gene_GO_terms_dict[GO_term_type.MF] = []

    #Override base class method.
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
        self.generate_node_gene_id_locustag_dict()
        self.active = True
        self.isDirty = False

    #Method to generate a dictionary containing gene_id as key and its locus tag (Y id) as its value.
    def generate_node_gene_id_locustag_dict(self):
        self.configdata.logger.debug("Debugging from inside generate_node_gene_id_locustag_dict method of CNodeData_WI_Gene class.")
        self.node_gene_id_locustag_dict = dict()
        for node_id in self.node_set:
            if self.graphdata.node_dict[node_id].gene_id != -1:
                self.node_gene_id_locustag_dict[self.graphdata.node_dict[node_id].gene_id] = self.graphdata.node_dict[node_id].gene_locustag

    def reset_gene_GO_terms_dict(self):
        self.gene_GO_terms_dict = {}
        self.gene_GO_terms_dict[GO_term_type.BP] = []
        self.gene_GO_terms_dict[GO_term_type.CC] = []
        self.gene_GO_terms_dict[GO_term_type.MF] = []

    def calculate_avg_func_gene_pair_sim(self):
        node_list = list(self.node_set)
        sumsim = 0.0
        avgsim = 0.0
        for i in range(0, len(node_list)):
            for j in range(0, len(node_list)):
                if i < j:
                    sumsim = sumsim + self.graphdata.SM_GO[node_list[i],node_list[j]]

        avgsim = 2*float(sumsim)/(float(len(node_list)) * float(len(node_list) - 1))

        self.avg_func_gene_pair_sim = avgsim
        #return avgsim

        #for cnode_id, cnode_data in self.cnodes_dict.items():


class GO_term_type(object):
    BP = "BP"
    CC = "CC"
    MF = "MF"