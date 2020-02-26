__author__ = 'divya'

from .P2_sort_CM import sort_CM
from .P2_updateCL import updateCL

def MKNN_Phase2_execute(CM_List, CM_sort_List, NumNodesM_List, ProjectionM_List, OutreachM_List, CL_List, c_label, num_clusters, LIMIT_CLUSTERS, log):


    merging_row_num = 0
    debug_count = 0

    #Keep merging the clusters until either
    #a.) The desired number of clusters is obtained
    #b. There is no CM_Sort value left which is greater than 0.
    while(num_clusters > LIMIT_CLUSTERS and CM_sort_List[merging_row_num][2] > 0):
            #*************************
            #get the two clusters to
            # be merged
            #*************************
            cluster_label_1 = (int) (CM_sort_List[merging_row_num][0])
            cluster_label_2 = (int) (CM_sort_List[merging_row_num][1])

            ##########################################################
            #Check if the CM value for these two clusters is not = -1
            # (meaning that a merge already took place between the two
            ##########################################################
            if(CM_List[cluster_label_1][cluster_label_2] > 0):

                print('Inside the if part where merging takes place.')
                print(('Cluster label 1%d', cluster_label_1))
                print(('Cluster label 2%d', cluster_label_2))

                debug_count = debug_count + 1


                #*************************
                #Get the last available
                # cluster label in order
                # to name this new cluster
                #************************
                cluster_label_new = c_label


                #************************
                #Update Matrices
                #************************

                #Update NumNodesM
                # NumNodesM_List.append(NumNodesM_List[cluster_label_1] + NumNodesM_List[cluster_label_2])

                NumNodesM_List.append([NumNodesM_List[cluster_label_1][0] + NumNodesM_List[cluster_label_2][0]])


                #Update ProjectionM and OutreachM and CM
                projection_new_row = []
                #projection_new_column = []

                outreach_new_row = []

                CM_new_row = []

                #Update value of projection, outreach and CM for each currently existing cluster
                for current_cluster_no in range(0, len(CM_List)):
                    #current_cluster_no = 0
                    num_nodes_current_cluster = NumNodesM_List[current_cluster_no][0]

                    ##############################################
                    #Updates for Projection List (Inside the loop)
                    #############################################

                    #Create a new row for new cluster label and for column: current cluster label
                    #This new row will be fully built first in the loop and then added as a whole outside the loop.
                    #A special case: Merged cluster's Projection value with cluster label 1 and cluster label 2 to
                    # be set to 0 manually.
                    projection_new_row_value = ProjectionM_List[cluster_label_1][current_cluster_no] + ProjectionM_List[cluster_label_2][current_cluster_no]
                    if projection_new_row_value < 0 or current_cluster_no == cluster_label_1 or current_cluster_no == cluster_label_2:
                        projection_new_row_value = -1

                    projection_new_row.append(projection_new_row_value)
                    #projection_new_column.append(ProjectionM_List[current_cluster_no][cluster_label_1] + ProjectionM_List[current_cluster_no][cluster_label_2])

                    #Add new projection value in the new column for new cluster label and row: current_cluster_label
                    #This new column. row value will be added in the for loop one by one.
                    projection_new_column_value = ProjectionM_List[current_cluster_no][cluster_label_1] + ProjectionM_List[current_cluster_no][cluster_label_2]
                    if projection_new_column_value < 0 or current_cluster_no == cluster_label_1 or current_cluster_no == cluster_label_2:
                        projection_new_column_value = -1

                    ProjectionM_List[current_cluster_no].append(projection_new_column_value)

                    #Nullify the projection values for cluster label 1 and cluster label 2 with all the other clusters
                    #because they have been merged and the individual clusters don't matter now.
                    ProjectionM_List[cluster_label_1][current_cluster_no] = -1
                    ProjectionM_List[cluster_label_2][current_cluster_no] = -1
                    ProjectionM_List[current_cluster_no][cluster_label_1] = -1
                    ProjectionM_List[current_cluster_no][cluster_label_2] = -1


                    ############################################
                    #Updates for Outreach List (Inside the loop)
                    ############################################
                    #Calculate the new outreach value between the current cluster and the new cluster
                    #A special case: Outreach value between new cluster and cluster label 1 and
                    #cluster label 2 needs to be set manually= -1
                    outreach_new_value = OutreachM_List[cluster_label_1][current_cluster_no] + OutreachM_List[cluster_label_2][current_cluster_no]
                    if outreach_new_value < 0 or current_cluster_no == cluster_label_1 or current_cluster_no == cluster_label_2:
                        outreach_new_value = -1
                    outreach_new_row.append(outreach_new_value)
                    OutreachM_List[current_cluster_no].append(outreach_new_value)

                    #Nullify the outreach values for cluster label 1 and cluster label 2 with all the other clusters
                    #because they have been merged and their individual values don't count now.
                    OutreachM_List[cluster_label_1][current_cluster_no] = -1
                    OutreachM_List[cluster_label_2][current_cluster_no] = -1
                    OutreachM_List[current_cluster_no][cluster_label_1] = -1
                    OutreachM_List[current_cluster_no][cluster_label_2] = -1

                    ###############################################
                    #Updates for CM List (Inside the loop)
                    ###############################################
                    if outreach_new_value == -1 or projection_new_row_value == -1:
                        CM_new_row_value = -1
                    else:
                        CM_new_row_value = (outreach_new_value * projection_new_row_value)/(((float)(NumNodesM_List[cluster_label_new][0]) * (float)(NumNodesM_List[cluster_label_new][0]) * (float) (num_nodes_current_cluster)))

                    if outreach_new_value == -1 or projection_new_column_value == -1:
                        CM_new_column_value = -1
                    else:
                        CM_new_column_value = (outreach_new_value * projection_new_column_value)/ (num_nodes_current_cluster * num_nodes_current_cluster * NumNodesM_List[cluster_label_new][0])

                    CM_new_row.append(CM_new_row_value)
                    CM_List[current_cluster_no].append(CM_new_column_value)

                    #Nullify the CM values for cluster label 1 and cluster label 2 with all the
                    #other clusters because the new merged cluster represents both of them now.
                    CM_List[cluster_label_1][current_cluster_no] = -1
                    CM_List[cluster_label_2][current_cluster_no] = -1
                    CM_List[current_cluster_no][cluster_label_1] = -1
                    CM_List[current_cluster_no][cluster_label_2] = -1


                ###############################################
                #Updates for Projection List (Outside the loop)
                ###############################################

                projection_new_row.append(-1) #Projection of new cluster with self = -1
                #Add the row for the new cluster to ProjectionM
                ProjectionM_List.append(projection_new_row)

                #Nullify the projection values between cluster 1 and cluster 2
                #ProjectionM_List[cluster_label_1][cluster_label_2] = -1
                #ProjectionM_List[cluster_label_2][cluster_label_1] = -1


                ###############################################
                #Updates for Outreach List (Outside the loop)
                ###############################################
                outreach_new_row.append(-1) #Outreach of new cluster with itself
                #Add the new row for the new cluster to OutreachM
                OutreachM_List.append(outreach_new_row)

                #Nullify the outreach values between cluster 1 and cluster 2
                #OutreachM_List[cluster_label_1][cluster_label_2] = -1
                #OutreachM_List[cluster_label_2][cluster_label_1] = -1


                #############################################
                #Updates for CM (Outside the loop)
                #############################################
                CM_new_row.append(-1)
                #Add the row for the new cluster to CM
                CM_List.append(CM_new_row)

                #Nullify the CM values between cluster label 1 and cluster label 2
                #CM_List[cluster_label_1][cluster_label_2] = -1
                #CM_List[cluster_label_2][cluster_label_1] = -1


                ######################################################
                #Nullify the values of NumNodesM_List (after the loop)
                ######################################################
                NumNodesM_List[cluster_label_1][0] = -1
                NumNodesM_List[cluster_label_2][0] = -1

                len(ProjectionM_List)
                len(OutreachM_List)
                len(CM_List)

                #************************
                #Update CL
                #************************
                CL_List = updateCL(CL_List, cluster_label_1, cluster_label_new, log)
                CL_List = updateCL(CL_List, cluster_label_2, cluster_label_new, log)

                #***********************
                #Increment the cluster
                #label
                #***********************
                c_label = c_label+1


                #**********************
                #Prepare for the next
                # iteration
                #**********************
                #IF CMsorting is not called
                #merging_row_num = merging_row_num + 1
                #IF CMsorting is called
                # merging_row_num remains equal to 0 always
                merging_row_num = 0
                CM_sort_List = sort_CM(CM_List, log)

                #the number of clusters goes down by 1 as
                #a merger has taken place
                num_clusters = num_clusters - 1
            else:
                #CM_sort_list for cluster_label_1 and cluster_label_2 is not 0
                #But CM_List = -1
                #This happens when the two clusters already merged before
                #No merging takes place here in this case.
                ##################
                #Prepare for the next iteration

                #Delete the top most row
                #del CM_sort_List[0]
                print('Inside the else part where no merging takes place.')
                #merging_row_num remains equal to 0
                merging_row_num = merging_row_num + 1
                #num_clusters remains the same as before

    debug_count

    return (CL_List, num_clusters)
