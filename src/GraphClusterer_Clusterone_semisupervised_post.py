__author__ = 'divya'

from GraphData_Clusterone_Gene_post import GraphData_Clusterone_Gene
from ConfigData_Clusterone import ConfigData_Clusterone
from Phase1Data_Clusterone_gene_pre import Phase1Data_Clusterone_gene_pre
from Phase2Data_Clusterone_gene_post import Phase2Data_Clusterone_gene_post
from MKNN_Helper import MKNN_Helper
from EdgeData import EdgeType
from AllKEvaluationData import AllKEvaluationData

class GraphClusterer_Clusterone_semisupervised(object):
    CODE_DIR = '/Users/divya/work/repo/Dissertation'
    #CODE_DIR = '/Users/divya/Documents/Dissertation/Dissertation'
    DATA_DIR = '/Users/divya/Documents/input/Dissertation/data'
    LOG_DIR = '/Users/divya/Documents/logs/Dissertation'
    configdata = ConfigData_Clusterone(CODE_DIR, DATA_DIR, LOG_DIR)
    graphdata = None

    def __init__(self):
        self.phase1data = None
        self.phase2data = None
        self.phase1_allKevaluationdata = None
        self.phase2_allKevaluationdata = None
        self.helper = MKNN_Helper()

    def clusterone_worker_wrapper(self):
        #GraphClusterer_Clusterone_semisupervised.configdata.logger.info("Debugging from inside clusterone_wrapper")
        #GraphClusterer_Clusterone_semisupervised.configdata.logger.info("Initialization of Clusterone begins.")
        self.clusterone_init()
        GraphClusterer_Clusterone_semisupervised.configdata.logger.info("Initialization phase of Clusterone finished.")
        GraphClusterer_Clusterone_semisupervised.configdata.logger.debug("Working of Clusterone begins.")
        self.clusterone_worker()

    def clusterone_init(self):
        #setting up configuration
        GraphClusterer_Clusterone_semisupervised.configdata.do_config()
        GraphClusterer_Clusterone_semisupervised.configdata.data_dir
        logger = GraphClusterer_Clusterone_semisupervised.configdata.logger
        logger.debug("Debugging from inside MKNN_init method")

        GraphClusterer_Clusterone_semisupervised.graphdata = GraphData_Clusterone_Gene(GraphClusterer_Clusterone_semisupervised.configdata.GO_TYPE, GraphClusterer_Clusterone_semisupervised.configdata.GO_SIZE, GraphClusterer_Clusterone_semisupervised.configdata.GO_SIM_TYPE, GraphClusterer_Clusterone_semisupervised.configdata.go_obo_file, GraphClusterer_Clusterone_semisupervised.configdata.gene_syn_file)

        #Create SM and SM_orig
        GraphClusterer_Clusterone_semisupervised.graphdata.create_SM_from_relfile(GraphClusterer_Clusterone_semisupervised.configdata.inp_rel_file)


        #Expansion step not needed here as in MKNN
        GraphClusterer_Clusterone_semisupervised.graphdata.setup_SM_GO_1(GraphClusterer_Clusterone_semisupervised.configdata.inp_rel_file, GraphClusterer_Clusterone_semisupervised.configdata.gene2go_file)

        #Create edge objects
        GraphClusterer_Clusterone_semisupervised.graphdata.create_edge_objects()

        #Initialize all K evaluation objects for both phases
        self.phase1_allKevaluationdata = AllKEvaluationData(self.configdata, 1) #1 for phase=1
        self.phase2_allKevaluationdata = AllKEvaluationData(self.configdata, 2) #2 for phase=2

    def clusterone_worker(self):
        self.phase1data = Phase1Data_Clusterone_gene_pre(GraphClusterer_Clusterone_semisupervised.graphdata,
                                     GraphClusterer_Clusterone_semisupervised.configdata)
        self.clusterone_growth_phase()
        self.phase2data = Phase2Data_Clusterone_gene_post(GraphClusterer_Clusterone_semisupervised.graphdata,
                                     GraphClusterer_Clusterone_semisupervised.configdata,
                                     self.phase1data.cnodes_dict,
                                     self.phase1data.next_cluster_label,
                                     self.phase1data.num_clusters)
        self.clusterone_merge_phase()


    #Greedy growth process of clusters
    def clusterone_growth_phase(self):
        #Initialize Phase 1
        self.phase1data.initialize_phase()

        #Execute phase
        self.phase1data.execute_phase()

        #Visualize phase 1 results
        self.phase1data.visualize_phase()

        #Evaluate phase 1
        self.phase1data.evaluate_phase()

    #merge the possibly overlapping clusters
    #after the cluster growth phase is over.
    #read the paper again to understand it better.
    def clusterone_merge_phase(self):

        self.phase2data.initialize_phase()
        self.helper.print_list(self.phase2data.c_SM)

        self.phase2data.execute_phase()

        self.phase2data.prune_phase()

        self.phase2data.filter_clusters()

        self.phase2data.evaluate_phase()

        self.phase2data.visualize_phase()

    def clusterone_prune_phase(self):
        #1. Discard cnodes having less than three nodes, or
        #whose density n/(n-1)/2 is less than a given threshold.
        pass

if __name__ == "__main__":
    gc = GraphClusterer_Clusterone_semisupervised()
    gc.clusterone_worker_wrapper()
