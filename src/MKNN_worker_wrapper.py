__author__ = 'divya'

import os
import datetime
import configparser as cp

from .MKNN_worker import MKNN_worker
from .eval_plot_summary_measures import eval_plot_summary_measures
from .MKNN_eval import MKNN_eval
from .MKNN_init import MKNN_init
from .config_ConfigSectionMap import ConfigSectionMap
from .config_get_logger import logger_class

def MKNN_worker_wrapper():

    ############################
    #Configuration Phase
    ############################
    code_dir = '/Users/divya/Documents/Dissertation/Dissertation'
    data_dir = '/Users/divya/Documents/input/Dissertation/data'
    log_dir = '/Users/divya/Documents/logs/Dissertation'
    Config = cp.ConfigParser()
    path_config_file = code_dir + "/settings_GMKNN.ini"
    Config.read(path_config_file)
    #Config.sections()

    #Read the name of the input relationships file
    inp_rel_file = ConfigSectionMap(Config, "InitializationPhase")['inp_rel_file']

    #Read the number of hops for matrix expansion
    nhops = (int) (ConfigSectionMap(Config, "InitializationPhase")['nhops'])

    #Read the range of K values for which the code needs to be run
    K_min = ConfigSectionMap(Config, "PhaseOne")['k_min']
    K_max = ConfigSectionMap(Config, "PhaseOne")['k_max']
    K_range = list(range((int)(K_min), (int)(K_max)+1))

    #Read the maximum number of clusters required in the final output
    max_num_clusters = (int) (ConfigSectionMap(Config, "PhaseTwo")['max_num_clusters'])

    #Read the directory name where all the evaluation results will be stored
    eval_results_dir = ConfigSectionMap(Config, "EvaluationPhase")['eval_results_dir']

    #Get the logger level (INFO, DEBUG)
    logger_level = ConfigSectionMap(Config, "General")['logger_level']

    #Get the currentdate for naming files
    currentdate = datetime.datetime.now()
    currentdate_str = currentdate.strftime("%Y_%m_%d_%I_%M")

    #Get the name of the dataset from the input_Rel_file
    dataset_name  = os.path.split(inp_rel_file)[1].split(".")[0]

    ###########################
    #Logging setup
    ##########################
    log = logger_class(currentdate_str, log_dir, logger_level)
    logger = log.get_logger(__name__)
    logger = log.get_logger('root')

    ###########################
    #Initialization Phase
    ##########################
    #print("Initialization phase of GMKNN begins.")
    logger.info("Initialization phase of GMKNN begins")
    logger.debug("A test logger debug message")

    (SM_orig, SM, num_nodes, node_codes) = MKNN_init(inp_rel_file, nhops, log)

    logger.info("Initialization phase of GMKNN ends.")

    ###################################################################################
    #Calling MKNN_worker for different values of K and appending the results to a file
    ###################################################################################

    #Name the output file based upon the current date

    filename_P1 = eval_results_dir + "/stats/phase1/" + currentdate_str + "_GMKNN_" + dataset_name + "_K_All" + "_Phase_1"  + "_stats.txt"
    filename_P2 = eval_results_dir + "/stats/phase2/" + currentdate_str + "_GMKNN_" + dataset_name + "_K_All" + "_Phase_2"  + "_stats.txt"

    num_clusters_List_P2 = []
    K_List = []
    num_clusters_size_3_or_more_List_P2 = []
    average_Mean_List_P2 = []
    average_Variance_List_P2 = []
    average_Standard_Deviation_List_P2 = []
    average_Struct_Density_List_P2 = []
    min_cluster_size_List_P2 = []
    max_cluster_size_List_P2 = []

    num_clusters_List_P1 = []
    num_clusters_size_3_or_more_List_P1 = []
    average_Mean_List_P1 = []
    average_Variance_List_P1 = []
    average_Standard_Deviation_List_P1 = []
    average_Struct_Density_List_P1 = []
    min_cluster_size_List_P1 = []
    max_cluster_size_List_P1 = []
    K=3

    logger.info("Running G-MKNN for different values of K.")

    for K in K_range:
        logger.info("Running G-MKNN for the value of K: ")
        print((str(K)))
        #Call MKNN_worker for the value of K
        (CL_List_P2, CL_List_P1, SM, SM_orig, num_clusters_P2, num_clusters_P1, num_nodes) = MKNN_worker(K, max_num_clusters, SM, SM_orig, num_nodes, node_codes, currentdate_str, dataset_name, eval_results_dir, log)

        #Calculate evaluation measures for phase 1
        (num_clusters_size_3_or_more, average_Mean, average_Variance, average_Standard_Deviation, average_Struct_Density, max_cluster_size, min_cluster_size) = MKNN_eval(CL_List_P1, SM, SM_orig, num_clusters_P1, num_nodes, node_codes, filename_P1, K, 1, log)

        #Save all phase 1 measures in a list
        num_clusters_List_P1.append(num_clusters_P1)
        K_List.append(K)
        num_clusters_size_3_or_more_List_P1.append(num_clusters_size_3_or_more)
        average_Mean_List_P1.append(average_Mean)
        average_Variance_List_P1.append(average_Variance)
        average_Standard_Deviation_List_P1.append(average_Standard_Deviation)
        average_Struct_Density_List_P1.append(average_Struct_Density)
        max_cluster_size_List_P1.append(max_cluster_size)
        min_cluster_size_List_P1.append(min_cluster_size)

        #Calculate evaluation measures for phase 2
        (num_clusters_size_3_or_more, average_Mean, average_Variance, average_Standard_Deviation, average_Struct_Density, max_cluster_size, min_cluster_size) = MKNN_eval(CL_List_P2, SM, SM_orig, num_clusters_P2, num_nodes, node_codes, filename_P2, K, 2, log)

        #Save all phase 2 measures in a list
        num_clusters_List_P2.append(num_clusters_P2)
        #K_List.append(K)
        num_clusters_size_3_or_more_List_P2.append(num_clusters_size_3_or_more)
        average_Mean_List_P2.append(average_Mean)
        average_Variance_List_P2.append(average_Variance)
        average_Standard_Deviation_List_P2.append(average_Standard_Deviation)
        average_Struct_Density_List_P2.append(average_Struct_Density)
        max_cluster_size_List_P2.append(max_cluster_size)
        min_cluster_size_List_P2.append(min_cluster_size)

        logger.info("G-MKNN run finished for K: ")
        print((str(K)))
        logger.info("and dataset:")
        logger.info(dataset_name)

    logger.info("Algorithm run for all K values, now plotting evaluation plots.")

    logger.info("Plotting evaluation measures for phase 1.")
    #Plot the evaluation measures for phase 1 against different values of K
    eval_plot_summary_measures(currentdate_str, dataset_name, 1, K_List, num_clusters_List_P1, num_clusters_size_3_or_more_List_P1, average_Mean_List_P1, average_Standard_Deviation_List_P1, average_Struct_Density_List_P1, min_cluster_size_List_P1, max_cluster_size_List_P1, eval_results_dir, log)

    logger.info("Plotting evaluation measures for phase 2.")
    #Plot the evaluation measures for phase 2 against different values of K
    eval_plot_summary_measures(currentdate_str, dataset_name, 2, K_List, num_clusters_List_P2, num_clusters_size_3_or_more_List_P2, average_Mean_List_P2, average_Standard_Deviation_List_P2, average_Struct_Density_List_P2, min_cluster_size_List_P2, max_cluster_size_List_P2, eval_results_dir, log)

    logger.info("Plotting of evaluation graphs done.")
    logger.info("GMKNN clustering finished")