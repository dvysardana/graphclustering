__author__ = 'divya'

from AlgorithmName import AlgorithmName

class ClusteringPrinter(object):

    def __init__(self, configdata, graphdata, phase, K, CL_list,algorithm_name ):
        self.configdata = configdata
        self.graphdata = graphdata
        self.phase = phase
        self.K = K
        self.CL_list = CL_list
        self.algorithm_name = algorithm_name


    def printClusters(self):

        self.configdata.logger.debug("Debugging from inside printClusters method")

        a_name = AlgorithmName()
        filename = self.configdata.eval_results_dir + "/docs/phase" + str(self.phase)+ "/" + self.configdata.currentdate_str + "_" + str(a_name.get_algorithm_name(self.algorithm_name)) + "_" + self.configdata.dataset_name + "_K_" + str(self.K) + "_Phase_" + str(self.phase) + "_print.txt"
        target = open(filename, 'w')

        for i in range(0, self.graphdata.num_nodes):
            target.write(str(self.CL_list[i]))
            target.write("\t")
            target.write(str(i))
            target.write("\t")
            target.write(str(self.graphdata.node_dict[i].node_code))
            target.write("\n")

        target.close()

