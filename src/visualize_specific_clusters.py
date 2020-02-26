__author__ = 'divya'

import pygraphviz as pgv
import networkx as nx
import numpy as np
import string
import urllib.request, urllib.parse, urllib.error
import random
import logging
import matplotlib.cm as cmx
import matplotlib.colors as colors

from .helper_hsv_to_rgb import hsv_to_rgb

try:
    import matplotlib.pyplot as plt
except:
    raise

def visualize_specific_clusters(SM, CL_List, List_To_Plot, node_codes, num_clusters, K, phase, currentdate_str, dataset_name, eval_results_dir, log):

    #logger = log.get_logger(__name__)
    logger = logging.getLogger('root')
    logger.debug("Debugging from inside visualize_specific_clusters module")

    #phase = 2
    plt.close("all")
    #currentdate = datetime.datetime.now()
    filename = eval_results_dir + "/figures/specific/" + currentdate_str + "_GMKNN_" + dataset_name + "_K_" + str(K) + "_Phase_" + str(phase) + "_Clusters_Some.png"

    #########################################################
    #Code below is a way for plotting graph from matrix.
    #Didnt use it finally, because, we had to put attributes to nodes and edges.
    # dt =[('len', float)]
    # SM = SM.view(dt)
    #
    # G = nx.from_numpy_matrix(SM)
    # G.nodes()
    # G.edges()
    # G = nx.relabel_nodes(G, dict(zip(range(len(G.nodes())), node_codes)))
    # #G = nx.relabel_nodes(G, dict(zip(range(len(G.nodes())),string.ascii_uppercase)))
    # G = nx.to_agraph(G)
    #
    # G.node_attr.update(color="red", style="filled")
    # G.edge_attr.update(color="blue", width="2.0")
    #
    # edges = G.edges()
    #
    #
    # G.draw('figures/distances.png', format='png',prog='dot')
    ##########################################################

    #Generate a unique list of cluster labels
    CL_List_unique = list(set(CL_List))

    #Assign colors to each distinct cluster using a color map
    cluster_colors = generateCMap(List_To_Plot, len(List_To_Plot))

    #Create a nx graph for the similarity matrix
    G=nx.Graph()

    #Add edges to the graph, one edge at a time
    for i in range(0,len(node_codes)):
        for j in range(0, len(node_codes)):
            if(SM[i,j] != -1 and SM[i,j] != 0 and i!=j and CL_List[i] in List_To_Plot and CL_List[j] in List_To_Plot): #change SM[i][i] please to some other value than 1.
                G.add_edge(node_codes[i],node_codes[j], weight=SM[i,j])

    #Specify the graph layout
    pos = nx.graphviz_layout(G)
    #
    # Draw nodes of G
    #Get nodes belonging to cluster 1
    # for cluster_idx in CL_List_unique:
    #     cluster_idx_nodes = [u for u in G.nodes() if CL_List[node_codes.index(u)] == cluster_idx]
    #     #nx.draw_networkx_nodes(G,pos,cluster_idx_nodes, node_size=200, node_color= cluster_colors[cluster_idx] )
    #     nx.draw_networkx_nodes(G,pos,cluster_idx_nodes, node_size=200, node_color= np.linspace(0,1,len(G.nodes())) )

    #Another way for drawing nodes of G:

    #Assign a node attribute for cluster label
    for node in G.nodes():
        G.node[node]['category'] = CL_List[node_codes.index(node)]

    nList=[]
    for (u,d) in G.nodes(data=True):
        nList.append((u,d))


    #Draw nodes with different colors for each cluster. Colors are chosen from the cluster map constructed before.
    nx.draw_networkx_nodes(G, pos, node_color=[cluster_colors[G.node[node]['category']] for node in G], node_size = 250, alpha=0.7)


    # Draw edges of G(one by one) , setting the width equal to the weight of the edge.
    for (u,v,d) in G.edges(data=True):
        eCurrent = [(u,v)]
        if(G.node[u]['category'] == G.node[v]['category']): #intra cluster edge
            nx.draw_networkx_edges(G, pos, eCurrent, width=(d['weight']*4), alpha=0.2)
        else: #inter cluster edge, draw it in a dotted style.
            nx.draw_networkx_edges(G, pos, eCurrent, width=(d['weight']*4), alpha=0.2, style='dashed')

    ##########################
    # elarge=[(u,v) for (u,v,d) in G.edges(data=True) if d['weight'] >0.5]
    # esmall=[(u,v) for (u,v,d) in G.edges(data=True) if d['weight'] <=0.5]
    #
    # #nx.draw_networkx_edges(G,pos)
    # nx.draw_networkx_edges(G,pos,edgelist=elarge,
    #                 width=2, alpha=0.5)
    # nx.draw_networkx_edges(G,pos,edgelist=esmall,
    #                 width=1, alpha=0.5)


    #Draw labels of G
    nx.draw_networkx_labels(G,pos,font_size=10,font_family='sans-serif', font_weight='bold')

    #Plot the graph
    plt.axis('off')
    plt.savefig(filename) # save as png
    #plt.show() # display
    plt.close("all")

# #This function generates random hexadecimal colors
# def hex_code_colors():
#     a = hex((random.randrange(0,128) + 127))
#     b = hex((random.randrange(0,128) + 127))
#     c = hex((random.randrange(0,128) + 127))
#     a = a[2:]
#     b = b[2:]
#     c = c[2:]
#     if len(a)<2:
#         a = "0" + a
#     if len(b)<2:
#         b = "0" + b
#     if len(c)<2:
#         c = "0" + c
#     z = a + b + c
#     return "#" + z.upper()
#
# def get_cmap(N):
#     '''Returns a function that maps each index in 0, 1, ... N-1 to a distinct
#     RGB color.'''
#     color_norm  = colors.Normalize(vmin=0, vmax=N-1)
#     scalar_map = cmx.ScalarMappable(norm=color_norm, cmap='hsv')
#     def map_index_to_rgb_color(index):
#         return scalar_map.to_rgba(index)
#     return map_index_to_rgb_color


def generateCMap(CL_List_unique, num_clusters):
    # use golden ratio
    golden_ratio_conjugate = 0.618033988749895
    h = random.randrange(0,1) # use random start value
    #h = 0.99 # use random start value
    cluster_colors = {}
    for i in range(0, num_clusters):
      #i=0
      h += golden_ratio_conjugate
      h %= 1
      cluster_colors[CL_List_unique[i]] = hsv_to_rgb(h, 0.99, 0.99)

    return cluster_colors

