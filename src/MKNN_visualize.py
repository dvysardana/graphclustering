__author__ = 'divya'

from .helper_printObjects import printList
from .visualizeClusters_2 import visualizeClusters_2
from .visualize_specific_clusters import visualize_specific_clusters
from .printClusters import printClusters
from .visualizeClusters import visualizeClusters

def MKNN_visualize(CL_List, num_clusters, SM, SM_orig, num_nodes, node_codes, K, currentdate_str, dataset_name, eval_results_dir, phase, log):


    printList(CL_List)
    visualizeClusters(SM, CL_List, node_codes, num_clusters, K, phase, currentdate_str, dataset_name, eval_results_dir, log)

    visualizeClusters_2(SM_orig, CL_List, node_codes, num_clusters, K, phase, currentdate_str, dataset_name, eval_results_dir, log)

    #visualize only specific clusters
    visualize_specific_clusters(SM_orig, CL_List, [28, 30], node_codes, num_clusters, K, phase, currentdate_str, dataset_name, eval_results_dir, log)

    printClusters(SM, CL_List, node_codes, num_clusters, num_nodes, K, phase, currentdate_str, dataset_name, eval_results_dir, log)
