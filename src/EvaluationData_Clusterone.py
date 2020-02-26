__author__ = 'divya'

from EvaluationData import EvaluationData
from AlgorithmName import AlgorithmName
from CNodeData import ClusterStatus

class EvaluationData_Clusterone(EvaluationData):

    def __init__(self, graphdata, configdata, K, phase, num_clusters, cnodes_dict, algorithm_name):
        super(EvaluationData_Clusterone, self).__init__(graphdata, configdata, K, phase, num_clusters, cnodes_dict, algorithm_name)

        self.level1_perc_essential_genes = 0
        self.level2_perc_essential_genes = 0
        self.level3_perc_essential_genes = 0
        self.level1_avg_struct_density = 0
        self.level2_avg_struct_density = 0
        self.level3_avg_struct_density = 0
        self.level1_avg_mean = 0
        self.level2_avg_mean = 0
        self.level3_avg_mean = 0
        self.level1_avg_standard_deviation = 0
        self.level2_avg_standard_deviation = 0
        self.level3_avg_standard_deviation = 0
        # #For Gavin Dataset (Old values: outdated now)
        # self.level1_num_cnodes = 22
        # self.level2_num_cnodes = 153
        # self.level3_num_cnodes = 51

        # For Krogan Dataset (Old values:outdated now)
        # self.level1_num_cnodes = 16
        # self.level2_num_cnodes = 248
        # self.level3_num_cnodes = 52

        # #For Gavin Dataset
        # self.level1_num_cnodes = 27
        # self.level2_num_cnodes = 149
        # self.level3_num_cnodes = 52

        # # #For Krogan Dataset
        # self.level1_num_cnodes = 14
        # self.level2_num_cnodes = 247
        # self.level3_num_cnodes = 55

        # #For Collins Dataset
        # self.level1_num_cnodes = 31
        # self.level2_num_cnodes = 59
        # self.level3_num_cnodes = 27

        # #For A2Zsim dataset
        # self.level1_num_cnodes = 2
        # self.level2_num_cnodes = 3
        # self.level3_num_cnodes = 2

        #For A2Zsim dataset
        self.level1_num_cnodes = 2
        self.level2_num_cnodes = 4
        self.level3_num_cnodes = 2

    #Overriding the base class method:
    # This method performs different steps for evaluation after a phase
    # (for one K)
    def calculate_evaluation_measures_for_one_K(self):
        self.configdata.logger.debug("Debugging from inside calculate_evaluation_measures_"
                                     "for_one_K method of class EvaluationData_Clusterone class.")

        super().calculate_evaluation_measures_for_one_K()

        #Write the average measures to a file
        a_name = AlgorithmName()
        filename_1 = self.configdata.eval_results_dir + "/stats/phase" + str(self.phase) + "/" + self.configdata.currentdate_str + "_" + str(a_name.get_algorithm_name(self.algorithm_name)) + "_" + self.configdata.dataset_name + "_K_All" + "_Phase_" + str(self.phase) + "_stats_CP_1.txt"
        filename_3 = self.configdata.eval_results_dir + "/stats/phase" + str(self.phase) + "/" + self.configdata.currentdate_str + "_" + str(a_name.get_algorithm_name(self.algorithm_name)) + "_" + self.configdata.dataset_name + "_K_All" + "_Phase_" + str(self.phase) + "_stats_CP_3.txt"

        if self.phase == 2:
            #Calculate total average measures
            self.eval_calculate_total_avg_measures()
            #Print the global_core_periphery relationships
            self.eval_print_summary_stats_CP_1(filename_1)
            self.eval_print_coreperiphery_summary_format(filename_3)


    def eval_calculate_total_avg_measures(self):
        self.configdata.logger.debug("Debugging from inside eval_calculate_total_avg_measures method of "
                                     "EvaluationData_Clusterone class.")

        num_level1 = 0
        sum_level1_essentiality = 0
        sum_level1_standard_deviation = 0
        sum_level1_mean = 0
        sum_level1_struct_density = 0

        num_level2 = 0
        sum_level2_essentiality = 0
        sum_level2_standard_deviation = 0
        sum_level2_mean = 0
        sum_level2_struct_density = 0

        num_level3 = 0
        sum_level3_essentiality = 0
        sum_level3_standard_deviation = 0
        sum_level3_mean = 0
        sum_level3_struct_density = 0

        sorted_cnode_ids = sorted(list(self.cnodes_dict.keys()))

        count = 0
        for cnode_id in sorted_cnode_ids:
            cnode_data = self.cnodes_dict[cnode_id]
            if len(cnode_data.node_set) >= 3 and cnode_data.active == True:
                count = count + 1


                if count <= self.level1_num_cnodes:
                    #set core status for top level clusters,
                    #for comparison with clusterone-CP.
                    cnode_data.cnode_CP_status = ClusterStatus.core

                    #Calculate avg essentiality for top level1 cnodes

                    sum_level1_essentiality = sum_level1_essentiality + cnode_data.perc_essential_genes
                    num_level1 = num_level1 + 1
                    sum_level1_mean = sum_level1_mean + cnode_data.mean_edges
                    sum_level1_standard_deviation = sum_level1_standard_deviation + cnode_data.standard_deviation_edges
                    sum_level1_struct_density = sum_level1_struct_density + cnode_data.struct_density
                    #print("Cnode mean:")
                    #print(str(cnode_data.mean_edges))
                    #print("Cnode struct density:")
                    #print(str(cnode_data.struct_density))
                    #print(str(cnode_data.num_nodes))
                    #print("%s\t%s\t%s\t%s" % (str(cnode_data.mean_edges),str(cnode_data.struct_density),str(cnode_data.num_nodes), str(num_level1)))


                elif count <= (self.level1_num_cnodes + self.level2_num_cnodes):
                    #set coreandperiphery status for second level clusters,
                    #for comparison with clusterone-CP.
                    cnode_data.cnode_CP_status = ClusterStatus.coreandperiphery
                    sum_level2_essentiality = sum_level2_essentiality + cnode_data.perc_essential_genes
                    num_level2 = num_level2 + 1
                    sum_level2_mean = sum_level2_mean + cnode_data.mean_edges
                    sum_level2_standard_deviation = sum_level2_standard_deviation + cnode_data.standard_deviation_edges
                    sum_level2_struct_density = sum_level2_struct_density + cnode_data.struct_density
                    #print("%s\t%s\t%s\t%s" % (str(cnode_data.mean_edges),str(cnode_data.struct_density),str(cnode_data.num_nodes), str(num_level1)))

                elif count <= (self.level1_num_cnodes + self.level2_num_cnodes + self.level3_num_cnodes):
                    #set periphery status for third level clusters,
                    #for comparison with clusterone-CP.
                    cnode_data.cnode_CP_status = ClusterStatus.periphery
                    sum_level3_essentiality = sum_level3_essentiality + cnode_data.perc_essential_genes
                    num_level3 = num_level3 + 1
                    sum_level3_mean = sum_level3_mean + cnode_data.mean_edges
                    sum_level3_standard_deviation = sum_level3_standard_deviation + cnode_data.standard_deviation_edges
                    sum_level3_struct_density = sum_level3_struct_density + cnode_data.struct_density
                    #print("%s\t%s\t%s\t%s" % (str(cnode_data.mean_edges),str(cnode_data.struct_density),str(cnode_data.num_nodes), str(num_level1)))
                else:
                    break
            #print("Num level1")
            #print(num_level1)
            self.level1_perc_essential_genes = self.calculate_cnode_avg_measure(sum_level1_essentiality, num_level1)
            self.level2_perc_essential_genes = self.calculate_cnode_avg_measure(sum_level2_essentiality, num_level2)
            self.level3_perc_essential_genes = self.calculate_cnode_avg_measure(sum_level3_essentiality, num_level3)

            self.level1_avg_mean = self.calculate_cnode_avg_measure(sum_level1_mean, num_level1)
            self.level2_avg_mean = self.calculate_cnode_avg_measure(sum_level2_mean, num_level2)
            self.level3_avg_mean = self.calculate_cnode_avg_measure(sum_level3_mean, num_level3)


            self.level1_avg_standard_deviation = self.calculate_cnode_avg_measure(sum_level1_standard_deviation, num_level1)
            self.level2_avg_standard_deviation = self.calculate_cnode_avg_measure(sum_level2_standard_deviation, num_level2)
            self.level3_avg_standard_deviation = self.calculate_cnode_avg_measure(sum_level3_standard_deviation, num_level3)

            self.level1_avg_struct_density = self.calculate_cnode_avg_measure(sum_level1_struct_density, num_level1)
            self.level2_avg_struct_density = self.calculate_cnode_avg_measure(sum_level2_struct_density, num_level2)
            self.level3_avg_struct_density = self.calculate_cnode_avg_measure(sum_level3_struct_density, num_level3)


    def eval_print_summary_stats_CP_1(self, filename):
        self.configdata.logger.debug("Debugging from inside eval_print_summary_stats_CP_1 method of class EvaluationData_Clusterone.")
        target = open(filename, 'a')

        target.write("Num Level1 clusters (size >= 3):")
        target.write("\n")
        target.write(str(self.level1_num_cnodes))
        target.write("\n")
        target.write("Avg Level1 mean:")
        target.write("\n")
        target.write(str(self.level1_avg_mean))
        target.write("\n")
        target.write("Avg Level1 standard deviation:")
        target.write("\n")
        target.write(str(self.level1_avg_standard_deviation))
        target.write("\n")
        target.write("Avg Level1 structural density:")
        target.write("\n")
        target.write(str(self.level1_avg_struct_density))
        target.write("\n")
        target.write("Avg Level1 essentiality:")
        target.write("\n")
        target.write(str(self.level1_perc_essential_genes))
        target.write("\n")

        target.write("Num Level2 clusters (size >= 3):")
        target.write("\n")
        target.write(str(self.level2_num_cnodes))
        target.write("\n")
        target.write("Avg Level2 mean:")
        target.write("\n")
        target.write(str(self.level2_avg_mean))
        target.write("\n")
        target.write("Avg Level2 standard deviation:")
        target.write("\n")
        target.write(str(self.level2_avg_standard_deviation))
        target.write("\n")
        target.write("Avg Level2 structural density:")
        target.write("\n")
        target.write(str(self.level2_avg_struct_density))
        target.write("\n")
        target.write("Avg Level2 essentiality:")
        target.write("\n")
        target.write(str(self.level2_perc_essential_genes))
        target.write("\n")

        target.write("Num Level3 clusters (size >= 3):")
        target.write("\n")
        target.write(str(self.level3_num_cnodes))
        target.write("\n")
        target.write("Avg Level3 mean:")
        target.write("\n")
        target.write(str(self.level3_avg_mean))
        target.write("\n")
        target.write("Avg Level3 standard deviation:")
        target.write("\n")
        target.write(str(self.level3_avg_standard_deviation))
        target.write("\n")
        target.write("Avg Level3 structural density:")
        target.write("\n")
        target.write(str(self.level3_avg_struct_density))
        target.write("\n")
        target.write("Avg Level3 essentiality:")
        target.write("\n")
        target.write(str(self.level3_perc_essential_genes))
        target.write("\n")

    #This method prints the clusters into the summary file.
    #The format used in this method is different than the format used in the printClusters method.
    def eval_print_coreperiphery_summary_format(self, filename):

        self.configdata.logger.debug("Debugging from inside eval_print_clusters_summary_format method of class EvaluationData_Clusterone_CP.")

        target = open(filename, 'a')
        target.write("CPStatus\tcnode_id\tcluster nodes\tcnode_size\tcnode_mean\tcnode_standdev\tcnode_structdens\n")
        for cnode_id, cnode_data in self.cnodes_dict.items():
            if cnode_data.active == True and cnode_data.num_nodes >= 3:
                target.write(str(cnode_data.cnode_CP_status))
                target.write("\t")
                target.write(str(cnode_id))
                target.write("\t")
                self.print_nodeset(cnode_id, target)
                target.write("\t")
                target.write(str(cnode_data.num_nodes))
                target.write("\t")
                target.write(str(cnode_data.mean_edges))
                target.write("\t")
                target.write(str(cnode_data.standard_deviation_edges))
                target.write("\t")
                target.write(str(cnode_data.struct_density))
                target.write("\n")

        target.close()
