__author__ = 'divya'

from EdgeData import EdgeType

class NodeData(object):

    def __init__(self, id, code, graphdata):
        self.node_id = id
        self.node_code = code
        self.graphdata = graphdata
        #self.GMKNN_clabel = -1
        self.GMKNN_clabel_dict = dict() #This dict is made for flexibility for overlapping clusters.

                                         #This saves cluster label and corresponding cluster center.
        self.clusterone_clabel_dict = dict()

        #self.MKNN_list = [-1]*K
        self.MKNN_list = []
        #self.MKNN_radius = -1
        #self.cluster_initiator_order = -1 #Removing these from here...as these are
                                           #used as a summary structures in clustering data
                                           #for all nodes at one place.
        #self.cluster_center = -1
        self.degree = -1
        self.weighted_degree = -1
        self.node_edges_dict = {}
        self.node_edges_dict[EdgeType.primary] = set()
        self.node_edges_dict[EdgeType.secondary] = set()

    ##########################################################
    #Add edge to the correct edge dict depending upon edgetype
    ##########################################################
    def add_edge_to_set(self, edge_id, edge_type):
        self.node_edges_dict[edge_type].add(edge_id)

    #########################################
    #Initialize the MKNN List for a node
    #########################################
    def initialize_MKNN(self, K):
        self.MKNN_list = [-1]*K

    def calculate_primary_degree(self):
        self.degree = len(self.node_edges_dict[EdgeType.primary])

    def calculate_primary_weighted_degree(self):
        self.weighted_degree = sum([self.graphdata.edge_dict[edge_id].edge_weight for edge_id in self.node_edges_dict[EdgeType.primary]])
        #print("weighted degree")
        #print(str(self.weighted_degree))

    def calculate_secondary_degree(self):
        pass

