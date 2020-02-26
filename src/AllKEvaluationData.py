__author__ = 'divya'

import pylab as pl
import numpy as np

class AllKEvaluationData(object):
    def __init__(self, configdata, phase):
        self.list_all_K_evaluation_data = []
        self.configdata = configdata
        self.phase = phase

    def add_evaluation_for_K(self, evaluation_data):
        self.list_all_K_evaluation_data.append(evaluation_data)

    def plot_evaluation_measures_for_all_K(self):
        self.configdata.logger.debug("Debugging from inside plot_evaluation_measures_for_all_K method")


        figurename1 = self.configdata.eval_results_dir + "/plots/phase" + str(self.phase) + "/" + self.configdata.currentdate_str + "_GMKNN_" + self.configdata.dataset_name + "_K_All" + "_Phase_" + str(self.phase) + "_plot_1.png"
        figurename2 = self.configdata.eval_results_dir + "/plots/phase" + str(self.phase) + "/" + self.configdata.currentdate_str + "_GMKNN_" + self.configdata.dataset_name + "_K_All" + "_Phase_" + str(self.phase) + "_plot_2.png"
        figurename3 = self.configdata.eval_results_dir + "/plots/phase" + str(self.phase) + "/" + self.configdata.currentdate_str + "_GMKNN_" + self.configdata.dataset_name + "_K_All" + "_Phase_" + str(self.phase) + "_plot_3.png"


        K_list = [eval_data.K for eval_data in self.list_all_K_evaluation_data]
        num_clusters_list = [eval_data.num_clusters for eval_data in self.list_all_K_evaluation_data]
        num_clusters_size_3_or_more_list = [eval_data.num_clusters_size_3_or_more for eval_data in self.list_all_K_evaluation_data]
        average_mean_list = [eval_data.average_mean_clusters for eval_data in self.list_all_K_evaluation_data]
        average_standard_deviation_list = [eval_data.average_standard_deviation_clusters for eval_data in self.list_all_K_evaluation_data]
        average_structural_density_list = [eval_data.average_structural_density_clusters for eval_data in self.list_all_K_evaluation_data]
        min_cluster_size_list = [eval_data.min_cluster_size for eval_data in self.list_all_K_evaluation_data]
        max_cluster_size_list = [eval_data.max_cluster_size for eval_data in self.list_all_K_evaluation_data]

        # #Plot the variation of number of clusters with K
        # plot1 = pl.plot(K_List, num_clusters_List, 'r', label='Total number of clusters')
        # plot2 = pl.plot(K_List, num_clusters_size_3_or_more_List,'g', label='Total number of clusters (size >=3)')
        #
        # pl.title('Number of Clusters for different values of K')
        # pl.xlabel('K')
        # pl.ylabel('#clusters')
        #
        # pl.legend(loc='upper center', bbox_to_anchor=(0.5, -0.05), fancybox=True, shadow=True, ncol=5)
        # #pl.show()
        # pl.savefig(figurename1)
        # pl.close("all")


        # #Plot the variation of average measures with K
        # plot3 = pl.plot(K_List, average_Mean_List, 'r', label='Avg. Mean')
        # #plot4 = pl.plot(K_List, average_Variance_List, 'g', label='Average Variance of clusters')
        # plot4 = pl.plot(K_List, average_Standard_Deviation_List, 'g', label='Avg. Stand. Deviation')
        # plot5 = pl.plot(K_List, average_Struct_Density_List, 'b', label='Avg. Struct. Density')
        #
        # pl.title('Average Clustering Measures vs. K')
        # pl.xlabel('K')
        # pl.ylabel('Average measures')
        # pl.yticks(np.arange(0, max(average_Standard_Deviation_List)+1, 0.5))
        #
        # pl.legend(loc='upper center', bbox_to_anchor=(0.5, -0.05), fancybox=True, shadow=True, ncol=5)
        # pl.legend()
        # pl.savefig(figurename2)
        # pl.close("all")

        # #Plot the variation of min and max cluster size with K
        # plot6 = pl.plot(K_List, min_cluster_size_List, 'r', label='Minimum cluster size')
        # plot7 = pl.plot(K_List, max_cluster_size_List, 'g', label='Maximum cluster size')
        #
        # pl.title('Cluster size vs. K')
        # pl.xlabel('K')
        # pl.ylabel('Min and Max cluster size')
        #
        # pl.legend(loc='upper center', bbox_to_anchor=(0.5, -0.05), fancybox=True, shadow=True, ncol=5)
        # #pl.savefig(figurename3)
        # pl.close("all")

        #######################################

        #Plot the variation of number of clusters with K

        fig = pl.figure()
        ax = fig.add_subplot(111)
        ax.plot(K_list, num_clusters_list, 'r', label='Total no. of clusters')
        ax.plot(K_list, num_clusters_size_3_or_more_list, 'g', label='Total no. of clusters (size >=3)')

        #fig.savefig(figurename3, dpi=300, format='png')

        # Shrink current axis's height by 10% on the bottom
        box = ax.get_position()
        ax.set_position([box.x0, box.y0 + box.height * 0.1, box.width, box.height * 0.7])

        # Put a legend below current axis
        lgd = ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.15), fancybox=True, shadow=True, ncol=5, fontsize=12)
        #ax.legend()

        ax.set_title('Number of Clusters vs. K', fontsize=14)
        ax.set_xlabel('K', fontsize=12)
        ax.set_ylabel('Number of Clusters', fontsize=12)
        ax.set_yticks(np.arange(min(num_clusters_size_3_or_more_list), max(num_clusters_list)+2))


        fig.savefig(figurename1, dpi=300, format='png', bbox_extra_artists=(lgd,), bbox_inches='tight')
        pl.close("all")
        ##############################################


        #Plot the variation of average measures with K

        fig = pl.figure()
        ax = fig.add_subplot(111)
        ax.plot(K_list, average_mean_list, 'r', label='Average Mean')
        ax.plot(K_list, average_standard_deviation_list, 'g', label='Average Standard Deviation')
        ax.plot(K_list, average_structural_density_list, 'b', label='Average Structural Density')

        #fig.savefig(figurename3, dpi=300, format='png')

        # Shrink current axis's height by 10% on the bottom
        box = ax.get_position()
        ax.set_position([box.x0, box.y0 + box.height * 0.1, box.width, box.height * 0.7])

        # Put a legend below current axis
        lgd = ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.15), fancybox=True, shadow=True, ncol=5, fontsize=12)
        #ax.legend()

        ax.set_title('Average Clustering Measures vs. K', fontsize=14)
        ax.set_xlabel('K', fontsize=12)
        ax.set_ylabel('Average Measure', fontsize=12)
        ax.set_yticks(np.arange(0, max(average_standard_deviation_list)+1, 0.5))


        fig.savefig(figurename2, dpi=300, format='png', bbox_extra_artists=(lgd,), bbox_inches='tight')
        pl.close("all")
        ##############################################

        #Plot the variation of min and max cluster size with K
        fig = pl.figure()
        ax = fig.add_subplot(111)
        ax.plot(K_list, min_cluster_size_list, 'r', label='Minimum cluster size')
        ax.plot(K_list, max_cluster_size_list, 'g', label='Maximum cluster size')

        #fig.savefig(figurename3, dpi=300, format='png')

        # Shrink current axis's height by 10% on the bottom
        box = ax.get_position()
        ax.set_position([box.x0, box.y0 + box.height * 0.1, box.width, box.height * 0.7])

        # Put a legend below current axis
        lgd = ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.15), fancybox=True, shadow=True, ncol=5, fontsize=12)
        #ax.legend()

        ax.set_title('Cluster size vs. K', fontsize=14)
        ax.set_xlabel('K', fontsize=12)
        ax.set_ylabel('Min. and Max. cluster size', fontsize=12)

        fig.savefig(figurename3, dpi=300, format='png', bbox_extra_artists=(lgd,), bbox_inches='tight')
        pl.close("all")
