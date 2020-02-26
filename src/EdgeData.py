__author__ = 'divya'

from enum import Enum


class EdgeData(object):
    def __init__(self, edge_id, node1_id, node2_id, weight, edge_type):
        self.edge_id = edge_id
        self.node1_id = node1_id
        self.node2_id = node2_id
        self.edge_weight = weight
        self.edge_type = edge_type


class EdgeType(object):
    primary = 1 #edges which are exclusively primary
    secondary = 2 #edges which are exclusively secondary