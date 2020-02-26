__author__ = 'divya'

import numpy as np
import pandas as pd
import nltk
import re
import os
import codecs
import logging
from .config_get_logger import logger_class
from sklearn import feature_extraction

import os  # for os.path.basename

import matplotlib.pyplot as plt
import random

from sklearn.manifold import MDS




def visualizeClusters(SM, CL_List, node_codes, num_clusters, K, phase, currentdate_str, dataset_name, eval_results_dir, log):

    #logger = log.get_logger(__name__)
    #logger = logging.getLogger('root')
    logger = logging.getLogger('root')
    logger.debug("Debugging from inside visualizeClusters module")

    #phase = 2
    #currentdate = datetime.datetime.now()
    filename = eval_results_dir + "/figures/phase" + str(phase) + "/" + currentdate_str + "_GMKNN_" + dataset_name + "_K_" + str(K) + "_Phase_" + str(phase) + "_V_MDS.png"
    MDS()

    mds = MDS(n_components=2, dissimilarity="precomputed", random_state=1)

    pos = mds.fit_transform(1-SM)  # shape (n_components, n_samples)

    xs, ys = pos[:, 0], pos[:, 1]
    print()
    print()

    #imitating the code already there in python for data visualization to
    #learn pandas as well as matplotliblibrary.


    #set up colors per clusters using a dict
    # cluster_colors = {0: '#1b9e707',
    #                   1: '#d95f02',
    #                   2: '#7570b3',
    #                   3: '#e7298a',
    #                   4: '#66a61e',
    #                   5: '#bae2bf',
    #                   6: '#ff7373',
    #                   7: '#b0e0e6',
    #                   8: '#ffd700',
    #                   9: '#ff60b0',
    #                   10: '#00aaff',
    #                   11: '#728c9f',
    #                   12: '#9f2424',
    #                   13: '#b16ee4',
    #                   14: '#007694',
    #                   15: '#f3f15d'}

    cluster_colors = {i : hex_code_colors() for i in range(0, num_clusters)}


    #set up cluster names using a dict
    # cluster_names = {0: '0',
    #                  1: '1',
    #                  2: '2',
    #                  3: '3',
    #                  4: '4',
    #                  5: '5',
    #                  6: '6',
    #                  7: '7',
    #                  8: '8',
    #                  9: '9',
    #                  10: '10',
    #                  11: '11',
    #                  12: '12',
    #                  13: '13',
    #                  14: '14',
    #                  15: '15'}

    CL_List_unique = list(set(CL_List))
    cluster_names = {i:CL_List_unique[i] for i in range(0, num_clusters)}
    #some ipython magic to show the matplotlib plots inline
    #%matplotlib inline

    #create data frame that has the result of the MDS plus the cluster numbers and titles
    df = pd.DataFrame(dict(x=xs, y=ys, label=CL_List, title=node_codes))

    #group by cluster
    groups = df.groupby('label')


    ######################
    #set up font size


    # set up plot
    #fig, ax = plt.subplots(figsize=(17, 9)) # set size
    fig, ax = plt.subplots(figsize=(30, 12)) # set size
    ax.margins(0.05) # Optional, just adds 5% padding to the autoscaling

    #iterate through groups to layer the plot
    #note that I use the cluster_name and cluster_color dicts with the 'name' lookup to return the appropriate color/label
    for name, group in groups:
        # ax.plot(group.x, group.y, marker='o', linestyle='', ms=25,
        #         label=cluster_names[CL_List_unique.index(name)], color=cluster_colors[CL_List_unique.index(name)],
        #         mec='none')
        ax.plot(group.x, group.y, marker='o', linestyle='', ms=25,
                label=name, color=cluster_colors[CL_List_unique.index(name)],
                mec='none')



        ax.set_aspect('auto')
        ax.tick_params(\
            axis= 'x',          # changes apply to the x-axis
            which='both',      # both major and minor ticks are affected
            bottom='off',      # ticks along the bottom edge are off
            top='off',         # ticks along the top edge are off
            labelbottom='off')
        ax.tick_params(\
            axis= 'y',         # changes apply to the y-axis
            which='both',      # both major and minor ticks are affected
            left='off',      # ticks along the bottom edge are off
            top='off',         # ticks along the top edge are off
            labelleft='off')

    ax.legend(numpoints=1,loc=0, prop={'size':8})  #show legend with only 1 point


    #add label in x,y position with the label as the film title
    for i in range(len(df)):
        ax.text(df.ix[i]['x'], df.ix[i]['y'], df.ix[i]['title'], size=14)

     # for item in ([ax.title, ax.xaxis.label, ax.yaxis.label, ax.legend]):
     #    item.set_fontsize(12)

    #plt.show() #show the plot

    #uncomment the below to save the plot if need be
   # plt.savefig('figures/clusters_small_noaxes_1.png', dpi=200)
    plt.savefig(filename, dpi=200)

    plt.close()
    ######################


def hex_code_colors():
    a = hex((random.randrange(0,128) + 127))
    b = hex((random.randrange(0,128) + 127))
    c = hex((random.randrange(0,128) + 127))
    a = a[2:]
    b = b[2:]
    c = c[2:]
    if len(a)<2:
        a = "0" + a
    if len(b)<2:
        b = "0" + b
    if len(c)<2:
        c = "0" + c
    z = a + b + c
    return "#" + z.upper()