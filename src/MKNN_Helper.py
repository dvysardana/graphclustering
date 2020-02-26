__author__ = 'divya'

import math
from ConfigData import ConfigData
from AlgorithmName import AlgorithmName

class MKNN_Helper(object):
    CODE_DIR = '/Users/divya/work/repo/Dissertation'
    #CODE_DIR = '/Users/divya/Documents/Dissertation/Dissertation'
    DATA_DIR = '/Users/divya/Documents/input/Dissertation/data'
    LOG_DIR = '/Users/divya/Documents/logs/Dissertation'
    configdata = ConfigData(CODE_DIR, DATA_DIR, LOG_DIR)

    def __init__(self):
        MKNN_Helper.configdata.do_config()
    ###################################################
    #Helper function: Calculate the union of two lists
    #Used in MKNN_init
    ##################################################
    def union(self, a, b):
        """ return the union of two lists """
        return list(set(a) | set(b))

    def print_list(self, list_1):
        for i in list_1:
            print(i)
            print(",")

    def print_set(self, set_1):
        for i in set_1:
            print(i)
            print(",")

    def print_dict(self, dict_1):
        for (key, value) in dict_1.items():
            print("%s: %s" % (key, value))

    def convert_list_ids_to_codes(self, graphdata, list_1):
        codes_list = [graphdata.node_dict[i].node_code for i in list_1]
        print(codes_list)

    def print_set_codes(self, set_1, node_dict):
        for i in set_1:
            print(node_dict[i].node_code)
            print(",")

    def print_list_codes(self, list_1, node_dict):
        for i in list_1:
            if i != -1:
                print(node_dict[i].node_code)
            else:
                print("-1")
            print(",")

    def print_clusters(self, clusters_list, cnodes_dict):
        nodeset = set()
        for cluster_id in clusters_list:
            cnode_data = cnodes_dict[cluster_id]
            nodeset = cnode_data.node_set

    def edit_cluster_label_list(self, cluster_label_list, node_dict, cnodes_dict, specific_set_to_draw, algorithm_name):
        for cluster_id in specific_set_to_draw:
            set_temp = set()
            set_temp.add(cluster_id)
            cnode_data = cnodes_dict[cluster_id]
            nodeset = cnode_data.node_set
            for node_id in nodeset:
                if algorithm_name == AlgorithmName.Clusterone:
                    if len(set(node_dict[node_id].clusterone_clabel_dict.keys()).intersection(specific_set_to_draw.difference(set_temp))) != 0:
                        cluster_label_list[node_id] = -3
                        print("Specific 1")
                    else:
                        cluster_label_list[node_id] = cluster_id
                        print("Specific 2")
                elif algorithm_name == AlgorithmName.GMKNN_ZhenHu:
                    if set(node_dict[node_id].GMKNN_clabel_dict.keys()).intersection(specific_set_to_draw.difference(set_temp)) != None:
                        cluster_label_list[node_id] = -3
                    else:
                        cluster_label_list[node_id] = cluster_id
        return cluster_label_list