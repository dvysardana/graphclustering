__author__ = 'divya'

from GraphData_Gene_Pre import GraphData_Gene

class GraphData_Clusterone_Gene(GraphData_Gene):
    def __init__(self, go_type, go_size, go_sim_type, go_obo_file, gene_syn_file):
        super(GraphData_Clusterone_Gene, self).__init__(go_type, go_size, go_sim_type, go_obo_file, gene_syn_file)