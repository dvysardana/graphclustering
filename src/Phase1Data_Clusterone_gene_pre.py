__author__ = 'divya'

from Phase1Data_Clusterone import Phase1Data_Clusterone
from CNodeData_Clusterone_gene import CNodeData_Clusterone_gene

class Phase1Data_Clusterone_gene_pre(Phase1Data_Clusterone):
    def __init__(self, graphdata, configdata):
        super(Phase1Data_Clusterone_gene_pre, self).__init__(graphdata, configdata)


    #Overriding base class method
    ##################################################
    #Method to update the cluster membership of a node
    ##################################################
    def add_node_to_cluster_label(self, node, cluster_label, cluster_center, algorithm_name):
        self.configdata.logger.debug("Debugging from inside add_node_cluster_label method")

        #set the node's cluster label and cluster center in the dict
        if(algorithm_name == 0):
            node.GMKNN_clabel_dict[cluster_label] = cluster_center
        elif(algorithm_name == 1):
            node.clusterone_clabel_dict[cluster_label] = cluster_center

        # case: cluster_label does not exist in clusters dictionary
        #create a cnode object and add it to the dictionary
        if(self.cnodes_dict.get(cluster_label) == None):
            #Create a new cnode
            cnode = CNodeData_Clusterone_gene(cluster_label, -1, -1, cluster_center, self.graphdata, self.configdata)

            # #cluster.num_nodes = 1
            # cnode.node_set.add(node.node_id)
            # #Add edges to cluster's external edge dicts.
            # cnode.external_edge_dict[EdgeType.primary].update(node.node_edges_dict[EdgeType.primary])
            # cnode.external_edge_dict[EdgeType.secondary].update(node.node_edges_dict[EdgeType.secondary])

            #Add node to cnode
            self.add_node_to_cnode(node, cnode)
            #Add cnode to cnodes_dict
            self.cnodes_dict[cluster_label] = cnode


        #case: cluster_label already exists there, add the node id
        #to the corresponding c-node
        else:
            #Get all members of cluster_label
            cnode = self.cnodes_dict[cluster_label]

            #Add node to cnode
            self.add_node_to_cnode(node, cnode)

        cnode.isDirty = True
        cnode.active = True
