__author__ = 'divya'

import numpy as np

from GraphData import GraphData
from ConfigData import ConfigData
from Phase1Data import Phase1Data
from Phase2Data import Phase2Data
from MKNN_Helper import MKNN_Helper
from EdgeData import EdgeType
from AllKEvaluationData import AllKEvaluationData

class GraphClusterer(object):
    CODE_DIR = '/Users/divya/work/repo/Dissertation'
    #CODE_DIR = '/Users/divya/Documents/Dissertation/Dissertation'
    DATA_DIR = '/Users/divya/Documents/input/Dissertation/data'
    LOG_DIR = '/Users/divya/Documents/logs/Dissertation'
    configdata = ConfigData(CODE_DIR, DATA_DIR, LOG_DIR)
    graphdata = GraphData()

    def __init__(self, K):
        self.phase1data = None
        self.phase2data = None
        self.phase1_allKevaluationdata = None
        self.phase2_allKevaluationdata = None
        self.helper = MKNN_Helper()

    ##############################################################
    #1. Initialize MKNN
    #2. As a wrapper, call MKNN_worker for different values of K
    ##############################################################
    def MKNN_worker_wrapper(self):
        #GraphClusterer.configdata.logger.info("Initialization phase of GMKNN begins")
        self.MKNN_init()
        GraphClusterer.configdata.logger.info("Initialization phase of GMKNN ends.")

        GraphClusterer.configdata.logger.info("Working of G-MKNN begins")
        GraphClusterer.configdata.logger.info("Running G-MKNN for different values of K.")

        K_range = list(range((int)(GraphClusterer.configdata.K_min), (int)(GraphClusterer.configdata.K_max)+1))

        for K in K_range:
            GraphClusterer.configdata.logger.info("Running G-MKNN for the value of K: ")
            GraphClusterer.configdata.logger.info(K)
            #Call MKNN_worker for the value of K
            self.MKNN_worker(K)
            #(CL_List_P2, CL_List_P1, SM, SM_orig, num_clusters_P2, num_clusters_P1, num_nodes) = MKNN_worker(K, max_num_clusters, SM, SM_orig, num_nodes, node_codes, currentdate_str, dataset_name, eval_results_dir, log)

        #Plot evaluation measures for all values of K for phase 1
        self.phase1_allKevaluationdata.plot_evaluation_measures_for_all_K()

        #Plot evaluation measures for all values of K for phase 2
        self.phase2_allKevaluationdata.plot_evaluation_measures_for_all_K()

    ############################################
    #Set up configuration
    #Set up the input matrices for the algorithm
    ############################################
    def MKNN_init(self):

        #setting up configuration
        GraphClusterer.configdata.do_config()
        GraphClusterer.configdata.data_dir
        logger = GraphClusterer.configdata.logger
        logger.debug("Debugging from inside MKNN_init method")

        #setting up the input matrices
        #Create SM and SM_orig
        GraphClusterer.graphdata.create_SM_from_relfile(GraphClusterer.configdata.inp_rel_file)

        #Expand SM
        GraphClusterer.graphdata.setup_expanded_SM(GraphClusterer.configdata.nhops, GraphClusterer.configdata.inp_rel_file)

        #Create Edge Objects
        GraphClusterer.graphdata.create_edge_objects()
        #self.helper.print_dict(GraphClusterer.graphdata.edge_dict)
        #self.helper.print_set(GraphClusterer.graphdata.node_dict[1].node_edges_dict[EdgeType.secondary])
        #print(GraphClusterer.graphdata.edge_dict[011].edge_id)

        #Initialize all K evaluation objects for both phases
        self.phase1_allKevaluationdata = AllKEvaluationData(self.configdata, 1) #1 for phase=1
        self.phase2_allKevaluationdata = AllKEvaluationData(self.configdata, 2) #2 for phase=2

    #############################
    #Run MKNN for one value of K
    #############################
    def MKNN_worker(self, K):
        self.phase1data = Phase1Data(GraphClusterer.graphdata,
                                     GraphClusterer.configdata,
                                     K)
        self.MKNN_Phase1()
        self.phase2data = Phase2Data(GraphClusterer.graphdata,
                                     GraphClusterer.configdata,
                                     K,
                                     self.phase1data.cnodes_dict,
                                     self.phase1data.next_cluster_label,
                                     self.phase1data.num_clusters
                                     )
        self.MKNN_Phase2()

    def MKNN_Phase1(self):

        #Initialize Phase 1
        self.phase1data.initialize_phase()
        self.helper.print_list(self.phase1data.graphdata.node_dict[10].MKNN_list)
        print('Degree')
        print((self.phase1data.graphdata.node_dict[10].degree))
        print('CI_list')
        #self.helper.print_list(self.phase1data.cluster_initiator_list)
        self.helper.convert_list_ids_to_codes(self.graphdata, self.phase1data.cluster_initiator_list)

        #print((self.phase1data.graphdata.CI_list[0]))

        #Execute Phase 1
        self.phase1data.execute_phase()


        #Visualize Phase 1 results
        self.phase1data.visualize_phase()

        #Evaluate phase
        self.phase1data.evaluate_phase()
        self.phase1_allKevaluationdata.add_evaluation_for_K(self.phase1data.phase1_evaluation_data)

    def MKNN_Phase2(self):

        #Initialize phase 2
        self.phase2data.initialize_phase()

        #self.helper.print_list(self.phase2data.c_SM)

        #self.helper.print_list(self.phase2data.c_SM_sort)

        #Execute phase 2
        self.phase2data.execute_phase()

        #Visualize phase
        self.phase2data.visualize_phase()

        #Evaluate Phase
        self.phase2data.evaluate_phase()
        self.phase2_allKevaluationdata.add_evaluation_for_K(self.phase2data.phase2_evaluation_data)

        #self.helper.print_list(self.phase2data.phase2_evaluation_data.gold_standard_CL_list)
        self.helper.print_list(self.phase2data.phase2_evaluation_data.contingency_matrix)
        print("sensitivity:")
        print(self.phase2data.phase2_evaluation_data.sensitivity)
        print("PPV")
        print(self.phase2data.phase2_evaluation_data.PPV)
        print("accuracy")
        print(self.phase2data.phase2_evaluation_data.accuracy)


if __name__ == "__main__":
    gc = GraphClusterer(2)
    gc. MKNN_worker_wrapper()


