__author__ = 'divya'

import numpy as np
import logging

from MKNN_Helper import MKNN_Helper
from NodeData import NodeData
from AlgorithmName import AlgorithmName


#Class to hold the data on which the clustering algorithm acts
class ClusteringData(object):
    #(CL_List_P2, CL_List_P1, SM, SM_orig, num_clusters_P2, num_clusters_P1, num_nodes)
    def __init__(self, graphdata, configdata, K, cnodes_dict, next_cluster_label, num_clusters):
        self.K = K
        self.graphdata = graphdata
        self.configdata = configdata
        self.cnodes_dict = cnodes_dict #Dictionary containing node_ids along with their objects
        #self.cluster_members_dict = {} #Dictionary containing node_ids belonging to
                                        # each cluster label

        self.next_cluster_label = next_cluster_label
        self.num_clusters = num_clusters
        self.helper = MKNN_Helper()

    #Function to initialize the cluster labels to all -1 before the clustering
    # begins
    def initialize_node_cluster_labels(self):
        for nodeid, nodedata in self.graphdata.node_dict.items():
            nodedata.GMKNN_clabel_dict = dict()

    #Function to generate cluster_label_list for evaluation purposes
    def generate_cluster_label_list(self, algorithm_name):
        num_active_cnodes = 0
        cluster_label_list = [-1]*self.graphdata.num_nodes
        for nodeid, nodedata in self.graphdata.node_dict.items():
            if(algorithm_name == AlgorithmName.GMKNN_ZhenHu):
                #cluster_label_list[nodeid] = list(nodedata.GMKNN_clabel_dict.keys())[0]
                active_cnode_list = [-1 if self.cnodes_dict[cnode_id].active == False else cnode_id for cnode_id in nodedata.GMKNN_clabel_dict.keys()]
                num_active_cnodes = sum(x > 0 for x in active_cnode_list)
                #cluster_label_list[nodeid] = -1
                if num_active_cnodes == 0:
                    cluster_label_list[nodeid] = -1 #Nodes with no cluster label
                elif num_active_cnodes > 1:
                    cluster_label_list[nodeid] = -2 #Nodes with more than one cluster label
                else:
                    cluster_label_list[nodeid] = max(active_cnode_list)

            elif algorithm_name == AlgorithmName.Clusterone:
                if len(nodedata.clusterone_clabel_dict) == 0:
                    cluster_label_list[nodeid] = -1 #Nodes with no cluster label
                elif len(nodedata.clusterone_clabel_dict) > 1:
                    cluster_label_list[nodeid] = -2 #Nodes with more than one cluster label
                else:
                    cluster_label_list[nodeid] = list(nodedata.clusterone_clabel_dict.keys())[0]

        if self.phase == 2:
            specific_set_to_draw = set()
            #specific_set_to_draw.add(1)
            # specific_set_to_draw.add(4)
            # specific_set_to_draw.add(3)
            # specific_set_to_draw.add(6)
            cluster_label_list = self.helper.edit_cluster_label_list(cluster_label_list, self.graphdata.node_dict, self.cnodes_dict, specific_set_to_draw, algorithm_name)
        #self.helper.print_list(cluster_label_list)
        return cluster_label_list

