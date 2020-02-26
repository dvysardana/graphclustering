__author__ = 'divya'


import logging

def printClusters(SM, CL_List, node_codes, num_clusters, num_nodes, K, Phase, currentdate_str, dataset_name, eval_results_dir, log):

    #logger = log.get_logger(__name__)
    logger = logging.getLogger('root')
    logger.debug("Debugging from inside printClusters module")

    #directoryname = "docs/" + currentdate.isoformat() + "GMKNN_K_" + str(K) + "_Phase_" + str(Phase);
    #Create a directory for the current timestamp
    #if not os.path.exists(directoryname):
    #    os.makedirs(directory)
    #currentdate = datetime.datetime.now()
    #currentdate = datetime.datetime.now()



    filename = eval_results_dir + "/docs/phase" + str(Phase)+ "/" + currentdate_str + "_GMKNN_" + dataset_name + "_K_" + str(K) + "_Phase_" + str(Phase) + "_print.txt"
    target = open(filename, 'w')

    for i in range(0, num_nodes):
        target.write(str(CL_List[i]))
        target.write("\t")
        target.write(str(i))
        target.write("\t")
        target.write(str(node_codes[i]))
        target.write("\n")

    target.close()