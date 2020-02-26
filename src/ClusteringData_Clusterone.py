__author__ = 'divya'


from ClusteringData import ClusteringData

#Class to hold the data on which the clustering algorithm acts
class ClusteringData_Clusterone(ClusteringData):
    #(CL_List_P2, CL_List_P1, SM, SM_orig, num_clusters_P2, num_clusters_P1, num_nodes)
    def __init__(self, graphdata, configdata, cnodes_dict, next_cluster_label):
        K = -1
        num_clusters = -1
        super(ClusteringData_Clusterone, self).__init__(graphdata, configdata, K, cnodes_dict, next_cluster_label, num_clusters)


