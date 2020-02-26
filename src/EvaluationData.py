__author__ = 'divya'

import pandas as pd
from CNodeData import CNodeData
from AlgorithmName import AlgorithmName
import operator
import numpy as np
from scipy.misc import comb
from RandIndex_Calculator import RandIndex_Calculator

class EvaluationData(object):
    def __init__(self, graphdata, configdata, K, phase, num_clusters, cnodes_dict, algorithm_name):

        #parameters
        self.graphdata = graphdata
        self.configdata = configdata
        self.K = K
        self.phase = phase
        self.num_clusters = num_clusters
        self.cnodes_dict = cnodes_dict
        self.algorithm_name = algorithm_name

        #measures to be calculated
        self.num_clusters_size_3_or_more = 0
        self.num_clusters_size_2_or_more = 0
        self.average_mean_clusters = 0.0
        self.average_variance_clusters = 0.0
        self.average_standard_deviation_clusters = 0.0
        self.average_structural_density_clusters = 0.0
        self.max_cluster_size = 0.0
        self.min_cluster_size = 0.0

        #Sn and PPV
        self.num_gold_standard_complexes = 0
        self.sensitivity = 0.0
        self.PPV = 0.0
        self.accuracy = 0.0
        self.rand_index = 0.0
        self.contingency_matrix = []
        self.gold_standard_CL_list = [] #this list can be used for visualization of gold
                                        #standard complexes.
        #Recall and Precision
        #self.recall_list = []
        #self.precision_list = []
        #self.fmeasure_dict = []
        #self.best_matching_cluster_dict = {}
        self.f_measure_dict = {}
        self.contingency_matrix_cnode_id_map = {}

        self.gold_standard_cnodes_dict = {}




    #This method performs different steps for evaluation after a phase
    # (for one K)
    def calculate_evaluation_measures_for_one_K(self):

        self.configdata.logger.debug("Debugging from inside calculate_evaluation_measures_for_one_K method of class EvaluationData.")

        #CL_list_unique = list(set(self.CL_list))

        #Measures of individual clusters
        (mean_list, variance_list, struct_density_list, node_count_list) = self.eval_calc_measures()

        #Average measures
        self.eval_calc_average_measures(mean_list, variance_list, struct_density_list, node_count_list)

        # #commented temporarily
        if self.phase == 2:
             #Calculate Sn and PPV and accuracy
             self.eval_calc_accuracy(self.configdata.gold_standard_file)
             #Calculate Rand Index
             self.calculate_rand_index()

             self.eval_calc_f_measure(self.configdata.complex_codes_file)
             self.eval_calc_avg_cnode_avg_measures(self.configdata.evol_rates_file, self.configdata.essentiality_file, self.configdata.phyletic_age_file)


             #Print cluster stats
             #self.print_cluster_stats()

             # #Calculate total avg evolutionary rates for cores and peripheries
             # #Results meaningful only for PPI datasets
             # self.eval_calculate_total_avg_evol_rate()


        #Write the average measures to a file
        a_name = AlgorithmName()
        filename = self.configdata.eval_results_dir + "/stats/phase" + str(self.phase) + "/" + self.configdata.currentdate_str + "_" + str(a_name.get_algorithm_name(self.algorithm_name)) + "_" + self.configdata.dataset_name + "_K_All" + "_Phase_" + str(self.phase) + "_stats.txt"

        self.eval_print_summary_stats(filename)

        #Also print a summary list of all clusters formed to the same file.
        self.eval_print_clusters_summary_format(filename)

        ###########################




    #Method to calculate evaluation measures for all clusters.
    def eval_calc_measures(self):
        mean_list = []
        variance_list = []
        struct_density_list = []
        node_count_list = []

        self.configdata.logger.debug("Debugging from inside eval_calc_measures method of class EvaluationData.")

        for cnode_id, cnode_data in self.cnodes_dict.items():
            if cnode_data.active == True:
                #mean of cnode
                if cnode_data.isDirty == True:
                    cnode_data.calculate_cnode_secondary_fields()

                #cnode_data.calculate_cnode_insim()
                #cnode_data.calculate_cnode_mean_edges()
                mean_list.append(cnode_data.mean_edges)

                #variance of cnode
                #cnode_data.calculate_cnode_standard_deviation_edges()
                variance_list.append(cnode_data.standard_deviation_edges * cnode_data.standard_deviation_edges)

                #structural density of cnode
                #cnode_data.calculate_cnode_struct_density()
                struct_density_list.append(cnode_data.struct_density)

                #number of nodes in the cnode
                node_count_list.append(cnode_data.num_nodes)


        return (mean_list, variance_list, struct_density_list, node_count_list)

    #This method calculates all average measures of clustering
    def eval_calc_average_measures(self, mean_list, variance_list,  struct_density_list, node_count_list):
        numerator_mean = 0
        numerator_variance = 0
        numerator_struct_density = 0
        numerator_standard_deviation = 0
        self.num_clusters_size_3_or_more = 0

        self.configdata.logger.debug("Debugging from inside eval_calc_average_measures method of class EvaluationData.")


        for i in range(0, self.num_clusters):
            if(node_count_list[i] > 2):
                self.num_clusters_size_3_or_more = self.num_clusters_size_3_or_more + 1
                if(node_count_list[i] >=2):
                    self.num_clusters_size_2_or_more = self.num_clusters_size_2_or_more + 1
                numerator_mean = numerator_mean + mean_list[i]
                numerator_variance = numerator_variance + variance_list[i]
                numerator_standard_deviation = numerator_standard_deviation + variance_list[i]**0.5
                numerator_struct_density = numerator_struct_density + struct_density_list[i]

        if self.num_clusters_size_3_or_more != 0:
            self.average_mean_clusters = (float) (numerator_mean)/ (float) (self.num_clusters_size_3_or_more)
            self.average_variance_clusters = (float) (numerator_variance)/ (float) (self.num_clusters_size_3_or_more)
            self.average_standard_deviation_clusters = (float) (numerator_standard_deviation)/ (float) (self.num_clusters_size_3_or_more)
            self.average_structural_density_clusters = (float) (numerator_struct_density)/ (float) (self.num_clusters_size_3_or_more)
        else:
            self.average_mean_clusters = 0
            self.average_variance_clusters = 0
            self.average_standard_deviation_clusters = 0
            self.average_struct_density = 0

        self.min_cluster_size = min(node_count_list)
        self.max_cluster_size = max(node_count_list)

    #This method prints summary measures calculated for the cludters, along with a list of clusters
    def eval_print_summary_stats(self, filename):

        self.configdata.logger.debug("Debugging from inside eval_print_summary_stats method of class EvaluationData.")

        target = open(filename, 'a')
        target.write("Graph Statistics:\n")
        target.write("Structural density of graph: ")
        target.write(str(self.graphdata.graph_struct_density))
        target.write("\n")
        target.write("Standard deviation of graph:")
        target.write(str(self.graphdata.graph_std))
        target.write("\n")
        target.write("Clustering Statistics:")
        target.write("\n")
        target.write("K:")
        target.write(str(self.K))
        target.write("\n")
        target.write("Phase of clustering:")
        target.write(str(self.phase))
        target.write("\n")
        target.write("Number Clusters:")
        target.write(str(self.num_clusters))
        target.write("\n")
        target.write("Number of clusters of size greater than 2:")
        target.write(str(self.num_clusters_size_3_or_more))
        target.write("\n")
        target.write("Average Mean:")
        target.write(str(self.average_mean_clusters))
        target.write("\n")
        target.write("Average Variance:")
        target.write(str(self.average_variance_clusters))
        target.write("\n")
        target.write("Average Structural Density:")
        target.write(str(self.average_structural_density_clusters))
        target.write("\n")
        target.write("Minimum cluster size:")
        target.write(str(self.min_cluster_size))
        target.write("\n")
        target.write("Maximum cluster size:")
        target.write(str(self.max_cluster_size))
        target.write("\n")
        if(self.phase == 2):
            target.write("Sensitivity:")
            target.write(str(self.sensitivity))
            target.write("\n")
            target.write("PPV:")
            target.write(str(self.PPV))
            target.write("\n")
            target.write("Accuracy:")
            target.write(str(self.accuracy))
            target.write("\n")
            target.write("Rand index:")
            target.write(str(self.rand_index))
            target.write("\n")
        target.write("\n")

        target.close()

    #This method prints the clusters into the summary file.
    #The format used in this method is different than the format used in the printClusters method.
    def eval_print_clusters_summary_format(self, filename):

        self.configdata.logger.debug("Debugging from inside eval_print_clusters_summary_format method of class EvaluationData.")

        target = open(filename, 'a')

        for cnode_id, cnode_data in self.cnodes_dict.items():
            if cnode_data.active == True:
                target.write("Cluster no.:")
                target.write(str(cnode_id))
                target.write(":\n")
                #print the cnode
                target.write("CLUSTER NODESET:\n")
                self.print_nodeset(cnode_id, target)
                target.write("CLUSTER MERGE TREE:\n")
                #print the merging tree of the cnode
                self.print_cnode_tree(cnode_id, target)

        target.write("\n")
        target.write("\n")

        target.close()

    #Print nodeset belonging to a cnode to a file
    def print_nodeset(self, cnode_id, target):
        cnode_data = self.cnodes_dict[cnode_id]
        for node_cnode_i in cnode_data.node_set:
            target.write(str(self.graphdata.node_dict[node_cnode_i].node_code))
            target.write(",")
        # target.write("\n")

    #Print the merge tree about the components cnodes of a cnode to a file
    def print_cnode_tree(self, cnode_id, target):
        cnode_child_id = cnode_id
        if cnode_child_id != -1:
            cnode_child_data = self.cnodes_dict[cnode_child_id]
            cnode_parent_id_1 = cnode_child_data.cnode_parent_id_1
            cnode_parent_id_2 = cnode_child_data.cnode_parent_id_2

            if(cnode_parent_id_1 != -1):
                self.print_nodeset(cnode_parent_id_1, target)

            if(cnode_parent_id_2 != -1):
                self.print_nodeset(cnode_parent_id_2, target)

            self.print_cnode_tree(cnode_parent_id_1, target)
            self.print_cnode_tree(cnode_parent_id_2, target)


    def eval_calc_accuracy(self, file_name):
        #Read gold standard complexes
        self.read_gold_standard_complexes(file_name)

        #Create contingency table
        self.create_contingency_table()

        #Calculate Sn and PPV
        self.calculate_Sn_PPV()

        #Calculate accuracy
        self.calculate_accuracy()

        #Print Sn and PPV



    def eval_calc_f_measure(self, complex_codes_file):
        self.generate_f_measure_dict(complex_codes_file)

    def eval_calc_avg_cnode_avg_measures(self, evol_rates_file, essentiality_file, phyletic_age_file):
        self.calculate_all_cnodes_avg_measures(evol_rates_file, essentiality_file, phyletic_age_file)

    # Read the gold standard complexes file
    def read_gold_standard_complexes(self, file_name):
        self.configdata.logger.debug("Debugging from inside read_gold_standard_complexes method of class EvaluationData.")

        self.gold_standard_CL_list = [-1]*self.graphdata.num_nodes

        file_read = pd.read_csv(
            filepath_or_buffer= file_name,
            header=None,
            sep=' ')

        file_read.columns = ['cluster_id', 'node_id', 'node_code']

        for i in range(0, file_read.shape[0]):
            #print(str(file_read['node_id'][i]))
            self.gold_standard_CL_list[file_read['node_id'][i]] =  file_read['cluster_id'][i]
            if(self.gold_standard_cnodes_dict.get(file_read['cluster_id'][i]) == None):
                cnode = CNodeData(file_read['cluster_id'], -1, -1, -1, self.graphdata, self.configdata)
                cnode.node_set.add(file_read['node_id'][i])
                self.gold_standard_cnodes_dict[file_read['cluster_id'][i]] = cnode
                self.num_gold_standard_complexes = self.num_gold_standard_complexes + 1
            else:
                self.gold_standard_cnodes_dict[file_read['cluster_id'][i]].node_set.add(file_read['node_id'][i])

    #Create a contingency table to calculate Sn and PPV
    #for predicted clusters of size greater than = 3.
    def create_contingency_table(self):
        self.configdata.logger.debug("Debbuging from inside create_contingency_table method.")

        #Intialize the size of the contingency matrix.
        self.contingency_matrix = [[0]*self.num_gold_standard_complexes for i in range(0, self.num_clusters_size_3_or_more)]

        #Compute the values of contingency matrix
        #The predicted clusters are given a random
        #order in the final matrix because of lack of
        #a serial order in them.
        i=0
        for cnode_id, cnode_data_i in self.cnodes_dict.items():
            if cnode_data_i.active == True and len(cnode_data_i.node_set) >=3:
                for j in range(0, self.num_gold_standard_complexes):
                    cnode_data_j = self.gold_standard_cnodes_dict[j]
                    self.contingency_matrix[i][j] = len(cnode_data_i.node_set.intersection(cnode_data_j.node_set))
                self.contingency_matrix_cnode_id_map[i] = cnode_data_i.cnode_id
                i = i + 1

    #Method to calculate Sn and PPV
    def calculate_Sn_PPV(self):
        self.configdata.logger.debug("Debbuging from inside calculate_Sn_PPV method.")
        self.calculate_Sn()
        self.calculate_PPV()

    #Method to calculate Sn
    def calculate_Sn(self):
        self.configdata.logger.debug("Debbuging from inside calculate_Sn method.")
        sn_denominator = 0
        sn_numerator = 0

        for j in range(0, self.num_gold_standard_complexes):
            cnode_data_j = self.gold_standard_cnodes_dict[j]
            sn_denominator = sn_denominator + len(cnode_data_j.node_set)

            sn_numerator_temp_value = max([self.contingency_matrix[i][j] for i in range(0, self.num_clusters_size_3_or_more)])

            sn_numerator = sn_numerator + sn_numerator_temp_value

        self.sensitivity = (float) (sn_numerator)/ (float) (sn_denominator)
        print("Sn:")
        print(str(self.sensitivity))

    #Method to calculate PPV
    def calculate_PPV(self):
        self.configdata.logger.debug("Debbuging from inside calculate_PPV method.")
        ppv_numerator = 0
        ppv_denominator = 0

        for i in range(0, self.num_clusters_size_3_or_more):
            ppv_numerator_temp_value = max([self.contingency_matrix[i][k] for k in range(0, self.num_gold_standard_complexes)])
            ppv_numerator = ppv_numerator + ppv_numerator_temp_value

            ppv_denominator_temp_value = sum([self.contingency_matrix[i][k] for k in range(0, self.num_gold_standard_complexes)])
            ppv_denominator = ppv_denominator + ppv_denominator_temp_value

        self.PPV = (float) (ppv_numerator)/ (float) (ppv_denominator)
        print("PPV")
        print(str(self.PPV))

    #Method to calculate accuracy
    #as geometric mean of sensitivity and PPV.
    def calculate_accuracy(self):
        self.accuracy = (self.sensitivity * self.PPV)
        #self.accuracy = self.accuracy ** self.accuracy
        self.accuracy = self.accuracy ** (0.5)
        print("Accuracy")
        print(str(self.accuracy))
        print(str(self.configdata.GO_TYPE))

    def generate_f_measure_dict(self, complex_codes_file):
        self.configdata.logger.debug("Debugging from inside generate_f_measure_dict methid of class EvaluationData.")

        complex_codes_dict = self.read_complex_codes_file(complex_codes_file)

        for i in range(0, self.num_clusters_size_3_or_more):
            intersection_list = [self.contingency_matrix[i][k] for k in range(0, self.num_gold_standard_complexes)]
            best_matching_complex_id, max_intersection_value = max(enumerate(intersection_list), key=operator.itemgetter(1))

            recall = (float)(max_intersection_value)/(float)(len(self.gold_standard_cnodes_dict[best_matching_complex_id].node_set))

            precision = (float)(max_intersection_value)/(float)(self.cnodes_dict[self.contingency_matrix_cnode_id_map[i]].num_nodes)

            f_measure = self.calculate_f_measure(recall, precision)

            self.add_cnode_to_f_measure_dict(self.contingency_matrix_cnode_id_map[i], recall, precision, f_measure, best_matching_complex_id, complex_codes_dict[best_matching_complex_id])

    def calculate_f_measure(self, recall, precision):
        self.configdata.logger.debug("Debugging from inside calculate_f_measure method of class EvaluationData.")
        if recall == 0 and precision == 0:
            f_measure = 0.0
        else:
            f_measure = float(2 * recall * precision)/ float(recall + precision)
        #print('f_measure')
        #print(str(f_measure))
        return f_measure

    #Method to add a cnode to periphery dict
    def add_cnode_to_f_measure_dict(self, cnode_id, recall, precision, f_measure, best_matching_complex_id, best_matching_complex_name):
        self.configdata.logger.debug("Debugging from inside add_cnode_to_f_measure_dict"
                                     "method of class Evaluation_Data.")
        if cnode_id not in self.f_measure_dict:
            self.f_measure_dict[cnode_id] = {'recall' : float, 'precision' : float , 'f_measure' : float, 'best_matching_complex_id' : int, 'best_matching_complex_name' : 'S'}

        self.f_measure_dict[cnode_id]['recall'] = recall
        self.f_measure_dict[cnode_id]['precision'] = precision
        self.f_measure_dict[cnode_id]['f_measure'] = f_measure
        self.f_measure_dict[cnode_id]['best_matching_complex_id'] = best_matching_complex_id
        self.f_measure_dict[cnode_id]['best_matching_complex_name'] = best_matching_complex_name

    def read_complex_codes_file(self, complex_codes_file):
        self.configdata.logger.debug("Debugging from inside read_complex_codes file method"
                                     "of class EvaluationData.")
        complex_codes_dict = {}

        file_read = pd.read_csv(
            filepath_or_buffer= complex_codes_file,
            header=None,
            sep=' ')

        file_read.columns = ['complex_id', 'complex_name']

        for i in range(0, file_read.shape[0]):
            complex_codes_dict[int(file_read['complex_id'][i])] = file_read['complex_name'][i]

        return complex_codes_dict

    def calculate_all_cnodes_avg_measures(self, evol_rates_file, essentiality_file, phyletic_age_file):
        self.configdata.logger.debug("Debugging from inside calculate_avg_evol_rate "
                                     "method of class EvaluationData.")

        evol_rates_dict = self.read_evol_rates_file(evol_rates_file)

        essentiality_dict = self.read_essentiality_file(essentiality_file)

        phyletic_age_dict = self.read_phyletic_age_file(phyletic_age_file)

        for cnode_id, cnode_data_i in self.cnodes_dict.items():
            if cnode_data_i.active == True and len(cnode_data_i.node_set) >=3:
                node_set = cnode_data_i.node_set
                sum_evol_rate = 0
                num_evol_rate = 0
                sum_essentiality = 0
                num_essentiality = 0
                sum_phyletic_age = 0
                num_phyletic_age = 0

                for node_id in node_set:
                    if node_id in evol_rates_dict:
                        if evol_rates_dict[node_id] != -1:
                            #print('node id found in evol_rates_dict.')
                            #print(str(evol_rates_dict[node_id]))
                            sum_evol_rate = sum_evol_rate + evol_rates_dict[node_id]
                            num_evol_rate = num_evol_rate + 1
                    else:
                        pass

                    if node_id in essentiality_dict:
                        num_essentiality = num_essentiality + 1
                        if 'Y' in essentiality_dict[node_id]:
                            #print('node id found in evol_rates_dict.')
                            #print(str(evol_rates_dict[node_id]))
                            sum_essentiality = sum_essentiality + 1

                    else:
                        pass

                    if node_id in phyletic_age_dict:
                        if phyletic_age_dict[node_id] != -1:
                            #print('node id found in evol_rates_dict.')
                            #print(str(evol_rates_dict[node_id]))
                            sum_phyletic_age = sum_phyletic_age + phyletic_age_dict[node_id]
                            num_phyletic_age = num_phyletic_age + 1
                    else:
                        pass


                cnode_data_i.avg_evol_rate = self.calculate_cnode_avg_measure(sum_evol_rate, num_evol_rate)
                cnode_data_i.perc_essential_genes = self.calculate_cnode_avg_measure(sum_essentiality, num_essentiality)
                cnode_data_i.avg_phyletic_age = self.calculate_cnode_avg_measure(sum_phyletic_age, num_phyletic_age)

    def calculate_cnode_avg_measure(self, sum_evol_rate, num_evol_rate):
        if num_evol_rate != 0:
            avg_evol_rate = float(sum_evol_rate)/float(num_evol_rate)
        else:
            avg_evol_rate = -1
        return avg_evol_rate

    def read_evol_rates_file(self, evol_rates_file):
        self.configdata.logger.debug("Debugging from inside read_evol_rates_file method of"
                                     "class EvaluationData")
        evol_rates_dict = {}

        file_read = pd.read_csv(
            filepath_or_buffer= evol_rates_file,
            header=None,
            sep=' ')

        file_read.columns = ['node_id', 'node_name', 'evol_rate']

        for i in range(0, file_read.shape[0]):
            evol_rates_dict[int(file_read['node_id'][i])] = (float) (file_read['evol_rate'][i])

        return evol_rates_dict

    def read_essentiality_file(self, essentiality_file):
        self.configdata.logger.debug("Debugging from inside read_evol_rates_file method of"
                                     "class EvaluationData")
        essentiality_dict = {}

        file_read = pd.read_csv(
            filepath_or_buffer= essentiality_file,
            header=None,
            sep=' ')

        file_read.columns = ['node_id', 'node_name', 'essential']

        for i in range(0, file_read.shape[0]):
            essentiality_dict[int(file_read['node_id'][i])] = (str) (file_read['essential'][i])

        return essentiality_dict

    def read_phyletic_age_file(self, phyletic_age_file):
        self.configdata.logger.debug("Debugging from inside read_phyletic_age_file method of"
                                     "class EvaluationData")
        phyletic_age_dict = {}

        file_read = pd.read_csv(
            filepath_or_buffer= phyletic_age_file,
            header=None,
            sep=' ')

        file_read.columns = ['node_id', 'node_name', 'phyletic_age']

        for i in range(0, file_read.shape[0]):
            phyletic_age_dict[int(file_read['node_id'][i])] = (float) (file_read['phyletic_age'][i])

        return phyletic_age_dict

    def print_cluster_stats(self):
        self.configdata.logger.debug("Debugging from inside printCluster_stats method of Evaluation Data class.")

        a_name = AlgorithmName()
        filename = self.configdata.eval_results_dir + "/docs/phase" + str(self.phase)+ "/" + self.configdata.currentdate_str + "_" + str(a_name.get_algorithm_name(self.algorithm_name)) + "_" + self.configdata.dataset_name + "_K_" + str(self.K) + "_Phase_" + str(self.phase) + "_print_cluster_stats.txt"
        target = open(filename, 'w')

        for cnode_id, cnode_data in self.cnodes_dict.items():
            if cnode_data.num_nodes >=3:
                target.write(str(cnode_id))
                target.write("\t")
                target.write(str(cnode_data.num_nodes))
                target.write("\t")
                target.write(str(cnode_data.mean_edges))
                target.write("\t")
                target.write(str(cnode_data.standard_deviation_edges))
                target.write("\t")
                target.write(str(cnode_data.struct_density))
                target.write("\t")
                target.write(str(self.f_measure_dict[cnode_id]['f_measure']))
                target.write("\n")

    def calculate_rand_index(self):
        rc = RandIndex_Calculator()
        rc = RandIndex_Calculator()
        tp, fp, tn, fn = rc.get_tp_fp_tn_fn(np.array(self.contingency_matrix).transpose())
        print("TP: %d, FP: %d, TN: %d, FN: %d" % (tp, fp, tn, fn))

        # Print the measures:
        print("Rand index: %f" % (float(tp + tn) / (tp + fp + fn + tn)))

        self.rand_index = float(tp + tn) / (tp + fp + fn + tn)
        precision = float(tp) / (tp + fp)
        recall = float(tp) / (tp + fn)

        print("Precision : %f" % precision)
        print("Recall    : %f" % recall)
        print("F1        : %f" % ((2.0 * precision * recall) / (precision + recall)))
