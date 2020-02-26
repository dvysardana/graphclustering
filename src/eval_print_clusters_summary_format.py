__author__ = 'divya'

import logging

#This function prints the clusters into the summary file.
#The format used in this function is different than the format used in the printClusters function.
def eval_print_clusters_summary_format(SM, CL_List, CL_List_unique, node_codes, num_clusters, num_nodes, filename, log):

    #logger = log.get_logger(__name__)
    logger = logging.getLogger('root')
    logger.debug("Debugging from inside eval_print_clusters_summary_format module")


    target = open(filename, 'a')

    for i in CL_List_unique:
        #Get nodes belonging to cluster Ci
        nodes_Ci = [x for x in range(0, num_nodes) if CL_List[x] == i]

        target.write("Cluster no.: ")
        target.write(str(i))

        for node_Ci in nodes_Ci:
            target.write(str(node_codes[node_Ci]))
            target.write(",")

        target.write("\n")


    target.write("\n")
    target.write("\n")

    target.close()