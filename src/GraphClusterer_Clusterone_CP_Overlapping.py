__author__ = 'divya'

from ConfigData_Clusterone import ConfigData_Clusterone
from GraphData_Clusterone import GraphData_Clusterone
from Phase1Data_Clusterone_CP_Overlapping import Phase1Data_Clusterone_CP_Overlapping
from Phase2Data_Clusterone_CP_Overlapping import Phase2Data_Clusterone_CP_Overlapping
from AllKEvaluationData import AllKEvaluationData
from MKNN_Helper import MKNN_Helper

class GraphClusterer_Clusterone_CP_Overlapping(object):
    CODE_DIR = '/Users/divya/work/repo/Dissertation'
    #CODE_DIR = '/Users/divya/Documents/Dissertation/Dissertation'
    DATA_DIR = '/Users/divya/Documents/input/Dissertation/data'
    LOG_DIR = '/Users/divya/Documents/logs/Dissertation'
    configdata = ConfigData_Clusterone(CODE_DIR, DATA_DIR, LOG_DIR)
    graphdata = GraphData_Clusterone()

    def __init__(self):
        self.phase1data = None
        self.phase2data = None
        self.phase1_allKevaluationdata = None
        self.phase2_allKevaluationdata = None
        self.helper = MKNN_Helper()

    def clusterone_worker_wrapper(self):
        #GraphClusterer_Clusterone.configdata.logger.info("Debugging from inside clusterone_wrapper")
        #GraphClusterer_Clusterone.configdata.logger.info("Initialization of Clusterone begins.")
        self.clusterone_init()
        GraphClusterer_Clusterone_CP_Overlapping.configdata.logger.info("Initialization phase of Clusterone finished.")
        GraphClusterer_Clusterone_CP_Overlapping.configdata.logger.debug("Working of Clusterone begins.")
        self.clusterone_worker()

    def clusterone_init(self):
        #setting up configuration
        GraphClusterer_Clusterone_CP_Overlapping.configdata.do_config()
        GraphClusterer_Clusterone_CP_Overlapping.configdata.data_dir
        logger = GraphClusterer_Clusterone_CP_Overlapping.configdata.logger
        logger.debug("Debugging from inside MKNN_init method.")

        #Create SM and SM_orig
        GraphClusterer_Clusterone_CP_Overlapping.graphdata.create_SM_from_relfile(GraphClusterer_Clusterone_CP_Overlapping.configdata.inp_rel_file)

        #Expansion step not needed here as in MKNN

        #Create edge objects
        GraphClusterer_Clusterone_CP_Overlapping.graphdata.create_edge_objects()

        #Initialize all K evaluation objects for both phases
        self.phase1_allKevaluationdata = AllKEvaluationData(self.configdata, 1) #1 for phase=1
        self.phase2_allKevaluationdata = AllKEvaluationData(self.configdata, 2) #2 for phase=2

    def clusterone_worker(self):
        self.phase1data = Phase1Data_Clusterone_CP_Overlapping(GraphClusterer_Clusterone_CP_Overlapping.graphdata,
                                     GraphClusterer_Clusterone_CP_Overlapping.configdata)
        self.clusterone_growth_phase()
        self.phase2data = Phase2Data_Clusterone_CP_Overlapping(GraphClusterer_Clusterone_CP_Overlapping.graphdata,
                                     GraphClusterer_Clusterone_CP_Overlapping.configdata,
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

        self.phase2data.evaluate_phase()

        self.phase2data.visualize_phase()


if __name__ == "__main__":
    gc = GraphClusterer_Clusterone_CP_Overlapping()
    gc.clusterone_worker_wrapper()