__author__ = 'divya'

import numpy as np
import logging

# def sort_CM(CM, num_clusters):
#     #Flatten CM to get a vector of all CM values
#
#     num_clusters =
#     CM_flat = np.array(CM).flatten()
#     CM_values = CM_flat.reshape(CM_flat.shape[0],1)
#
#     #Create an array of 0 to num_clusters
#     y = np.array(range(0,num_clusters), dtype=int).reshape(num_clusters, 1)
#
#
#     #Create a placeholder for the final sorted array
#     CM_indices = np.zeros(shape=(1,2), dtype=int)
#     #CM_indices = np.zeros(shape=(1,2), dtype=[('x',int), ('y', int)])
#
#
#     for i in range(0, num_clusters):
#         #Create an array of all i's
#         x = i * np.ones(shape=(num_clusters), dtype=int).reshape(num_clusters, 1)
#
#         #Concatenate y with x to form the row and column combinations for CM_sort
#         z = np.concatenate((x,y), axis=1)
#
#         #Store z in CM_sort
#         CM_indices = np.concatenate((CM_indices, z), axis=0)
#
#     #Delete the first row in CM_sort
#     CM_indices = np.delete(CM_indices, (0), axis=0)
#
#
#     #Concatenate CM_Flat with CM_sort now
#     CM_sort = np.concatenate((CM_indices, CM_values), axis=1)
#
#     #sort CM_sort based upon column 2 (the one with values)
#     #np.sort(CM_sort, order=2)
#
#     col=2
#     CM_sort = np.matrix(CM_sort[np.array(CM_sort[:,col].argsort(axis=0)[::-1].tolist()).reshape(-1)])
#
#     return CM_sort


def sort_CM(CM_List, log):

    #logger = log.get_logger(__name__)
    logger = logging.getLogger('root')
    logger.debug("Debugging from inside P2_sort_CM module")


    #Flatten CM to get a vector of all CM values

    num_rows_CM = len(CM_List)

    #Flatten CM to get all values in a flat list
    CM_flat = np.array(CM_List).flatten()
    CM_values = CM_flat.reshape(CM_flat.shape[0],1)

    #Create an array of 0 to num_rows_CM
    y = np.array(list(range(0,num_rows_CM)), dtype=int).reshape(num_rows_CM, 1)


    #Create a placeholder for the final sorted array
    CM_indices = np.zeros(shape=(1,2), dtype=int)
    #CM_indices = np.zeros(shape=(1,2), dtype=[('x',int), ('y', int)])


    for i in range(0, num_rows_CM):
        #Create an array of all i's
        x = i * np.ones(shape=(num_rows_CM), dtype=int).reshape(num_rows_CM, 1)

        #Concatenate y with x to form the row and column combinations for CM_sort
        z = np.concatenate((x,y), axis=1)

        #Store z in CM_sort
        CM_indices = np.concatenate((CM_indices, z), axis=0)

    #Delete the first row in CM_sort
    CM_indices = np.delete(CM_indices, (0), axis=0)


    #Concatenate CM_Flat with CM_sort now
    CM_sort = np.concatenate((CM_indices, CM_values), axis=1)

    #sort the matrix based upon column 2 (the column containing the CM values
    col=2
    CM_sort = CM_sort[np.array(CM_sort[:,col].argsort(axis=0)[::-1].tolist()).reshape(-1)]

    return np.array(CM_sort).tolist()