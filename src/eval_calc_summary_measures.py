__author__ = 'divya'

import logging

from .eval_calc_measures import eval_calc_measures


def eval_calc_summary_measures(CL_List, SM, SM_orig, num_clusters, num_nodes, log):
    #logger = log.get_logger(__name__)
    logger = logging.getLogger('root')
    logger.debug("Debugging from inside eval_calc_summary_ module")


    (Mean_List, Variance_List, Struct_Density_List, Node_Count_List) = eval_calc_measures(CL_List, SM, SM_orig, num_clusters, num_nodes, log)

    return (Mean_List, Variance_List, Struct_Density_List, Node_Count_List)
