__author__ = 'divya'

import logging

#This function prints summary measures calculated for the cludters, along with a list of clusters
def eval_print_summary_stats(num_clusters, num_clusters_size_3_or_more, average_Mean, average_Variance, average_Struct_Density, min_cluster_size, max_cluster_size, K, Phase, filename, log):

    #logger = log.get_logger(__name__)
    logger = logging.getLogger('root')
    logger.debug("Debugging from inside eval_print_summary_stats module")


    target = open(filename, 'a')

    target.write("Clustering Statistics:")
    target.write("\n")
    target.write("K:")
    target.write(str(K))
    target.write("\n")
    target.write("Phase of clustering:")
    target.write(str(Phase))
    target.write("\n")
    target.write("Number Clusters:")
    target.write(str(num_clusters))
    target.write("\n")
    target.write("Number of clusters of size greater than 2:")
    target.write(str(num_clusters_size_3_or_more))
    target.write("\n")
    target.write("Average Mean:")
    target.write(str(average_Mean))
    target.write("\n")
    target.write("Average Variance:")
    target.write(str(average_Variance))
    target.write("\n")
    target.write("Average Structural Density:")
    target.write(str(average_Struct_Density))
    target.write("\n")
    target.write("Minimum cluster size:")
    target.write(str(min_cluster_size))
    target.write("\n")
    target.write("Maximum cluster size:")
    target.write(str(max_cluster_size))
    target.write("\n")
    target.write("\n")

    target.close()
