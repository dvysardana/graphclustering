__author__ = 'divya'

import logging

def eval_calc_average_measures(Mean_List, Variance_List,  Struct_Density_List, Node_Count_List,log):
    average_Mean = 0.0
    average_Variance = 0.0
    average_Standard_Deviation = 0.0
    average_Struct_Density = 0.0
    min_cluster_size = 0.0
    max_cluster_size = 0.0

    numerator_mean = 0
    numerator_variance = 0
    numerator_struct_density = 0
    numerator_standard_deviation = 0
    num_clusters_size_3_or_more = 0
    num_clusters = len(Mean_List)

    #logger = log.get_logger(__name__)
    logger = logging.getLogger('root')
    logger.debug("Debugging from inside eval_calc_average_measures")


    for i in range(0, num_clusters):
        if(Node_Count_List[i] > 2):
            num_clusters_size_3_or_more = num_clusters_size_3_or_more + 1
            numerator_mean = numerator_mean + Mean_List[i]
            numerator_variance = numerator_variance + Variance_List[i]
            numerator_standard_deviation = numerator_standard_deviation + Variance_List[i]**0.5
            numerator_struct_density = numerator_struct_density + Struct_Density_List[i]

    if num_clusters_size_3_or_more != 0:
        average_Mean = (float) (numerator_mean)/ (float) (num_clusters_size_3_or_more)
        average_Variance = (float) (numerator_variance)/ (float) (num_clusters_size_3_or_more)
        average_Standard_Deviation = (float) (numerator_standard_deviation)/ (float) (num_clusters_size_3_or_more)
        average_Struct_Density = (float) (numerator_struct_density)/ (float) (num_clusters_size_3_or_more)
    else:
        average_Mean = 0
        average_Variance = 0
        average_Standard_Deviation = 0
        average_Struct_Density = 0

    min_cluster_size = min(Node_Count_List)
    max_cluster_size = max(Node_Count_List)

    #Write all average measures to a file


    return(num_clusters_size_3_or_more, average_Mean, average_Variance, average_Standard_Deviation, average_Struct_Density, min_cluster_size, max_cluster_size)