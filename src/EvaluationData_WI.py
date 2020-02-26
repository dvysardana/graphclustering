__author__ = 'divya'

from EvaluationData import EvaluationData
from AlgorithmName import AlgorithmName
from CNodeData import ClusterStatus

class EvaluationData_WI(EvaluationData):


    def __init__(self, graphdata, configdata, K, phase, num_clusters, cnodes_dict, cnode_relationship_dict, algorithm_name):
        super(EvaluationData_WI, self).__init__(graphdata, configdata, K, phase, num_clusters, cnodes_dict, algorithm_name)
        self.cnode_relationship_dict = cnode_relationship_dict
        self.mean_diff = self.configdata.mean_diff
        self.node_penalty = self.configdata.node_penalty
        self.overlap_threshold = self.configdata.overlap_threshold

        self.core_num = 0
        self.periphery_num = 0
        self.coreperiphery_num = 0

        self.core_avg_evol_rate = 0
        self.periphery_avg_evol_rate = 0
        self.coreperiphery_avg_evol_rate = 0

        self.core_perc_essential_genes = 0
        self.periphery_perc_essential_genes = 0
        self.coreperiphery_perc_essential_genes = 0

        self.core_avg_phyletic_age = 0
        self.periphery_avg_phyletic_age = 0
        self.coreperiphery_avg_phyletic_age = 0

        self.core_avg_mean = 0
        self.periphery_avg_mean = 0
        self.coreperiphery_avg_mean = 0

        self.core_avg_standard_deviation = 0
        self.periphery_avg_standard_deviation = 0
        self.coreperiphery_avg_standard_deviation = 0

        self.core_avg_struct_density = 0
        self.periphery_avg_struct_density = 0
        self.coreperiphery_avg_struct_density = 0

        self.avg_type1_mean_difference = 0 #Type A,C,AF
        self.avg_type2_mean_difference = 0#Type B
        self.avg_type3_mean_difference = 0#Type E

        self.num_type1 = 0 #Type A,C,AF
        self.num_type2 = 0 #Type B
        self.num_type3 = 0 #Type E

        self.avg_type1_cohesion_difference = 0#Type A,C,AF
        self.avg_type2_cohesion_difference = 0#Type B
        self.avg_type3_cohesion_difference = 0#Type E

        self.avg_type1_cohesion_incdec = 0#Type A,C,AF
        self.avg_type2_cohesion_incdec = 0#Type B
        self.avg_type3_cohesion_incdec = 0#Type E

        self.avg_type1_struct_density_difference = 0#Type A,C,AF
        self.avg_type2_struct_density_difference = 0#Type B
        self.avg_type3_struct_density_difference = 0#Type E


    #Overriding base class method:
    # This method performs different steps for evaluation after a phase
    # (for one K)
    def calculate_evaluation_measures_for_one_K(self):
        self.configdata.logger.debug("Debugging from inside calculate_evaluation_measures_for_one_K method of class EvaluationData_WI.")

        super().calculate_evaluation_measures_for_one_K()

       #Write the average measures to a file
        a_name = AlgorithmName()
        filename = self.configdata.eval_results_dir + "/stats/phase" + str(self.phase) + "/" + self.configdata.currentdate_str + "_" + str(a_name.get_algorithm_name(self.algorithm_name)) + "_" + self.configdata.dataset_name + "_K_All" + "_Phase_" + str(self.phase) + "_stats_CP.txt"
        filename_1 = self.configdata.eval_results_dir + "/stats/phase" + str(self.phase) + "/" + self.configdata.currentdate_str + "_" + str(a_name.get_algorithm_name(self.algorithm_name)) + "_" + self.configdata.dataset_name + "_K_All" + "_Phase_" + str(self.phase) + "_stats_CP_1.txt"
        filename_2 = self.configdata.eval_results_dir + "/stats/phase" + str(self.phase) + "/" + self.configdata.currentdate_str + "_" + str(a_name.get_algorithm_name(self.algorithm_name)) + "_" + self.configdata.dataset_name + "_K_All" + "_Phase_" + str(self.phase) + "_stats_CP_2.txt"
        filename_3 = self.configdata.eval_results_dir + "/stats/phase" + str(self.phase) + "/" + self.configdata.currentdate_str + "_" + str(a_name.get_algorithm_name(self.algorithm_name)) + "_" + self.configdata.dataset_name + "_K_All" + "_Phase_" + str(self.phase) + "_stats_CP_3.txt"


        if self.phase == 2:
            #Calculate total average measures
            self.eval_calculate_total_avg_measures()

            #Print the core periphery relationships
            self.eval_print_summary_stats_CP(filename)

            #Print the global_core_periphery relationships
            self.eval_print_summary_stats_CP_1(filename_1)

            #Print the global core periphery relationships in a table format
            self.eval_print_summary_stats_CP_2(filename_2)

            #Print statistics for core periphery relationships
            self.eval_print_coreperiphery_summary_format(filename_3)


    def eval_calculate_total_avg_measures(self):
        self.configdata.logger.debug("Debugging from inside method eval_calculate_total_avg_evol_rate"
                                     "of class EvaluationData_Clusterone_CP.")
        num_core_evol_rate = 0
        num_periphery_evol_rate = 0
        num_core_periphery_evol_rate = 0

        sum_core_evol_rate = 0
        sum_periphery_evol_rate = 0
        sum_core_periphery_evol_rate = 0

        num_core_essentiality = 0
        num_periphery_essentiality = 0
        num_core_periphery_essentiality = 0

        sum_core_essentiality = 0
        sum_periphery_essentiality = 0
        sum_core_periphery_essentiality = 0

        num_core_phyletic_age = 0
        num_periphery_phyletic_age = 0
        num_core_periphery_phyletic_age = 0

        sum_core_phyletic_age = 0
        sum_periphery_phyletic_age = 0
        sum_core_periphery_phyletic_age = 0


        sum_core_mean = 0
        sum_core_standard_deviation = 0
        sum_core_struct_density = 0

        sum_periphery_mean = 0
        sum_periphery_standard_deviation = 0
        sum_periphery_struct_density = 0

        sum_core_periphery_mean = 0
        sum_core_periphery_standard_deviation = 0
        sum_core_periphery_struct_density = 0

        for cnode_id, cnode_data_i in self.cnodes_dict.items():
            if cnode_data_i.active == True and len(cnode_data_i.node_set) >=3:
                if cnode_data_i.cnode_CP_status == ClusterStatus.core:
                    self.core_num = self.core_num + 1
                    sum_core_mean = sum_core_mean + cnode_data_i.mean_edges
                    sum_core_standard_deviation = sum_core_standard_deviation + cnode_data_i.standard_deviation_edges
                    sum_core_struct_density = sum_core_struct_density + cnode_data_i.struct_density
                    print("Cnode mean:")
                    print(str(cnode_data_i.mean_edges))
                    print("Cnode struct density:")
                    print(str(cnode_data_i.struct_density))

                    if cnode_data_i.avg_evol_rate != -1:
                        num_core_evol_rate = num_core_evol_rate +1
                        sum_core_evol_rate = sum_core_evol_rate + cnode_data_i.avg_evol_rate
                    if cnode_data_i.perc_essential_genes != -1:
                        num_core_essentiality = num_core_essentiality +1
                        sum_core_essentiality= sum_core_essentiality + cnode_data_i.perc_essential_genes
                    if cnode_data_i.avg_phyletic_age != -1:
                        num_core_phyletic_age = num_core_phyletic_age +1
                        sum_core_phyletic_age = sum_core_phyletic_age + cnode_data_i.avg_phyletic_age


                elif cnode_data_i.cnode_CP_status == ClusterStatus.periphery:
                    self.periphery_num = self.periphery_num + 1
                    sum_periphery_mean = sum_periphery_mean + cnode_data_i.mean_edges
                    sum_periphery_standard_deviation = sum_periphery_standard_deviation + cnode_data_i.standard_deviation_edges
                    sum_periphery_struct_density = sum_periphery_struct_density + cnode_data_i.struct_density

                    if cnode_data_i.avg_evol_rate != -1:
                        num_periphery_evol_rate = num_periphery_evol_rate + 1
                        sum_periphery_evol_rate = sum_periphery_evol_rate + cnode_data_i.avg_evol_rate
                    if cnode_data_i.perc_essential_genes != -1:
                        num_periphery_essentiality = num_periphery_essentiality +1
                        sum_periphery_essentiality= sum_periphery_essentiality + cnode_data_i.perc_essential_genes
                    if cnode_data_i.avg_phyletic_age != -1:
                        num_periphery_phyletic_age = num_periphery_phyletic_age +1
                        sum_periphery_phyletic_age = sum_periphery_phyletic_age + cnode_data_i.avg_phyletic_age


                elif cnode_data_i.cnode_CP_status == ClusterStatus.coreandperiphery:
                    self.coreperiphery_num = self.coreperiphery_num + 1
                    sum_core_periphery_mean = sum_core_periphery_mean + cnode_data_i.mean_edges
                    sum_core_periphery_standard_deviation = sum_core_periphery_standard_deviation + cnode_data_i.standard_deviation_edges
                    sum_core_periphery_struct_density = sum_core_periphery_struct_density + cnode_data_i.struct_density

                    if cnode_data_i.avg_evol_rate != -1:
                        num_core_periphery_evol_rate = num_core_periphery_evol_rate + 1
                        sum_core_periphery_evol_rate = sum_core_periphery_evol_rate + cnode_data_i.avg_evol_rate
                    if cnode_data_i.perc_essential_genes != -1:
                        num_core_periphery_essentiality = num_core_periphery_essentiality +1
                        sum_core_periphery_essentiality= sum_core_periphery_essentiality + cnode_data_i.perc_essential_genes
                    if cnode_data_i.avg_phyletic_age != -1:
                        num_core_periphery_phyletic_age = num_core_periphery_phyletic_age +1
                        sum_core_periphery_phyletic_age = sum_core_periphery_phyletic_age + cnode_data_i.avg_phyletic_age


        self.core_avg_evol_rate = self.calculate_cnode_avg_measure(sum_core_evol_rate, num_core_evol_rate)
        self.periphery_avg_evol_rate = self.calculate_cnode_avg_measure(sum_periphery_evol_rate, num_periphery_evol_rate)
        self.coreperiphery_avg_evol_rate = self.calculate_cnode_avg_measure(sum_core_periphery_evol_rate, num_core_periphery_evol_rate)

        self.core_perc_essential_genes = self.calculate_cnode_avg_measure(sum_core_essentiality, num_core_essentiality)
        self.periphery_perc_essential_genes = self.calculate_cnode_avg_measure(sum_periphery_essentiality, num_periphery_essentiality)
        self.coreperiphery_perc_essential_genes = self.calculate_cnode_avg_measure(sum_core_periphery_essentiality, num_core_periphery_essentiality)

        self.core_avg_phyletic_age = self.calculate_cnode_avg_measure(sum_core_phyletic_age, num_core_phyletic_age)
        self.periphery_avg_phyletic_age = self.calculate_cnode_avg_measure(sum_periphery_phyletic_age, num_periphery_phyletic_age)
        self.coreperiphery_avg_phyletic_age = self.calculate_cnode_avg_measure(sum_core_periphery_phyletic_age, num_core_periphery_phyletic_age)

        self.core_avg_mean = self.calculate_cnode_avg_measure(sum_core_mean, self.core_num)
        self.periphery_avg_mean = self.calculate_cnode_avg_measure(sum_periphery_mean, self.periphery_num)
        self.coreperiphery_avg_mean = self.calculate_cnode_avg_measure(sum_core_periphery_mean, self.coreperiphery_num)

        self.core_avg_standard_deviation = self.calculate_cnode_avg_measure(sum_core_standard_deviation, self.core_num)
        self.periphery_avg_standard_deviation = self.calculate_cnode_avg_measure(sum_periphery_standard_deviation, self.periphery_num)
        self.coreperiphery_avg_standard_deviation = self.calculate_cnode_avg_measure(sum_core_periphery_standard_deviation, self.coreperiphery_num)

        self.core_avg_struct_density = self.calculate_cnode_avg_measure(sum_core_struct_density, self.core_num)
        self.periphery_avg_struct_density = self.calculate_cnode_avg_measure(sum_periphery_struct_density, self.periphery_num)
        self.coreperiphery_avg_struct_density = self.calculate_cnode_avg_measure(sum_core_periphery_struct_density, self.coreperiphery_num)




    #This method prints summary measures calculated for the cludters, along with a list of clusters
    def eval_print_summary_stats(self, filename):

        self.configdata.logger.debug("Debugging from inside eval_print_summary_stats method of class EvaluationData_WI")

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
        target.write("mean_diff:")
        target.write(str(self.mean_diff))
        target.write("\n")
        target.write("node_penalty:")
        target.write(str(self.node_penalty))
        target.write("\n")
        target.write("overlap_threshold:")
        target.write(str(self.overlap_threshold))
        target.write("\n")
        target.write("Phase of clustering:")
        target.write(str(self.phase))
        target.write("\n")
        target.write("Number Clusters:")
        target.write(str(self.num_clusters))
        target.write("\n")
        target.write("Number of clusters of size greater than =3:")
        target.write(str(self.num_clusters_size_3_or_more))
        target.write("\n")
        target.write("Number of clusters of size greater than =2:")
        target.write(str(self.num_clusters_size_2_or_more))
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

        self.configdata.logger.debug("Debugging from inside eval_print_clusters_summary_format method of class EvaluationData_WI.")

        target = open(filename, 'a')

        for cnode_id, cnode_data in self.cnodes_dict.items():
            if cnode_data.active == True:
                target.write("Cluster no.:")
                target.write(str(cnode_id))
                target.write(":\n")

                #print the cnode
                target.write("CLUSTER NODESET:\n")
                self.print_nodeset(cnode_id, target)

                #target.write("CLUSTER MERGE TREE:\n")
                #print the merging tree of the cnode
                #self.print_cnode_tree(cnode_id, target)

                target.write("BOUNDARY NODESET A low (Ycohesion, Nsd, High:\n")
                self.print_boundary_dict(cnode_data.boundary_cnode_dict_ycohesion_nsd_low, target)

                target.write("BOUNDARY NODESET A high (Ycohesion, Nsd, High:\n")
                self.print_boundary_dict(cnode_data.boundary_cnode_dict_ycohesion_nsd_high, target)

                target.write("BOUNDARY NODESET B (Ncohesion, Ysd):\n")
                self.print_boundary_dict(cnode_data.boundary_cnode_dict_ncohesion_ysd, target)

                target.write("BOUNDARY NODESET C (NCohesion, Nsd, low):\n")
                self.print_boundary_dict(cnode_data.boundary_cnode_dict_ncohesion_nsd_low, target)

                target.write("BOUNDARY NODESET D (NCohesion, Nsd, high):\n")
                self.print_boundary_dict(cnode_data.boundary_cnode_dict_ncohesion_nsd_high, target)


        target.write("\n")
        target.write("\n")

        target.close()

    # #Print overlapping nodeset belonging to a cnode to a file
    # def print_overlapping_nodeset(self, cnode_id, target):
    #     cnode_data = self.cnodes_dict[cnode_id]
    #     for node_cnode_i, overlapping_score in cnode_data.overlapping_node_dict.items():
    #         target.write(str(self.graphdata.node_dict[node_cnode_i].node_code))
    #         target.write(",")
    #     target.write("\n")

    #Method to print boundary nodes for a cnode.
    def print_boundary_dict(self, boundary_dict, target):
        self.configdata.logger.debug("Debugging from inside print_boundary_dict method of class EvaluationData_WI.")
        for node_id, periphery_score in boundary_dict.items():
            target.write(str(self.graphdata.node_dict[node_id].node_code))
            target.write(":")
            target.write(str(periphery_score))
            target.write(",")
        target.write("\n")


    def eval_print_summary_stats_CP(self, filename):
        self.configdata.logger.debug("Debugging from inside eval_print_summary_stats_CP method of class EvaluationData_WI.")
        target = open(filename, 'a')

        for cnode_id, cnode_data in self.cnodes_dict.items():
            if cnode_data.active == True:
                target.write("Cluster no.:")
                target.write(str(cnode_id))
                #print(str(cnode_id))
                target.write(":\n")

                #print the cnode
                target.write("CLUSTER NODESET:\n")
                self.print_nodeset(cnode_id, target)

                target.write("NO. OF PERIPHERY CLUSTERS:\n")
                #print("NO. of periphery clusters")
                target.write(str(len(cnode_data.periphery_cnode_dict.keys())))
                #print(str(len(cnode_data.periphery_cnode_dict.keys())))
                target.write("\n")
                self.print_periphery_cnodes(cnode_data, target)
                target.write("\n")


    #Method to print periphery cnodes for a cnode.
    def print_periphery_cnodes(self, cnode_data, target):
        self.configdata.logger.debug("Debugging from inside print_periphery_cnodes method of class EvaluationData_WI.")

        for periphery_cnode_id, cnode_relationship_score in cnode_data.periphery_cnode_dict.items():
            target.write("Periphery cluster no:")
            target.write(str(periphery_cnode_id))
            target.write(":\n")
            target.write("PERIPHERY NODESET:")
            self.print_nodeset(periphery_cnode_id, target)
            #target.write("\n")
            self.print_periphery_scores(cnode_relationship_score, target)

    #Method to print periphery scores
    def print_periphery_scores(self, cnode_relationship_score, target):
        self.configdata.logger.debug("Debugging from inside print_periphery_scores method of class EvaluationData_WI.")

        target.write("TypeA score:")
        target.write(str(cnode_relationship_score.typeA_score))
        target.write("\n")
        target.write("TypeB score:")
        target.write(str(cnode_relationship_score.typeB_score))
        target.write("\n")
        target.write("TypeC score:")
        target.write(str(cnode_relationship_score.typeC_score))
        target.write("\n")
        target.write("TypeD score:")
        target.write(str(cnode_relationship_score.typeD_score))
        target.write("\n")
        target.write("TypeE score:")
        target.write(str(cnode_relationship_score.typeE_score))
        target.write("\n")
        target.write("TypeF score:")
        target.write(str(cnode_relationship_score.typeF_score))
        target.write("\n")

    #This method prints the core periphery into the summary file.
    def eval_print_coreperiphery_summary_format(self, filename):

        self.configdata.logger.debug("Debugging from inside eval_print_clusters_summary_format method of class EvaluationData_Clusterone_CP.")

        target = open(filename, 'a')
        target.write("CPStatus\tcnode_id\tcluster nodes\tcnode_size\tcnode_mean\tcnode_standdev\tcnode_structdens\tcnode_essentiality\n")
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
                target.write("\t")
                target.write(str(cnode_data.perc_essential_genes))
                target.write("\n")

        target.close()


    def eval_print_summary_stats_CP_1(self, filename):
        self.configdata.logger.debug("Debugging from inside eval_print_summary_stats_CP_1 method of class EvaluationData_WI.")
        target = open(filename, 'a')

        target.write("Num Core clusters (size >= 3):")
        target.write("\n")
        target.write(str(self.core_num))
        target.write("\n")
        target.write("Num Periphery clusters (size >= 3):")
        target.write("\n")
        target.write(str(self.periphery_num))
        target.write("\n")
        target.write("Num CorePeriphery clusters (size >= 3):")
        target.write("\n")
        target.write(str(self.coreperiphery_num))
        target.write("\n")
        target.write("Avg core mean:")
        target.write("\n")
        target.write(str(self.core_avg_mean))
        target.write("\n")
        target.write("Avg periphery mean:")
        target.write("\n")
        target.write(str(self.periphery_avg_mean))
        target.write("\n")
        target.write("Avg coreperiphery avg mean")
        target.write("\n")
        target.write(str(self.coreperiphery_avg_mean))
        target.write("\n")
        target.write("Avg core standard deviation:")
        target.write("\n")
        target.write(str(self.core_avg_standard_deviation))
        target.write("\n")
        target.write("Avg periphery standard deviation:")
        target.write("\n")
        target.write(str(self.periphery_avg_standard_deviation))
        target.write("\n")
        target.write("Avg coreperiphery standard deviation:")
        target.write("\n")
        target.write(str(self.coreperiphery_avg_standard_deviation))
        target.write("\n")
        target.write("Avg core structural density:")
        target.write("\n")
        target.write(str(self.core_avg_struct_density))
        target.write("\n")
        target.write("Avg periphery structural density:")
        target.write("\n")
        target.write(str(self.periphery_avg_struct_density))
        target.write("\n")
        target.write("Avg coreperiphery structural density")
        target.write("\n")
        target.write(str(self.coreperiphery_avg_struct_density))
        target.write("\n")
        target.write("Avg core evol rate:")
        target.write("\n")
        target.write(str(self.core_avg_evol_rate))
        target.write("\n")
        target.write("Avg periphery evol rate:")
        target.write("\n")
        target.write(str(self.periphery_avg_evol_rate))
        target.write("\n")
        target.write("Avg coreperiphery evol rate:")
        target.write("\n")
        target.write(str(self.coreperiphery_avg_evol_rate))
        target.write("\n")
        target.write("Avg core essentiality:")
        target.write("\n")
        target.write(str(self.core_perc_essential_genes))
        target.write("\n")
        target.write("Avg periphery essentiality:")
        target.write("\n")
        target.write(str(self.periphery_perc_essential_genes))
        target.write("\n")
        target.write("Avg coreperiphery essentiality:")
        target.write("\n")
        target.write(str(self.coreperiphery_perc_essential_genes))
        target.write("\n")
        target.write("Avg core phyletic age:")
        target.write("\n")
        target.write(str(self.core_avg_phyletic_age))
        target.write("\n")
        target.write("Avg periphery phyletic age:")
        target.write("\n")
        target.write(str(self.periphery_avg_phyletic_age))
        target.write("\n")
        target.write("Avg coreperiphery phyletic age")
        target.write("\n")
        target.write(str(self.coreperiphery_avg_phyletic_age))
        target.write("\n")

        for (cnode_id_1, cnode2_id_2), cnode_relationship in self.cnode_relationship_dict.cnode_relationship_dict.items():
            target.write("Relationship Type:")
            target.write(str(cnode_relationship.relationship_type))
            target.write("\n")
            target.write("CNODEID_1:")
            target.write(str(cnode_relationship.cnode1_id))
            target.write("\n")
            self.print_nodeset(cnode_relationship.cnode1_id, target)
            target.write("CNODEID_2:")
            target.write(str(cnode_relationship.cnode2_id))
            target.write("\n")
            self.print_nodeset(cnode_relationship.cnode2_id, target)
            target.write("Aggregate Relationship Type:")
            target.write(str(cnode_relationship.relationship_score.aggregate_type))
            target.write("\n")
            # target.write("Composite Relationship score:")
            # target.write(str(cnode_relationship.relationship_score.composite_score))
            # target.write("\n")
            # target.write("Reverse Composite Relationship_score: ")
            # target.write(str(cnode_relationship.relationship_score.reverse_composite_score))
            # target.write("\n")
            # target.write("Composite Relationship score 3:")
            # target.write(str(cnode_relationship.relationship_score.composite_score_3))
            # target.write("\n")
            target.write("Edge weight based Relationship score:")
            target.write(str(cnode_relationship.relationship_score.edge_weight_score))
            target.write("\n")
            target.write("Structure based Relationship score:")
            target.write(str(cnode_relationship.relationship_score.structure_score))
            target.write("\n")
            target.write("Structure based Relationship score 1:")
            target.write(str(cnode_relationship.relationship_score.structure_score_1))
            target.write("\n")

            self.print_periphery_scores(cnode_relationship.relationship_score, target)
            target.write("\n\n")

            #Calculate type1_avg_mean_difference, type2_avg_mean_difference
            #type1_avg_cohesion_difference
            #type2_avg_cohesion_difference
            #type1_avg_struct_density_difference
            #type2_avg_struct_density_difference

            if self.cnodes_dict[cnode_relationship.cnode1_id].num_nodes > 2 and self.cnodes_dict[cnode_relationship.cnode2_id].num_nodes > 2:

                mean_difference = abs(self.cnodes_dict[cnode_relationship.cnode1_id].mean_edges - self.cnodes_dict[cnode_relationship.cnode2_id].mean_edges)
                cohesion_difference = abs(self.cnodes_dict[cnode_relationship.cnode1_id].cohesion - self.cnodes_dict[cnode_relationship.cnode2_id].cohesion)
                cohesion_inc_dec = self.cnodes_dict[cnode_relationship.cnode1_id].get_prospective_cohesion_diff(self.cnodes_dict[cnode_relationship.cnode2_id])
                struct_density_difference = abs(self.cnodes_dict[cnode_relationship.cnode1_id].struct_density - self.cnodes_dict[cnode_relationship.cnode2_id].struct_density)

                if cnode_relationship.relationship_score.aggregate_type == 'B':
                    self.num_type1 = self.num_type1 + 1
                    self.avg_type1_mean_difference = self.avg_type1_mean_difference + mean_difference
                    self.avg_type1_cohesion_difference = self.avg_type1_cohesion_difference + cohesion_difference
                    self.avg_type1_cohesion_incdec = self.avg_type1_cohesion_incdec + cohesion_inc_dec
                    self.avg_type1_struct_density_difference = self.avg_type1_struct_density_difference + struct_density_difference


                elif cnode_relationship.relationship_score.aggregate_type == 'A' or cnode_relationship.relationship_score.aggregate_type == 'AF' or cnode_relationship.relationship_score.aggregate_type == 'C':

                    self.num_type2 = self.num_type2 + 1
                    self.avg_type2_mean_difference = self.avg_type2_mean_difference + mean_difference
                    self.avg_type2_cohesion_difference = self.avg_type2_cohesion_difference + cohesion_difference
                    self.avg_type2_cohesion_incdec = self.avg_type2_cohesion_incdec + cohesion_inc_dec
                    self.avg_type2_struct_density_difference = self.avg_type2_struct_density_difference + struct_density_difference

                elif cnode_relationship.relationship_score.aggregate_type == 'E':
                    self.num_type3 = self.num_type3 + 1
                    self.avg_type3_mean_difference = self.avg_type3_mean_difference + mean_difference
                    self.avg_type3_cohesion_incdec = self.avg_type3_cohesion_incdec + cohesion_inc_dec
                    self.avg_type3_cohesion_difference = self.avg_type3_cohesion_difference + cohesion_difference
                    self.avg_type3_struct_density_difference = self.avg_type3_struct_density_difference + struct_density_difference

        if self.num_type1 >=1:
            self.avg_type1_mean_difference = float(self.avg_type1_mean_difference)/float(self.num_type1)
            self.avg_type1_cohesion_difference = float(self.avg_type1_cohesion_difference)/ float(self.num_type1)
            self.avg_type1_cohesion_incdec = float(self.avg_type1_cohesion_incdec)/ float(self.num_type1)
            self.avg_type1_struct_density_difference = float(self.avg_type1_struct_density_difference)/ float(self.num_type1)

        if self.num_type2 >=1:
            self.avg_type2_mean_difference = float(self.avg_type2_mean_difference)/float(self.num_type2)
            self.avg_type2_cohesion_difference = float(self.avg_type2_cohesion_difference)/ float(self.num_type2)
            self.avg_type2_cohesion_incdec = float(self.avg_type2_cohesion_incdec)/ float(self.num_type2)
            self.avg_type2_struct_density_difference = float(self.avg_type2_struct_density_difference)/ float(self.num_type2)

        if self.num_type3 >=1:
            self.avg_type3_mean_difference = float(self.avg_type3_mean_difference)/float(self.num_type3)
            self.avg_type3_cohesion_difference = float(self.avg_type3_cohesion_difference)/ float(self.num_type3)
            self.avg_type3_cohesion_incdec = float(self.avg_type3_cohesion_incdec)/ float(self.num_type3)
            self.avg_type3_struct_density_difference = float(self.avg_type3_struct_density_difference)/ float(self.num_type3)




    def eval_print_summary_stats_CP_2(self, filename):
        self.configdata.logger.debug("Debugging from inside eval_print_summary_stats_CP_1 method of class EvaluationData_Clusterone_CP.")
        target = open(filename, 'a')

        target.write("Relationship Type\tCNODEID_1\tCNODE1_TYPE\tCNODE_1_NODESET\tRECALL\tPRECISION\tFMEASURE\tMATCHING COMPLEX ID\tMATCHING COMPLEX NAME\tCNODEID_2\tCNODE2_TYPE\tCNODE_2_NODESET\tRECALL\tPRECISION\tFMEASURE\tMATCHING COMPLEX ID\tMATCHING COMPLEX NAME\tEDGE WEIGHT SCORE\tSTRUCTURE SCORE\tPERIPHERY TYPE\n")

        for (cnode1_id, cnode2_id), cnode_relationship in self.cnode_relationship_dict.cnode_relationship_dict.items():
            #if self.cnodes_dict[cnode_relationship.cnode1_id].num_nodes > 2 and self.cnodes_dict[cnode_relationship.cnode2_id].num_nodes > 2:

                target.write(str(cnode_relationship.relationship_type))
                target.write("\t")
                target.write(str(cnode_relationship.cnode1_id))
                target.write("\t")
                target.write(str(self.cnodes_dict[cnode_relationship.cnode1_id].cnode_CP_status))
                target.write("\t")
                self.print_nodeset(cnode_relationship.cnode1_id, target)
                target.write("\t")
                self.print_f_measure_scores(target, cnode_relationship.cnode1_id)
                target.write("\t")

                target.write(str(cnode_relationship.cnode2_id))
                target.write("\t")
                target.write(str(self.cnodes_dict[cnode_relationship.cnode2_id].cnode_CP_status))
                target.write("\t")
                self.print_nodeset(cnode_relationship.cnode2_id, target)
                target.write("\t")
                self.print_f_measure_scores(target, cnode_relationship.cnode2_id)

                target.write("\t")

                target.write(str(cnode_relationship.relationship_score.edge_weight_score))
                target.write("\t")
                target.write(str(cnode_relationship.relationship_score.structure_score_1))
                target.write("\t")
                target.write(str(cnode_relationship.relationship_score.aggregate_type))
                #target.write("\t")

                # mean_difference = abs(self.cnodes_dict[cnode_relationship.cnode1_id].mean_edges - self.cnodes_dict[cnode_relationship.cnode2_id].mean_edges)
                # target.write(str(mean_difference))
                # target.write("\t")
                #
                # cohesion_difference = abs(self.cnodes_dict[cnode_relationship.cnode1_id].cohesion - self.cnodes_dict[cnode_relationship.cnode2_id].cohesion)
                # target.write(str(cohesion_difference))
                # target.write("\t")
                #
                # struct_density_difference = abs(self.cnodes_dict[cnode_relationship.cnode1_id].struct_density - self.cnodes_dict[cnode_relationship.cnode2_id].struct_density)
                # target.write(str(struct_density_difference))

                target.write("\n")

        target.write("Number of type 1 relations:")
        target.write("\n")
        target.write(str(self.num_type1))
        target.write("\n")
        target.write("Average mean difference of type 1 relations:")
        target.write("\n")
        target.write(str(self.avg_type1_mean_difference))
        target.write("\n")
        target.write("Average cohesion difference of type 1 peripheries:")
        target.write("\n")
        target.write(str(self.avg_type1_cohesion_difference))
        target.write("\n")
        target.write("Average cohesion increase/decrease of type 1 peripheries:")
        target.write("\n")
        target.write(str(self.avg_type1_cohesion_incdec))
        target.write("\n")

        target.write("Average structural density difference of type 1 peripheries:")
        target.write("\n")
        target.write(str(self.avg_type1_struct_density_difference))
        target.write("\n")
        target.write("\n")

        target.write("Number of type 2 relations:")
        target.write("\n")
        target.write(str(self.num_type2))
        target.write("\n")
        target.write("Average mean difference of type 2 relations:")
        target.write("\n")
        target.write(str(self.avg_type2_mean_difference))
        target.write("\n")
        target.write("Average cohesion difference of type 2 peripheries:")
        target.write("\n")
        target.write(str(self.avg_type2_cohesion_difference))
        target.write("\n")
        target.write("Average cohesion increase/decrease of type 2 peripheries:")
        target.write("\n")
        target.write(str(self.avg_type2_cohesion_incdec))
        target.write("\n")

        target.write("Average structural density difference of type 2 peripheries:")
        target.write("\n")
        target.write(str(self.avg_type2_struct_density_difference))
        target.write("\n")
        target.write("\n")

        target.write("Number of type 3 relations:")
        target.write("\n")
        target.write(str(self.num_type3))
        target.write("\n")
        target.write("Average mean difference of type 3 relations:")
        target.write("\n")
        target.write(str(self.avg_type3_mean_difference))
        target.write("\n")
        target.write("Average cohesion difference of type 3 peripheries:")
        target.write("\n")
        target.write(str(self.avg_type3_cohesion_difference))
        target.write("\n")

        target.write("Average cohesion increase/decrease of type 3 peripheries:")
        target.write("\n")
        target.write(str(self.avg_type3_cohesion_incdec))
        target.write("\n")

        target.write("Average structural density difference of type 3 peripheries:")
        target.write("\n")
        target.write(str(self.avg_type3_struct_density_difference))
        target.write("\n")
        target.write("\n")



    def print_f_measure_scores(self, target, cnode_id):
        if cnode_id in self.f_measure_dict:
            target.write(str(self.f_measure_dict[cnode_id]['recall']))
            target.write("\t")
            target.write(str(self.f_measure_dict[cnode_id]['precision']))
            target.write("\t")
            target.write(str(self.f_measure_dict[cnode_id]['f_measure']))
            target.write("\t")
            target.write(str(self.f_measure_dict[cnode_id]['best_matching_complex_id']))
            target.write("\t")
            target.write(str(self.f_measure_dict[cnode_id]['best_matching_complex_name']))
        else:
            target.write("NA")
            target.write("\t")
            target.write("NA")
            target.write("\t")
            target.write("NA")
            target.write("\t")
            target.write("NA")
            target.write("\t")
            target.write("NA")
