__author__ = 'divya'

class AlgorithmName(object):
    GMKNN_ZhenHu = 0
    Clusterone = 1
    GMKNN_WI = 2
    GMKNN_CorePeriphrey = 3

    def __init__(self):
        pass

    def get_algorithm_name(self, acode):
        if acode == 0:
            return "GMKNN_ZhenHu"
        elif acode == 1:
            return "clusterone"
        elif acode == 2:
            return "GMKNN_WI"
        elif acode == 3:
            return "GMKNN_CP"
        else:
            return "unknown"