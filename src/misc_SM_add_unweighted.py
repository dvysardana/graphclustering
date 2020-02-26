__author__ = 'divya'

def misc_SM_add_unweighted(perc_to_add, SM, num_nodes, replace_value):
    for i in range(0, num_nodes):
        for j in range(0, num_nodes):
            if(SM[i,j] != 0 and i !=j):
                SM[i,j] = 0.5

    return SM