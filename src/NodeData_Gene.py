__author__ = 'divya'

from NodeData import NodeData
from genes_NCBI_data_locustag import LocusTag2nt
from CNodeData_WI_Gene import GO_term_type


class NodeData_Gene(NodeData):

    def __init__(self, id, code, graphdata):
        super(NodeData_Gene, self).__init__(id, code, graphdata)

        #Gene details
        self.gene_locustag = code #ID mostly beginning with Y.
        if self.gene_locustag in LocusTag2nt:
            self.gene_id = LocusTag2nt[self.gene_locustag][1]
            self.gene_symbol = LocusTag2nt[self.gene_locustag][2]
        elif self.gene_locustag in self.graphdata.gene_syn_dict:
            self.gene_id = self.graphdata.gene_syn_dict[self.gene_locustag]
            self.gene_symbol = ""
        else:
            print("yeast locus id not found :")
            print(self.gene_locustag)
            self.gene_id = -1
            self.gene_symbol = ''

        #Enriched GO terms dict associated with this node
        self.gene_GO_terms_dict = {}

    def reset_gene_GO_terms_dict(self):
        self.gene_GO_terms_dict = {}
        self.gene_GO_terms_dict[GO_term_type.BP] = []
        self.gene_GO_terms_dict[GO_term_type.CC] = []
        self.gene_GO_terms_dict[GO_term_type.MF] = []

