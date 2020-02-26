__author__ = 'divya'


import pygraphviz as pgv
import networkx as nx
import numpy as np
import string
import urllib.request, urllib.parse, urllib.error
import random
from itertools import cycle
import matplotlib.cm as cmx
import matplotlib.colors as colors
from AlgorithmName import AlgorithmName

try:
    import matplotlib.pyplot as plt
except:
    raise

class ClusteringVisualizer(object):

    def __init__(self, graphdata, configdata, K, phase, num_clusters, cluster_label_list, algorithm_name):
        self.configdata = configdata
        self.graphdata = graphdata
        self.K = K
        self.phase = phase
        self.num_clusters = num_clusters
        self.CL_list = cluster_label_list
        self.algorithm_name = algorithm_name
        self.cluster_colors = None
        self.G = None

    def visualize_clusters(self):

        self.configdata.logger.debug("Debugging from inside visualize_clusters")

        #phase = 2
        plt.close("all")
        a_name = AlgorithmName()
        #currentdate = datetime.datetime.now()
        filename = self.configdata.eval_results_dir + "/figures/phase" + str(self.phase) + "/" + self.configdata.currentdate_str + "_" + str(a_name.get_algorithm_name(self.algorithm_name)) + "_" + self.configdata.dataset_name + "_K_" + str(self.K) + "_Phase_" + str(self.phase) + "_V_NX.png"

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
        #print(str(self.num_clusters))
        CL_list_unique = list(set(self.CL_list))

        #print(str(len(CL_list_unique)))

        #num_clusters should be the same as len(CL_List_unique)
        #but overriding it to take care of clusterone, where the two might
        #be different.
        #Plus, CL_List_unique might have -1 for all nodes with no cluster label
        #in case of clusterone.
        self.num_clusters = len(CL_list_unique)

        #Assign colors to each distinct cluster using a color map
        self.cluster_colors = self.generateCMap(CL_list_unique, self.num_clusters)
        #cluster_colors = self.generateCMap(CL_list_unique, len(CL_list_unique))

        #Create a nx graph for the similarity matrix
        self.G=nx.Graph()

        #Add edges to the graph, one edge at a time
        for i in range(0,len(self.CL_list)):
            for j in range(0, len(self.CL_list)):
                if(self.graphdata.SM_orig[i,j] != -1 and self.graphdata.SM_orig[i,j] != 0 and i!=j): #change SM[i][i] please to some other value than 1.
                    #Add edge
                    self.G.add_edge(self.graphdata.node_dict[i].node_code, self.graphdata.node_dict[j].node_code, weight=self.graphdata.SM_orig[i,j])
                    #G.add_edge(node_codes[i],node_codes[j], weight=self.graphdata.SM[i,j])

                    #Add node attributes
                    self.assign_node_attribute(i)
                    self.assign_node_attribute(j)
                    #G.node[self.graphdata.node_dict[i].node_code]['category'] = self.CL_list[i]
                    #G.node[self.graphdata.node_dict[j].node_code]['category'] = self.CL_list[j]


        #Specify the graph layout
        pos = nx.graphviz_layout(self.G)
        #
        # Draw nodes of G
        #Get nodes belonging to cluster 1
        # for cluster_idx in CL_list_unique:
        #     cluster_idx_nodes = [u for u in G.nodes() if CL_list[node_codes.index(u)] == cluster_idx]
        #     #nx.draw_networkx_nodes(G,pos,cluster_idx_nodes, node_size=200, node_color= cluster_colors[cluster_idx] )
        #     nx.draw_networkx_nodes(G,pos,cluster_idx_nodes, node_size=200, node_color= np.linspace(0,1,len(G.nodes())) )

        #Another way for drawing nodes of G:

        # #Assign a node attribute for cluster label
        # for node in G.nodes():
        #     G.node[node]['category'] = CL_list[node_codes.index(node)]


        nList=[]
        for (u,d) in self.G.nodes(data=True):
            nList.append((u,d))


        #Draw nodes with different colors for each cluster. Colors are chosen from the cluster map constructed before.
        #nx.draw_networkx_nodes(self.G, pos, node_color=[self.cluster_colors[self.G.node[node]['category']] for node in self.G], node_size = 250, alpha=0.7)
        #nx.draw_networkx_nodes(self.G, pos, node_color=[self.cluster_colors[self.G.node[node]['category']] if self.G.node[node]['category'] != -1 else "#bebcbd" for node in self.G], node_size = 250, alpha=0.7)

        nx.draw_networkx_nodes(self.G, pos, node_color=[(self.cluster_colors[self.G.node[node]['category']] if self.G.node[node]['category'] > -1 else ("#bebcbd" if self.G.node[node]['category'] == -1 else "#ffff00")) for node in self.G], node_size = 250, alpha=0.7)


        # Draw edges of G(one by one) , setting the width equal to the weight of the edge.
        for (u,v,d) in self.G.edges(data=True):
            eCurrent = [(u,v)]
            nx.draw_networkx_edges(self.G, pos, eCurrent, width=(d['weight']*4), alpha=0.2)

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
        nx.draw_networkx_labels(self.G,pos,font_size=10,font_family='sans-serif', font_weight='bold')

        #Plot the graph
        plt.axis('off')
        plt.savefig(filename) # save as png
        #plt.show() # display
        plt.close("all")

    #Visualize only specific clusters.
    def visualize_specific_clusters(self, list_to_plot):

        self.configdata.logger.debug("Debugging from inside visualize_clusters")

        #phase = 2
        plt.close("all")
        #currentdate = datetime.datetime.now()
        filename = self.configdata.eval_results_dir + "/figures/specific" + "/" + self.configdata.currentdate_str + "_" + str(self.algorithm_name) +  "_" + self.configdata.dataset_name + "_K_" + str(self.K) + "_Phase_" + str(self.phase) + "_Clusters_Some.png"
        filename_edges = self.configdata.eval_results_dir + "/figures/specific" + "/" + self.configdata.currentdate_str + "_" + str(self.algorithm_name) +  "_" + self.configdata.dataset_name + "_K_" + str(self.K) + "_Phase_" + str(self.phase) + "_Clusters_Some_edges.txt"

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
        CL_List_unique = list(set(self.CL_list))

        #Assign colors to each distinct cluster using a color map
        self.cluster_colors = self.generateCMap(list_to_plot, len(list_to_plot))

        #Create a nx graph for the similarity matrix
        self.G=nx.Graph()
        target = open(filename_edges, 'a')

        #Add edges to the graph, one edge at a time
        for i in range(0,len(self.CL_list)):
            for j in range(0, len(self.CL_list)):
                if(self.graphdata.SM_orig[i,j] != -1 and self.graphdata.SM_orig[i,j] != 0 and i!=j and self.CL_list[i] in list_to_plot and self.CL_list[j] in list_to_plot): #change SM[i][i] please to some other value than 1.
                    #G.add_edge(node_codes[i],node_codes[j], weight=self.graphdata.SM_orig[i,j])
                    self.G.add_edge(self.graphdata.node_dict[i].node_code, self.graphdata.node_dict[j].node_code, weight=self.graphdata.SM_orig[i,j], len="11.0")
                    #G.add_edge(node_codes[i],node_codes[j], weight=self.graphdata.SM[i,j])
                    target.write(str(self.graphdata.node_dict[i].node_code))
                    target.write("\t")
                    target.write(str(self.CL_list[i]))
                    target.write("\t")
                    target.write(str(self.graphdata.node_dict[j].node_code))
                    target.write("\t")
                    target.write(str(self.CL_list[j]))
                    target.write("\t")
                    target.write(str(self.graphdata.SM_orig[i,j]))
                    target.write("\n")

                    #Add node attributes
                    self.assign_node_attribute(i)
                    self.assign_node_attribute(j)
                    #G.node[self.graphdata.node_dict[i].node_code]['category'] = self.CL_list[i]
                    #G.node[self.graphdata.node_dict[j].node_code]['category'] = self.CL_list[j]


        #Specify the graph layout
        #pos = nx.graphviz_layout(self.G)

        #pos = nx.spring_layout(self.G, k=0.15,iterations=20)

        gk = self.G
        pos = nx.graphviz_layout(gk)

        #
        # Draw nodes of G
        #Get nodes belonging to cluster 1
        # for cluster_idx in CL_List_unique:
        #     cluster_idx_nodes = [u for u in G.nodes() if CL_List[node_codes.index(u)] == cluster_idx]
        #     #nx.draw_networkx_nodes(G,pos,cluster_idx_nodes, node_size=200, node_color= cluster_colors[cluster_idx] )
        #     nx.draw_networkx_nodes(G,pos,cluster_idx_nodes, node_size=200, node_color= np.linspace(0,1,len(G.nodes())) )

        #Another way for drawing nodes of G:

        #Assign a node attribute for cluster label
        #for node in G.nodes():
        #    G.node[node]['category'] = CL_List[node_codes.index(node)]

        nList=[]
        for (u,d) in self.G.nodes(data=True):
            nList.append((u,d))


        #Draw nodes with different colors for each cluster. Colors are chosen from the cluster map constructed before.
        #nx.draw_networkx_nodes(G, pos, node_color=[cluster_colors[G.node[node]['category']] for node in G], node_size = 250, alpha=0.7)
        nx.draw_networkx_nodes(gk, pos, node_color=[(self.cluster_colors[self.G.node[node]['category']] if self.G.node[node]['category'] > -1 else ("#bebcbd" if self.G.node[node]['category'] == -1 else "#ffff00")) for node in self.G], node_size = 250, alpha=0.7)


        # Draw edges of G(one by one) , setting the width equal to the weight of the edge.
        for (u,v,d) in self.G.edges(data=True):
            eCurrent = [(u,v)]
            if(self.G.node[u]['category'] == self.G.node[v]['category']): #intra cluster edge
                nx.draw_networkx_edges(gk, pos, eCurrent, width=(d['weight']*4), alpha=0.1)
            else: #inter cluster edge, draw it in a dotted style.
                nx.draw_networkx_edges(gk, pos, eCurrent, width=(d['weight']*4), alpha=0.1, style='dashed')

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
        nx.draw_networkx_labels(self.G,pos,font_size=10,font_family='sans-serif', font_weight='bold')

        #Plot the graph
        plt.axis('off')
        plt.savefig(filename) # save as png
        #plt.show() # display
        plt.close("all")



    def generateCMap(self, CL_list_unique, num_clusters):
        # use golden ratio
        golden_ratio_conjugate = 0.618033988749895
        h = random.randrange(0,1) # use random start value
        #h = 0.99 # use random start value
        cluster_colors = {}
        for i in range(0, num_clusters):
          #i=0
          h += golden_ratio_conjugate
          h %= 1
          if(CL_list_unique[i] != -1):
            cluster_colors[CL_list_unique[i]] = self.hsv_to_rgb(h, 0.49, 0.99)


        return cluster_colors

    ########################################
    # input: HSV values in [0..1]
    # returns [r, g, b] values from 0 to 255
    ########################################
    def hsv_to_rgb(self, h, s, v):


        #s=0.3
        #v=0.99
        h_i = (int)(h*6)
        f = h*6 - h_i
        p = v * (1 - s)
        q = v * (1 - f*s)
        t = v * (1 - (1 - f) * s)
        if h_i==0:
            r, g, b = v, t, p
        elif h_i==1:
            r, g, b = q, v, p
        elif h_i==2:
            r, g, b = p, v, t
        elif h_i==3:
            r, g, b = p, q, v
        elif h_i==4:
            r, g, b = t, p, v
        elif h_i==5:
            r, g, b = v, p, q
        x = hex((int)(r*256))
        y = hex((int)(g*256))
        z = hex((int) (b*256))

        x = x[2:]
        y = y[2:]
        z = z[2:]

        if len(x)<2:
            x = "0" + x
        if len(y)<2:
            y = "0" + y
        if len(z)<2:
            z = "0" + z

        hex_color = x + y + z
        return "#" + hex_color.upper()


    def assign_node_attribute(self, node_id):
        self.G.node[self.graphdata.node_dict[node_id].node_code]['category'] = self.CL_list[node_id]