__author__ = 'divya'

import os
import datetime
import configparser as cp
from config_ConfigSectionMap import ConfigSectionMap
from config_ConfigSectionMap import ConfigSectionMap
from config_get_logger import logger_class

class ConfigData():

    def __init__(self, code_dir, data_dir, log_dir):
        self.code_dir = code_dir
        self.data_dir = data_dir
        self.log_dir = log_dir
        self.inp_rel_file = ""
        self.gold_standard_file = ""
        self.nhops = -1
        self.K_min = -1
        self.K_max = -1
        self.Krange = []
        self.max_num_clusters = -1
        self.eval_results_dir = ""
        self.logger_level = ""
        self.currentdate_str = ""
        self.dataset_name = ""
        self.logger = None

        #Clusterone specific
        self.node_penalty = -1
        self.overlap_threshold = 0.0
        self.density_threshold = 0.0

        #Clusterone core periphery specific
        self.node_penalty_2 = -1
        self.mean_diff = -1

        #Raw file names
        self.inp_raw_file = ""

        #Dataset name
        self.dataset_name = ""

    ############################
    #Do configuration
    ###########################
    def do_config(self):
        self.do_config_variables()
        self.do_config_logger()

    ############################
    #Configuration of the logger
    ############################
    def do_config_logger(self):
        log = logger_class(self.currentdate_str, self.log_dir, self.logger_level)
        self.logger = log.get_logger('root')

    ######################################
    #Configuration of Clustering variables
    ######################################
    def do_config_variables(self):
        config_parser = cp.ConfigParser()
        path_config_file = self.code_dir + "/settings_GMKNN.ini"
        config_parser.read(path_config_file)

        #Read the name of the dataset
        self.dataset_name = ConfigSectionMap(config_parser, "InitializationPhase")['dataset_name']


        #Read the name of the input relationships file
        self.inp_rel_file = ConfigSectionMap(config_parser, "InitializationPhase")['inp_rel_file_'+ self.dataset_name]

        #Read the name of the gold standard complexes file
        self.gold_standard_file = ConfigSectionMap(config_parser, "EvaluationPhase")['gold_standard_file_' + self.dataset_name]

        #Read the name of complex codes file
        self.complex_codes_file = ConfigSectionMap(config_parser, "EvaluationPhase")['complex_codes_file_' + self.dataset_name]

        #Read the evolution rates file
        self.evol_rates_file = ConfigSectionMap(config_parser, "EvaluationPhase")['evol_rates_file_' + self.dataset_name]

        #Read the evolution rates file
        self.essentiality_file = ConfigSectionMap(config_parser, "EvaluationPhase")['essentiality_file_' + self.dataset_name]

        #Read the evolution rates file
        self.phyletic_age_file = ConfigSectionMap(config_parser, "EvaluationPhase")['phyletic_age_file_' + self.dataset_name]

        #Read the number of hops for matrix expansion
        self.nhops = (int) (ConfigSectionMap(config_parser, "InitializationPhase")['nhops'])

        #Read the range of K values for which the code needs to be run
        self.K_min = ConfigSectionMap(config_parser, "PhaseOne")['k_min']
        self.K_max = ConfigSectionMap(config_parser, "PhaseOne")['k_max']
        self.K_range = list(range((int)(self.K_min), (int)(self.K_max)+1))

        #Read the maximum number of clusters required in the final output
        self.max_num_clusters = (int) (ConfigSectionMap(config_parser, "PhaseTwo")['max_num_clusters'])

        #Read the directory name where all the evaluation results will be stored
        self.eval_results_dir = ConfigSectionMap(config_parser, "EvaluationPhase")['eval_results_dir']

        #Get the logger level (INFO, DEBUG)
        self.logger_level = ConfigSectionMap(config_parser, "General")['logger_level']

        #Get the currentdate for naming files
        currentdate = datetime.datetime.now()
        self.currentdate_str = currentdate.strftime("%Y_%m_%d_%I_%M")

        #Get the name of the dataset from the input_Rel_file
        self.get_dataset_name()

        #Clusterone specific variables
        #Read the value of node_penalty to be used in cohesion calculation
        self.node_penalty = (float)(ConfigSectionMap(config_parser, "ClusteroneSpecific")['node_penalty'])

        #Read the value of overlap_threshold to be used in merge phase
        self.overlap_threshold = (float)(ConfigSectionMap(config_parser, "ClusteroneSpecific")['overlap_threshold'])

        #Read the value of density_threshold to be used in prune phase
        self.density_threshold = (float)(ConfigSectionMap(config_parser, "ClusteroneSpecific")['density_threshold'])

        #Clusterone core periphery specific
        #Read the value of node_penalty_2 to be used in nodese_prospective calculation
        self.node_penalty_2 = (float)(ConfigSectionMap(config_parser, "ClusteroneSpecific")['node_penalty_2'])

        self.mean_diff = (float)(ConfigSectionMap(config_parser, "ClusteroneSpecific")['mean_diff'])

        #Raw files
        self.inp_raw_file = (ConfigSectionMap(config_parser, "RawFiles")['raw_file'])
        self.inp_raw_file_faculty_dataset = (ConfigSectionMap(config_parser, "RawFiles")['raw_file_faculty_dataset'])
        self.raw_mips_gold_standard_file = (ConfigSectionMap(config_parser, "RawFiles")['raw_mips_gold_standard_file'])
        self.raw_yeast_evolutionary_rates_file = (ConfigSectionMap(config_parser, "RawFiles")['raw_yeast_evolutionary_rates_file'])
        self.raw_yeast_evolutionary_rates_file_1 = (ConfigSectionMap(config_parser, "RawFiles")['raw_yeast_evolutionary_rates_file_1'])
        self.raw_essential_genes_file = (ConfigSectionMap(config_parser, "RawFiles")['raw_essential_genes_file'])
        self.raw_phyletic_age_file = (ConfigSectionMap(config_parser, "RawFiles")['raw_phyletic_age_file'])
        self.inp_raw_file_les_miserables = (ConfigSectionMap(config_parser, "RawFiles")['raw_file_les_miserables'])

        #GeneOntology Files and constants
        self.go_obo_file = (ConfigSectionMap(config_parser, "GeneOntology")['go_obo_file'])
        self.gene2go_file = (ConfigSectionMap(config_parser, "GeneOntology")['gene2go_file'])
        self.gene_syn_file = (ConfigSectionMap(config_parser, "GeneOntology")['gene_syn_file'])
        self.GO_TYPE = (ConfigSectionMap(config_parser, "GeneOntology")['go_type'])
        self.GO_SIM_TYPE = (ConfigSectionMap(config_parser, "GeneOntology")['go_sim_type'])
        self.GO_SIZE = (int)((ConfigSectionMap(config_parser, "GeneOntology")['go_size']))
        self.SIM_CUTOFF = (float)((ConfigSectionMap(config_parser, "GeneOntology")['sim_cutoff']))


    #########################################
    #Get dataset name from the input filename
    #########################################
    def get_dataset_name(self):
        self.dataset_name  = os.path.split(self.inp_rel_file)[1].split(".")[0]