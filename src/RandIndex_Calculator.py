__author__ = 'divya'


#Code taken from Stackexchange:
#http://stats.stackexchange.com/questions/89030/rand-index-calculation

import numpy as np
from scipy.misc import comb

# There is a comb function for Python which does 'n choose k'
# only you can't apply it to an array right away
# So here we vectorize it...
def myComb(a,b):
    return comb(a,b,exact=True)

class RandIndex_Calculator():

    def __init__(self):
        pass


    #Method to extract true positives, true negatives, false positives and
    #false negatives from a cooccurence matrix
    def get_tp_fp_tn_fn(self, cooccurrence_matrix):
        vComb = np.vectorize(myComb)
        tp_plus_fp = vComb(cooccurrence_matrix.sum(0, dtype=int),2).sum()
        #print("Tpplusfp%s" % str(cooccurrence_matrix.sum(0, dtype=int)))
        tp_plus_fn = vComb(cooccurrence_matrix.sum(1, dtype=int),2).sum()
        #print("Tpplusfn%s" % str(cooccurrence_matrix.sum(1, dtype=int)))
        tp = vComb(cooccurrence_matrix.astype(int), 2).sum()
        #print("Tp%s" % str(cooccurrence_matrix.astype(int)))
        fp = tp_plus_fp - tp
        fn = tp_plus_fn - tp
        tn = comb(cooccurrence_matrix.sum(), 2) - tp - fp - fn

        return [tp, fp, tn, fn]

    #Read a clustering and save in a dictionary
    def read_clusters(self):
        pass

    def create_cooccurence_matrix(self, cluster_dict_1, cluster_dict_2):
        pass

    #Wrapper method for calculating rand index
    def worker(self):
        #Read clustering 1

        #Read clustering 2

        #Create Cooccurance matrix

        #Extract tp fp tn fn

        #Calculate Rand index

        pass


if __name__ == "__main__":
    # The co-occurrence matrix from example from
    # An Introduction into Information Retrieval (Manning, Raghavan & Schutze, 2009)
    # also available on:
    # http://nlp.stanford.edu/IR-book/html/htmledition/evaluation-of-clustering-1.html
    #
    rc = RandIndex_Calculator()
    cooccurrence_matrix = np.array([[ 5,  1,  2], [ 1,  4,  0], [ 0,  1,  3]])

    # Get the stats
    tp, fp, tn, fn = rc.get_tp_fp_tn_fn(cooccurrence_matrix)

    print("TP: %d, FP: %d, TN: %d, FN: %d" % (tp, fp, tn, fn))

    # Print the measures:
    print("Rand index: %f" % (float(tp + tn) / (tp + fp + fn + tn)))

    precision = float(tp) / (tp + fp)
    recall = float(tp) / (tp + fn)

    print("Precision : %f" % precision)
    print("Recall    : %f" % recall)
    print("F1        : %f" % ((2.0 * precision * recall) / (precision + recall)))
