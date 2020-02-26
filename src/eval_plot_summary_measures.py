__author__ = 'divya'

import numpy as np
import pylab as pl
import logging

def eval_plot_summary_measures(currentdate_str, dataset_name, phase, K_List, num_clusters_List, num_clusters_size_3_or_more_List, average_Mean_List, average_Standard_Deviation_List, average_Struct_Density_List, min_cluster_size_List, max_cluster_size_List, eval_results_dir, log):

    #logger = log.get_logger(__name__)
    logger = logging.getLogger('root')
    logger.debug("Debugging from inside eval_plot_summary_measures module")


    figurename1 = eval_results_dir + "/plots/phase" + str(phase) + "/" + currentdate_str + "_GMKNN_" + dataset_name + "_K_All" + "_Phase_" + str(phase) + "_plot_1.png"
    figurename2 = eval_results_dir + "/plots/phase" + str(phase) + "/" + currentdate_str + "_GMKNN_" + dataset_name + "_K_All" + "_Phase_" + str(phase) + "_plot_2.png"
    figurename3 = eval_results_dir + "/plots/phase" + str(phase) + "/" + currentdate_str + "_GMKNN_" + dataset_name + "_K_All" + "_Phase_" + str(phase) + "_plot_3.png"


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
    ax.plot(K_List, num_clusters_List, 'r', label='Total no. of clusters')
    ax.plot(K_List, num_clusters_size_3_or_more_List, 'g', label='Total no. of clusters (size >=3)')

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
    ax.set_yticks(np.arange(min(num_clusters_size_3_or_more_List), max(num_clusters_List)+2))


    fig.savefig(figurename1, dpi=300, format='png', bbox_extra_artists=(lgd,), bbox_inches='tight')
    pl.close("all")
    ##############################################


    #Plot the variation of average measures with K

    fig = pl.figure()
    ax = fig.add_subplot(111)
    ax.plot(K_List, average_Mean_List, 'r', label='Average Mean')
    ax.plot(K_List, average_Standard_Deviation_List, 'g', label='Average Standard Deviation')
    ax.plot(K_List, average_Struct_Density_List, 'b', label='Average Structural Density')

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
    ax.set_yticks(np.arange(0, max(average_Standard_Deviation_List)+1, 0.5))


    fig.savefig(figurename2, dpi=300, format='png', bbox_extra_artists=(lgd,), bbox_inches='tight')
    pl.close("all")
    ##############################################

    #Plot the variation of min and max cluster size with K
    fig = pl.figure()
    ax = fig.add_subplot(111)
    ax.plot(K_List, min_cluster_size_List, 'r', label='Minimum cluster size')
    ax.plot(K_List, max_cluster_size_List, 'g', label='Maximum cluster size')

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