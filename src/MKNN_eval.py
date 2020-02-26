__author__ = 'divya'

import logging

from .eval_calc_summary_measures import eval_calc_summary_measures
from .eval_calc_average_measures import eval_calc_average_measures
from .eval_print_summary_stats import eval_print_summary_stats
from .eval_print_clusters_summary_format import eval_print_clusters_summary_format

#This function performs different steps for evaluation after both phase 1 and phase 2
def MKNN_eval(CL_List, SM, SM_orig, num_clusters, num_nodes, node_codes, filename, K, phase, log):
    #fd

    #logger = log.get_logger(__name__)
    logger = logging.getLogger('root')
    logger.debug("Debugging from inside eval_engine module")

    CL_List_unique = list(set(CL_List))

    #Measures of individual clusters
    (Mean_List, Variance_List, Struct_Density_List, Node_Count_List) = eval_calc_summary_measures(CL_List, SM, SM_orig, num_clusters, num_nodes, log)

    #Average measures
    (num_clusters_size_3_or_more, average_Mean, average_Variance, average_Standard_Deviation,  average_Struct_Density, min_cluster_size, max_cluster_size) = eval_calc_average_measures(Mean_List, Variance_List, Struct_Density_List, Node_Count_List, log)

    #(num_clusters, num_clusters_size_3_or_more, average_Mean, average_Variance, average_Standard_Deviation, average_Struct_Density, min_cluster_size, max_cluster_size, phase, CL_List, CL_List_unique) = MKNN_worker(K, num_expand, LIMIT_CLUSTERS, SM, SM_orig, num_nodes, node_codes, currentdate)

    #Write the average measures to a file
    eval_print_summary_stats(num_clusters, num_clusters_size_3_or_more, average_Mean, average_Variance, average_Struct_Density, min_cluster_size, max_cluster_size, K, phase, filename, log)

    #Also print a summary list of all clusters formed.
    eval_print_clusters_summary_format(SM, CL_List, CL_List_unique, node_codes, num_clusters, num_nodes, filename, log)

    return (num_clusters_size_3_or_more, average_Mean, average_Variance, average_Standard_Deviation, average_Struct_Density, max_cluster_size, min_cluster_size)
