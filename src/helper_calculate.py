__author__ = 'divya'

import pandas as pd

def calcNumClusters(CL_List, num_nodes, node_codes):
    num_clusters = 0
    output_phase1 = {'node_Labels': node_codes, 'node_Ids': list(range(0,num_nodes)), 'node_ClusterLabels': CL_List}
    frame = pd.DataFrame(output_phase1, index = [CL_List], columns = ['node_Labels', 'node_Ids', 'node_ClusterLabels'])
    num_clusters = frame['node_ClusterLabels'].value_counts().count()

    return num_clusters
