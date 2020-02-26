__author__ = 'divya'

from Phase2Data import Phase2Data
from CNodeData_WI import CNodeData_WI
from EdgeData import EdgeType
from CNodeRelationshipScore import CNodeRelationshipScore
from CNodeRelationship import CNodeRelationship
from CNodeRelationshipType import CNodeRelationshipType
from EvaluationData_WI import EvaluationData_WI
from AlgorithmName import AlgorithmName
from CNodeRelationshipDictionary import CNodeRelationshipDictionary
from CNodeData import ClusterStatus

class Phase2Data_WI(Phase2Data):

    def __init__(self, graphdata, configdata, K, cnodes_dict, next_cluster_label, num_clusters):
        super(Phase2Data_WI, self).__init__(graphdata, configdata, K, cnodes_dict, next_cluster_label, num_clusters)

        self.cnode_cluster_initiator_list = []
        #self.cnode_MKNN_radius_dict = {}
        self.cnode_id_map = dict()

        self.MEAN_DIFF = configdata.mean_diff

        self.c_OM = []

        self.OVERLAP_THRESHOLD = configdata.overlap_threshold


        self.periphery_ycohesion_nsd_dict = dict() #Key: periphery cnodes which satisfy cohesion, not sd
                                                   #Values: A set of thier core cnodes
        self.periphery_ncohesion_ysd_dict = dict() #Key: nodes which dont satisfy cohesion, satisfy sd
                                                   #Values: A set of their core cnodes
        self.periphery_ncohesion_nsd_low_dict = dict() #Key:nodes which dont satisfy cohesion and sd, lower mean than core
                                                       #Values: A set of their core cnodes
        self.periphery_ncohesion_nsd_high_dict = dict() #Key: nodes which dont satisfy cohesion and sd, higher mean than core
                                                        #Values: A set of their core cnodes
        self.periphery_dict = {}

        self.cnode_relationship_dict = CNodeRelationshipDictionary()

    def initialize_phase(self):
        self.configdata.logger.debug("Debugging from inside initialize_phase method of class Phase2Data_WI.")

        #Call the super class method.
        super().initialize_phase()

        #Sort the nodes in the descending order of cohesion.
        self.sort_cnodes_1()

        #Initialize MKNN lists and construct cnode id map
        self.initialize_MKNN_lists()

        #Calculate MKNN neighbors of nodes
        self.calculate_cnode_MKNN()

        print("Cluster initiator order:")
        self.helper.print_list(self.cnode_cluster_initiator_list)


    def execute_phase(self):
        self.configdata.logger.debug("Debugging from inside Phase2Data_WI class's execute_phase method.")

        #execute phase
        self.MKNN_phase2_execute()

        #merge highly overlapping cnodes
        self.MKNN_phase2_overlap()

        #extract core periphery relationships
        self.extract_core_periphery_relationships()

        #extract global core periphery relationships
        self.extract_global_core_periphery_relationships()

    def evaluate_phase(self):
        self.configdata.logger.debug("Debugging from inside Phase2Data_WI class's evaluate_phase method.")
        self.phase2_evaluation_data = EvaluationData_WI(self.graphdata, self.configdata, self.K, self.phase, self.num_clusters, self.cnodes_dict, self.cnode_relationship_dict, AlgorithmName.GMKNN_WI)
        self.phase2_evaluation_data.calculate_evaluation_measures_for_one_K()


    #Method to sort cnodes as per cohesion to get the cnode cluster initiator order.
    def sort_cnodes_1(self):
        self.configdata.logger.debug("Debugging from inside sort_cnodes_1 method of class Phase2Data_WI.")
        cnode_sort_list = []
        for cnode_id, cnode_data in self.cnodes_dict.items():
            if cnode_data.active == True:
                cnode_sort_list.append((cnode_id, cnode_data.cohesion))
            #cnode_data.initialize_MKNN(self.K)


        cnode_sort_list = sorted(cnode_sort_list, key = lambda x:x[1], reverse = True)
        self.cnode_cluster_initiator_list = [x for (x,y) in cnode_sort_list]

    #Initialize MKNN list for all active cnodes.
    def initialize_MKNN_lists(self):
        self.configdata.logger.debug("Initializing the MKNN lists of all active cnodes.")
        for cnode_id, cnode_data in self.cnodes_dict.items():
            if cnode_data.active == True:
                cnode_data.initialize_MKNN(self.K)
                #self.cnode_id_map[cnode_id] = cnode_id

    #Method to calculate MKNN cnode neighbors for each cnode.
    def calculate_cnode_MKNN(self):
        self.configdata.logger.debug("Debugging from inside calculate_cnode_MKNN method of class Phase2Data_WI.")

        for i in range(len(self.c_SM_sort)):
            row = self.c_SM_sort[i][0]
            col = self.c_SM_sort[i][1]
            edge_weight = self.c_SM_sort[i][2]

            if(self.cnodes_dict[self.cnode_id_map[row]].active == True and self.cnodes_dict[self.cnode_id_map[col]].active == True):
                if(self.boundary_check_for_MKNN(self.cnode_id_map[row], self.cnode_id_map[col]) == False):
                    if(row < col and edge_weight != 0):
                        #check if valid row column and edge weight values
                        MKNN_list_row = self.cnodes_dict[self.cnode_id_map[row]].cnode_MKNN_list
                        MKNN_list_col = self.cnodes_dict[self.cnode_id_map[col]].cnode_MKNN_list
                        if( -1 in MKNN_list_row and -1 in MKNN_list_col):
                            idx_row = MKNN_list_row.index(-1)
                            idx_col = MKNN_list_col.index(-1)
                            MKNN_list_row[idx_row] = col
                            MKNN_list_col[idx_col] = row

    #Method to check if two cnodes have any member cnodes which
    # are in boundary of each other.
    #Such nodes should not be made MKNN neighbors of each other.
    def boundary_check_for_MKNN(self, cnode_id_1, cnode_id_2):
        self.configdata.logger.debug("Debugging from inside boundary_check_MKNN method of class Phase2Data_WI.")
        cnode_data_1 = self.cnodes_dict[cnode_id_1]
        cnode_data_2 = self.cnodes_dict[cnode_id_2]
        #self.helper.print_set(set(list(cnode_data_1.boundary_cnode_dict_ycohesion_nsd.keys())))
        # cnode_boundary_set_1 = set(list(cnode_data_1.boundary_cnode_dict_ycohesion_nsd.keys())).update(set(list(cnode_data_1.boundary_cnode_dict_ncohesion_ysd.keys()))).update(set(list(cnode_data_1.boundary_cnode_dict_ncohesion_nsd_low.keys())))
        # cnode_boundary_set_2 = set(list(cnode_data_2.boundary_cnode_dict_ycohesion_nsd.keys())).update(set(list(cnode_data_2.boundary_cnode_dict_ncohesion_ysd.keys()))).update(set(list(cnode_data_2.boundary_cnode_dict_ncohesion_nsd_low.keys())))
        cnode_boundary_set_1 = set(list(cnode_data_1.boundary_cnode_dict_ycohesion_nsd_low.keys())).union(set(list(cnode_data_1.boundary_cnode_dict_ncohesion_ysd.keys()))).union(set(list(cnode_data_1.boundary_cnode_dict_ncohesion_nsd_low.keys()))).union(set(list(cnode_data_1.boundary_cnode_dict_ycohesion_ysd_pp.keys())))
        cnode_boundary_set_2 = set(list(cnode_data_2.boundary_cnode_dict_ycohesion_nsd_low.keys())).union(set(list(cnode_data_2.boundary_cnode_dict_ncohesion_ysd.keys()))).union(set(list(cnode_data_2.boundary_cnode_dict_ncohesion_nsd_low.keys()))).union(set(list(cnode_data_1.boundary_cnode_dict_ycohesion_ysd_pp.keys())))

        cnode_member_set_1 = cnode_data_1.member_cnode_set
        cnode_member_set_1.add(cnode_id_1)
        cnode_member_set_2 = cnode_data_2.member_cnode_set
        cnode_member_set_2.add(cnode_id_2)

        # if cnode_id_2 == 16:
        #     print("Cnode 1:")
        #     print(str(cnode_id_1))
        #     print("Cnode 1 member set.")
        #     self.helper.print_set(cnode_member_set_1)
        #     print("cnode boundary set.")
        #     self.helper.print_set(cnode_boundary_set_2)

        if bool(cnode_member_set_1.intersection(cnode_boundary_set_2)) == True or bool(cnode_member_set_2.intersection(cnode_boundary_set_1)) == True:
            print("MKNN boundary intersection found.")
            print(str(cnode_data_1.cnode_id))
            print(",")
            print(str(cnode_data_2.cnode_id))
            return True
        else:
            return False

    #Method to override super class method
    #to redirect code to use WI version of
    #c_SM calculation
    def calculate_c_SM(self):
        self.calculate_c_SM_WI()
        #self.calculate_c_SM_Zhen()
        #self.calculate_c_SM_WI_1()

    #Zhen Hu version of calculater_c_SM
    def calculate_c_SM_Zhen(self):
        self.configdata.logger.debug("Debugging from inside calculate_c_SM_Zhen method of class Phase2Data_Zhen.")
        cm_i = 0
        for i in range(0, self.next_cluster_label):
            cnode_i = self.cnodes_dict[i]
            if cnode_i.active == True:
                if cnode_i.isDirty == True:
                    cnode_i.calculate_cnode_secondary_fields()
                self.cnode_id_map[cm_i] = i
                cm_i = cm_i + 1

        super().calculate_c_SM()

    #WI version to calculate c_SM
    def calculate_c_SM_WI(self):
        self.configdata.logger.debug("Debugging from inside calculate_c_SM_WI method of class Phase2Data_WI.")

        #print("Active cnodes after iteration:")
        # for cnode_i, cnode_data in self.cnodes_dict.items():
        #     if cnode_data.active == True:
        #         print(str(cnode_i))
        #         #self.cnode_id_map[cnode_id] = cnode_id

        #initialize c_SM
        self.c_SM = [[-1] * self.num_clusters for i in range(self.num_clusters)]
        self.projectionM = [[-1] * self.num_clusters for i in range(self.num_clusters)]
        self.outreachM = [[-1] * self.num_clusters for i in range(self.num_clusters)]
        prev_cnode_id_map = self.cnode_id_map
        self.cnode_id_map = dict()
        print("Number of clusters")
        print(self.num_clusters)
        print("Next cluster label")
        print(self.next_cluster_label)
        cm_i = 0
        cm_j = 0

        for i in range(0, self.next_cluster_label):
            cnode_i = self.cnodes_dict[i]
            if cnode_i.active == True:
                if cnode_i.isDirty == True:
                    cnode_i.calculate_cnode_secondary_fields()
                self.cnode_id_map[cm_i] = i
                cm_j = cm_i + 1
                if i != self.next_cluster_label:
                    for j in range(i+1, self.next_cluster_label):
                        cnode_j = self.cnodes_dict[j]

                        if cnode_j.active == True:

                            if cnode_j.isDirty == True:
                                cnode_j.calculate_cnode_secondary_fields()
                            linkageij = 0
                            shared_edgeset = cnode_i.calculate_shared_edge_set(cnode_j)
                            #sum_shared = sum(shared_edgeset)
                            sum_shared = cnode_i.calculate_sum_edgeset(shared_edgeset)
                            if cnode_i.outsim == 0 or cnode_j.outsim == 0:
                                linkageij = 0
                            else:
                                linkageij = (float)((float)(sum_shared)/(float)(cnode_i.outsim)) + (float)((float)(sum_shared)/(float)(cnode_j.outsim))

                            #self.c_SM[i][j] = linkageij
                            #self.c_SM[j][i] = linkageij
                            self.c_SM[cm_i][cm_j] = linkageij
                            self.c_SM[cm_j][cm_i] = linkageij
                            cm_j = cm_j + 1



                    cm_i = cm_i + 1


    #WI version to calculate c_SM
    def calculate_c_SM_WI_1(self):
        self.configdata.logger.debug("Debugging from inside calculate_c_SM_WI method of class Phase2Data_WI.")

        print("Active cnodes after iteration:")
        for cnode_i, cnode_data in self.cnodes_dict.items():
            if cnode_data.active == True:
                print(str(cnode_i))
                #self.cnode_id_map[cnode_id] = cnode_id


        #initialize c_SM
        self.c_SM = [[-1] * self.num_clusters for i in range(self.num_clusters)]
        self.projectionM = [[-1] * self.num_clusters for i in range(self.num_clusters)]
        self.outreachM = [[-1] * self.num_clusters for i in range(self.num_clusters)]
        prev_cnode_id_map = self.cnode_id_map
        self.cnode_id_map = dict()
        print("Number of clusters")
        print(self.num_clusters)
        print("Next cluster label")
        print(self.next_cluster_label)
        cm_i = 0
        cm_j = 0

        for i in range(0, self.next_cluster_label):
            cnode_i = self.cnodes_dict[i]
            if cnode_i.active == True:
                if cnode_i.isDirty == True:
                    cnode_i.calculate_cnode_secondary_fields()
                self.cnode_id_map[cm_i] = i
                cm_j = cm_i + 1
                if i != self.next_cluster_label:
                    for j in range(i+1, self.next_cluster_label):
                        cnode_j = self.cnodes_dict[j]

                        if cnode_j.active == True:

                            if cnode_j.isDirty == True:
                                cnode_j.calculate_cnode_secondary_fields()
                            linkageij = 0
                            shared_edgeset = cnode_i.calculate_shared_edge_set(cnode_j)
                            #sum_shared = sum(shared_edgeset)
                            sum_shared = cnode_i.calculate_sum_edgeset(shared_edgeset)
                            linkageij = (float)(sum_shared)

                            #self.c_SM[i][j] = linkageij
                            #self.c_SM[j][i] = linkageij
                            self.c_SM[cm_i][cm_j] = linkageij
                            self.c_SM[cm_j][cm_i] = linkageij
                            cm_j = cm_j + 1



                    cm_i = cm_i + 1


    def MKNN_phase2_wrapper(self):
        pass

    #Overriding the base class method for implementing phase 2 for WI
    def MKNN_phase2_execute(self):
        self.configdata.logger.debug("Debugging from inside MKNN_phase2_execute method of class Phase2Data_WI.")
        continueFlag = True
        periphery_score = 0
        prev_cluster_label = self.next_cluster_label
        iteration_number = 0
        while(continueFlag == True):
            print("iteration:")
            print(str(iteration_number))
            iteration_number = iteration_number + 1
            iteration_num_clusters = self.num_clusters
            print("num clusters:")
            print(self.num_clusters)
            print("size of cluster initiator list:")
            print(str(len(self.cnode_cluster_initiator_list)))

            for i in range(iteration_num_clusters):
                cnode_initiator_id = self.cnode_cluster_initiator_list[i]
                cnode_initiator_data = self.cnodes_dict[cnode_initiator_id]

                self.configdata.logger.debug("Initiator:")
                self.configdata.logger.debug(cnode_initiator_id)

                print("Initiator:")
                print(str(cnode_initiator_id))

                clabel_current = -1
                cnode_merger_set = set()


                mean_diff = self.MEAN_DIFF
                if(len(cnode_initiator_data.cnode_GMKNN_clabel_dict) == 0 and cnode_initiator_data.num_nodes > 1):
                    self.configdata.logger.debug("Initiator cnode's cluster label is not yet set,"
                                                 " and number of nodes in cnode is > 1, "
                                                 "so it will initiate clustering:")

                    cnode_data_merged = cnode_initiator_data
                    #Check cluster initiator's neighbor cnodes for cluster membership
                    for j in range(self.K):
                        #j=0
                        cnode_initiator_MKNN_id = -1 if cnode_initiator_data.cnode_MKNN_list[j] == -1 else self.cnode_id_map[cnode_initiator_data.cnode_MKNN_list[j]]
                        cnode_initiator_MKNN_data = None if cnode_initiator_MKNN_id == -1 else self.cnodes_dict[cnode_initiator_MKNN_id]

                        add_flag = -1
                        print("MKNN neighbor:")
                        print(str(cnode_initiator_MKNN_id))

                        if(cnode_initiator_MKNN_id != -1 and len(cnode_initiator_MKNN_data.cnode_GMKNN_clabel_dict) == 0 and self.check_if_MKNN_core_of_initiator(cnode_initiator_MKNN_id, cnode_initiator_id) == False):
                            self.configdata.logger.debug("MKNN neighbor:")
                            self.configdata.logger.debug(cnode_initiator_MKNN_id)
                            print("MKNN neighbor not = 1 and not the core of current initiator.")
                            #print(str(cnode_initiator_MKNN_id))



                            (structure_constraint, edge_weight_constraint) = cnode_data_merged.check_structure_edge_weight_constraint(cnode_initiator_MKNN_data, mean_diff)

                            #(structure_constraint, edge_weight_constraint) = cnode_data_merged.check_structure_edge_weight_constraint(cnode_initiator_MKNN_data, self.MEAN_DIFF)
                            print("structure constraint")
                            print(str(structure_constraint))
                            print("edge weight constraint")
                            print(str(edge_weight_constraint))
                            #structure_constraint = cnode_initiator_data.check_structure_constraint(cnode_initiator_MKNN_data)
                            #(edge_weight_constraint, low_high_flag) = cnode_initiator_data.check_edge_weight_constraint(cnode_initiator_MKNN_data)

                            if structure_constraint == 1 and edge_weight_constraint == 1:
                                #add_flag = 1
                                if self.check_initiator_MKNN_compatibility(cnode_initiator_MKNN_id, cnode_initiator_id) == True:
                                    add_flag = 1
                                    print("Merging")
                                else:
                                    cnode_initiator_data.boundary_cnode_dict_ycohesion_ysd_pp[cnode_initiator_MKNN_id] = periphery_score
                                    self.add_cnode_to_periphery_dict(cnode_initiator_MKNN_id, cnode_initiator_id, 'ycohesion_ysd_pp')
                                    print("Periphery ycohesion_ysd_pp")
                            elif structure_constraint == 1 and edge_weight_constraint != 1:


                                #Add MKNN cnode to class level periphery dict
                                if edge_weight_constraint == 2: #sd low

                                    #if self.check_initiator_MKNN_compatibility(cnode_initiator_MKNN_id, cnode_initiator_id) == True:
                                    #      add_flag = 1
                                    #else:
                                        self.add_cnode_to_periphery_dict(cnode_initiator_MKNN_id, cnode_initiator_id, 'ycohesion_nsd_low')
                                        #add cnode to boundary_cnode_set A
                                        cnode_initiator_data.boundary_cnode_dict_ycohesion_nsd_low[cnode_initiator_MKNN_id] = periphery_score
                                        print("Periphery ycohesion_nsd_low")

                                elif edge_weight_constraint == 3: # sd high
                                    self.add_cnode_to_periphery_dict(cnode_initiator_MKNN_id, cnode_initiator_id, 'ycohesion_nsd_high')
                                    #add cnode to boundary_cnode_set A
                                    cnode_initiator_data.boundary_cnode_dict_ycohesion_nsd_high[cnode_initiator_MKNN_id] = periphery_score
                                    print("Periphery ycohesion_nsd_high")

                            elif structure_constraint == 0 and edge_weight_constraint == 1:
                                #Add MKNN cnode to class level periphery dict
                                self.add_cnode_to_periphery_dict(cnode_initiator_MKNN_id, cnode_initiator_id, 'ncohesion_ysd')
                                #add cnode to boundary nodeset B
                                cnode_initiator_data.boundary_cnode_dict_ncohesion_ysd[cnode_initiator_MKNN_id] = periphery_score
                                print("Periphery ncohesion_ysd")

                            elif structure_constraint == 0 and edge_weight_constraint == 2:
                                #Add MKNN cnode to class level periphery dict
                                self.add_cnode_to_periphery_dict(cnode_initiator_MKNN_id, cnode_initiator_id, 'ncohesion_nsd_low')
                                #Add to boundary nodeset C
                                cnode_initiator_data.boundary_cnode_dict_ncohesion_nsd_low[cnode_initiator_MKNN_id] = periphery_score
                                print("Periphery ncohesion_nsd_low")
                            elif structure_constraint == 0 and edge_weight_constraint == 3:
                                #Add MKNN cnode to class level periphery dict
                                self.add_cnode_to_periphery_dict(cnode_initiator_MKNN_id, cnode_initiator_id, 'ncohesion_nsd_high')
                                #Add to boundary_nodeset D.
                                cnode_initiator_data.boundary_cnode_dict_ncohesion_nsd_high[cnode_initiator_MKNN_id] = periphery_score
                                print("Periphery ncohesion_nsd_high")

                            print("structure_constraint:")
                            print(str(structure_constraint))
                            print("edge weight constraint:")
                            print(str(edge_weight_constraint))

                            if add_flag == 1:
                                if clabel_current == -1:
                                    #Put initiator node in a new cluster as well
                                    clabel_current = self.next_cluster_label
                                    #self.next_cluster_label = self.next_cluster_label+1
                                    #self.num_clusters = self.num_clusters - 1

                                    #Create merger set
                                    cnode_merger_set.add(cnode_initiator_id)
                                    cnode_merger_set.add(cnode_initiator_MKNN_id)

                                    #Initialize a new cnode object for the merged cnode.
                                    cnode_data_merged = CNodeData_WI(clabel_current, -1, -1, -1, self.graphdata, self.configdata)

                                    self.merge_cnodes(cnode_merger_set, cnode_data_merged)

                                    #Add the new cnode object to cnodes_dict
                                    self.cnodes_dict[cnode_data_merged.cnode_id] = cnode_data_merged

                                    #Update clustering statisics on first merge with an MKNN neighbor.
                                    self.update_next_cluster_label()
                                    #print("Num clusters:")
                                    #print(self.num_clusters)
                                else:
                                    cnode_merger_set.add(cnode_initiator_MKNN_id)

                                    self.merge_cnodes(cnode_merger_set, cnode_data_merged)
                                #Put the neighbor node in the current cluster.
                                #Make a merged cnode with updated values.
                                #This includes updated CM values (explore).

                                cnode_merger_set = set()
                                print("Add flag is 1")

                    #Merge all cnodes in the cnode_merger_set together.
                    #cnode_data_merged = self.merge_cnodes(cnode_merger_set)

                    #After all K MKNNs have been added, check if cnode_
                    # initiator has any new boundary nodes
                    #to be added to cnode_data_merged.
                    if cnode_data_merged != None:
                        cnode_merger_set.add(cnode_initiator_id)
                        self.add_boundary_sets_to_merged_cnode(cnode_merger_set, cnode_data_merged)
                        cnode_merger_set = set()
                        cnode_data_merged = None

                    #update number of clusters
                    self.update_num_clusters()

            if prev_cluster_label == self.next_cluster_label:
                continueFlag = False


            if continueFlag == True:
                prev_cluster_label = self.next_cluster_label

                self.recalculate_matrices_for_Phase2_next_iteration()
            else:

                continueFlag = False
                break

            #If next_clusterLabel in previous iteration = next cluster label in current iteration:
            #end the loop, else
            #Recalculate cluster initiator order.
            #Recalculate MKNN neighbors for each node.

    #Method to add a cnode to periphery dict
    def add_cnode_to_periphery_dict(self, cnode_periphery_id, cnode_core_id, periphery_type):
        self.configdata.logger.debug("Debugging from inside add_cnode_to_periphery_dict"
                                     "method of class Phase2Data_WI.")
        if cnode_periphery_id not in self.periphery_dict:
            self.periphery_dict[cnode_periphery_id] = {'ycohesion_nsd_low' : set(), 'ycohesion_nsd_high' : set(), 'ncohesion_ysd' : set(), 'ncohesion_nsd_low' : set(), 'ncohesion_nsd_high' : set(), 'ycohesion_ysd_pp' : set()}

        self.periphery_dict[cnode_periphery_id][periphery_type].add(cnode_core_id)

    # #Method to add a node to periphery dict
    # def add_cnode_to_periphery_dict(self, cnode_periphery_id, cnode_core_set, periphery_type):
    #     self.configdata.logger.debug("Debugging from inside add_cnode_to_periphery_dict"
    #                                  "method of class Phase2Data_WI.")
    #     if cnode_periphery_id not in self.periphery_dict:
    #         self.periphery_dict[cnode_periphery_id] = {'ycohesion_nsd' : set(), 'ncohesion_ysd' : set(), 'ncohesion_nsd_low' : set(), 'ncohesion_nsd_high' : set()}
    #
    #     self.periphery_dict[cnode_periphery_id][periphery_type].update(cnode_core_set)

    #Method to check if the current MKNN is a core for the current initiator cnode.
    #Only Boundary sets ycohesion_nsd_low, ncohesion_ysd and ncohesion_nsd_low are used
    #for the check.
    def check_if_MKNN_core_of_initiator(self, cnode_MKNN_id, cnode_initiator_id):
        self.configdata.logger.debug("Debugging from inside check_if_MKNN_core_of_initiator method"
                                     "of class Phase2Data_WI.")
        cnode_MKNN_data = self.cnodes_dict[cnode_MKNN_id]
        if cnode_initiator_id in cnode_MKNN_data.boundary_cnode_dict_ycohesion_nsd_low or cnode_initiator_id in cnode_MKNN_data.boundary_cnode_dict_ncohesion_ysd or cnode_initiator_id in cnode_MKNN_data.boundary_cnode_dict_ncohesion_nsd_low:
            return True
        else:
            return False

    #Check if initiator/MKNN belong to periphery of some cores.
    #Merge them only if their core sets are exactly the same
    def check_initiator_MKNN_compatibility(self, cnode_MKNN_id, cnode_initiator_id):
        self.configdata.logger.debug("Debugging from inside check_periphery_for_core_membership"
                                 "method of class Phase2Data_WI.")
        # if cnode_initiator_id == 23:
        #     print('cnode id 23')

        if cnode_initiator_id not in self.periphery_dict:
            flag = True
        else:
            cnode_core_core_set = self.periphery_dict[cnode_initiator_id]['ycohesion_nsd_low'].union(self.periphery_dict[cnode_initiator_id]['ncohesion_ysd'].union(self.periphery_dict[cnode_initiator_id]['ncohesion_nsd_low']))
            # if cnode_initiator_id == 23:
            #     print("Cnode_core_core_set for cnodeid 23:")
            #     self.helper.print_set(cnode_core_core_set)


            if cnode_MKNN_id not in self.periphery_dict:
                flag = True
            else:
                cnode_MKNN_core_set = self.periphery_dict[cnode_MKNN_id]['ycohesion_nsd_low'].union(self.periphery_dict[cnode_MKNN_id]['ncohesion_ysd'].union(self.periphery_dict[cnode_MKNN_id]['ncohesion_nsd_low']))
                # if cnode_initiator_id == 23:
                #     print("MKNN core set:")
                #     self.helper.print_set(cnode_MKNN_core_set)

                intersection_set = cnode_core_core_set.intersection(cnode_MKNN_core_set)
                if intersection_set != None and len(intersection_set) == len(cnode_core_core_set) and len(intersection_set) == len(cnode_MKNN_core_set) :
                    flag = True
                else:
                    flag = False

        # if cnode_periphery_id in self.periphery_dict:
        #     if self.periphery_dict[cnode_periphery_id]['ycohesion_nsd'].contains(cnode_core_id) or
        #         self.periphery_dict[cnode_periphery_id]['ncohesion_ysd'].contains(cnode_core_id or
        #         self.periphery_dict[cnode_periphery_id]['ncohesion_nsd_low'].contains(cnode_core_id):
        #         flag = True
        #     else:
        #         flag = False
        # else:
        #     flag = True

        return flag


    #Recalculate matrices
    def recalculate_matrices_for_Phase2_next_iteration(self):
        self.configdata.logger.debug("Debugging from inside recalculate_matrices"
                                     "_for_Phase_next_iteration method of "
                                     "Phase2Data_WI class.")
        self.calculate_c_SM()
        self.sort_c_SM()
        self.initialize_MKNN_lists()
        self.calculate_cnode_MKNN()
        self.sort_cnodes_1()

    #Merge a set of cnodes into a new cnode.
    def merge_cnodes(self, merger_set, cnode_data_merged):
        self.configdata.logger.debug("Debugging from inside merge_cnodes method of Phase2Data_WI class.")
        #no merging needed for a single cnode.
        if(len(merger_set) >= 1):
            #create merged cnode
            self.create_merged_cnode(merger_set, cnode_data_merged)

            #No need to update phase 2 matrices here as all the mergings are taking place all at once.
            #self.update_phase2_matrices(merger_set, cnode_data_merged.cnode_id)

            #deactivate merging cnodes and remove them from self.cnodes_dict.
            self.deactivate_merging_cnodes(merger_set, cnode_data_merged.cnode_id)

            #Add the new cnode object to cnodes_dict
            #self.cnodes_dict[cnode_data_merged.cnode_id] = cnode_data_merged

            #self.update_clustering_statistics(len(merger_set))

    #Method to perform final steps after all K neighbors of a cluster initiator have merged.
    # def merge_cnodes_finish_K(self):
    #     self.configdata.logger.debug("Debugging from inside merge_cnodes_finish_K method of class Phase2Data_WI.")


    #Method to create a new cnode upon merging of cnodes in merger_set
    def create_merged_cnode(self, merger_set, cnode_data_merged):
        self.configdata.logger.debug("Debugging from inside create_merged_cnode method.")
        #Create a new cnode object
        #cluster_label_new = self.next_cluster_label
        #cluster_label_new = min(list(merger_set))

        #cnode_data_merged = CNodeData_WI(cluster_label_new, -1, -1, -1, self.graphdata, self.configdata)

       #Add the new cnode object to cnodes_dict
        #self.cnodes_dict[cluster_label_new] = cnode_data_merged

       #Add member cnodes to new cnode
        self.add_member_cnodes_to_merged_cnode(merger_set, cnode_data_merged)

       #Add nodes to new cnode
        self.add_nodes_to_merged_cnode(merger_set, cnode_data_merged)

        #Add edges to new cnode
        #primary
        self.add_edges_to_merged_cnode(merger_set, cnode_data_merged, EdgeType.primary)

        #secondary
        self.add_edges_to_merged_cnode(merger_set, cnode_data_merged, EdgeType.secondary)

        #Add the boundary sets from all merging cnodes
        #Also update self.periphery_dict
        self.add_boundary_sets_to_merged_cnode(merger_set, cnode_data_merged)

        #Run the clustering statistics for the new cnode
        #this also sets the active and dirty flags.
        cnode_data_merged.calculate_cnode_secondary_fields()

        return cnode_data_merged

    def update_phase2_matrices(self, merger_set, cnode_data_merged_id):
        pass

    #Method to deactivate the merging cnodes.
    def deactivate_merging_cnodes(self, merger_set, merged_cnode_id):
        for cnode_i in merger_set:
            cnode_data_i = self.cnodes_dict[cnode_i]
            cnode_data_i.cnode_GMKNN_clabel_dict[merged_cnode_id] = merged_cnode_id
            self.deactivate_cnode(cnode_data_i)

            #Remove cnode_i from cnodes_dict
            #del self.cnodes_dict[cnode_i]

    #Method to update clustering statistics after each merging in phase 2
    # def update_clustering_statistics(self):
    #     #self.num_clusters = self.num_clusters - size_set + 1
    #     self.num_clusters = self.calculate_number_of_active_clusters()
    #     self.next_cluster_label = self.next_cluster_label + 1
    #     print("Active cnodes after merging:")
    #     for cnode_i, cnode_data in self.cnodes_dict.items():
    #         if cnode_data.active == True:
    #             print(str(cnode_i))
    #             #self.cnode_id_map[cnode_id] = cnode_id

    def update_num_clusters(self):
        self.configdata.logger.debug("Debugging from inside update_num_clusters method of Phase2Data_WI class.")
        self.num_clusters = self.calculate_number_of_active_clusters()

    def update_next_cluster_label(self):
        self.configdata.logger.debug("Debugging from inside update_next_cluster_label method of Phase2Data_WI class.")
        self.next_cluster_label = self.next_cluster_label + 1

    def calculate_number_of_active_clusters(self):
        num_clusters = 0
        for cnode_i, cnode_data in self.cnodes_dict.items():
            if cnode_data.active == True:
                num_clusters = num_clusters + 1
        return num_clusters

    #Method to add member cnodes to merged cnode
    def add_member_cnodes_to_merged_cnode(self, merger_set, cnode_data_merged):
        self.configdata.logger.debug("Debugging from inside add_member_cnodes_to_"
                                     "merged_cnode method of Phase2Data_WI class.")
        cluster_label_new = cnode_data_merged.cnode_id
        for cnode_i in merger_set:
            cnode_data_i = self.cnodes_dict[cnode_i]

            #Add merging cnode to the new cluster's member cnode set
            cnode_data_merged.member_cnode_set.add(cnode_i)
            cnode_data_merged.member_cnode_set.update(cnode_data_i.member_cnode_set)

            #Add new cluster label as merging cnode's cnode_clabel
            cnode_data_i.cnode_GMKNN_clabel_dict[cluster_label_new] = cluster_label_new
            for cnode_member_i in cnode_data_i.member_cnode_set:
                cnode_member_data_i = self.cnodes_dict[cnode_member_i]
                cnode_member_data_i.cnode_GMKNN_clabel_dict[cluster_label_new] = cluster_label_new

    #Method to add nodes to merged cnode
    def add_nodes_to_merged_cnode(self, merger_set, cnode_data_merged):
        self.configdata.logger.debug("Debugging from inside add_nodes_to_merged_cnod"
                                     "e method of Phase2Data_WI class.")
        #cnode_data_merged = self.cnodes_dict[cluster_label_new]
        print("merger_set")
        self.helper.print_set(merger_set)
        print("Merged cnode id:")
        print(str(cnode_data_merged.cnode_id))
        cluster_label_new = cnode_data_merged.cnode_id
        for cnode_i in merger_set:
            cnode_data_i = self.cnodes_dict[cnode_i]
            cnode_data_merged.node_set = cnode_data_merged.node_set | cnode_data_i.node_set
           #Update cluster membership of each node in the new nodeset
            for node_id in cnode_data_i.node_set:
                node = self.graphdata.node_dict[node_id]
                # print("GMKNN clabel dict:")
                # self.helper.print_dict(node.GMKNN_clabel_dict)
                # print("cnode_id:")
                # print(cnode_i)
                #del node.GMKNN_clabel_dict[cnode_i]
                node.GMKNN_clabel_dict[cluster_label_new] = cnode_i
                          #For each node (in phase 2), now the cluster center
                          #holds the cnode_id they come from in the big merged
                          #cnode. In phase 2, it was holding the actual cluster
                          #center node_id.

    #Method to add edges to merged cnode
    def add_edges_to_merged_cnode(self, merger_set, cnode_data_merged, edge_type):
        self.configdata.logger.debug("Debugging from inside add_edges_to_merged_cnode method of Phase2Data_WI class.")
        #cnode_data_merged = self.cnodes_dict[cluster_label_new]
        cluster_label_new = cnode_data_merged.cnode_id
        other_set = merger_set.copy()
        temp_set = set()
        for cnode_i in merger_set:
            cnode_data_i = self.cnodes_dict[cnode_i]
            cnode_data_merged.internal_edge_dict[edge_type].update(cnode_data_i.internal_edge_dict[edge_type])
            cnode_data_merged.external_edge_dict[edge_type].update(cnode_data_i.external_edge_dict[edge_type])

            other_set.discard(cnode_i)
            for cnode_j in other_set:
                cnode_data_j = self.cnodes_dict[cnode_j]
                temp_set = temp_set | self.get_edgeset_between_cnodes(cnode_data_i, cnode_data_j, EdgeType.primary)

        cnode_data_merged.internal_edge_dict[edge_type].update(temp_set)
        cnode_data_merged.external_edge_dict[edge_type].difference_update(temp_set)

    #method to add boundary sets to the merged cnode
    def add_boundary_sets_to_merged_cnode(self, merger_set, cnode_data_merged):
        self.configdata.logger.debug("Debugging from inside add_boundary_sets_to_merged_cnode method of Phase2Data_WI class.")
        for cnode_i in merger_set:
            cnode_data_i = self.cnodes_dict[cnode_i]

            #Add merged cnode to class level periphery dict
            #if any of the member cnodes belong there (that is
            #they are peripheries to some core)
            if cnode_i in self.periphery_dict:
                self.add_merged_cnode_to_periphery_dict(cnode_i, cnode_data_merged.cnode_id, 'ycohesion_nsd_low')
                self.add_merged_cnode_to_periphery_dict(cnode_i, cnode_data_merged.cnode_id, 'ycohesion_nsd_high')
                self.add_merged_cnode_to_periphery_dict(cnode_i, cnode_data_merged.cnode_id, 'ncohesion_ysd')
                self.add_merged_cnode_to_periphery_dict(cnode_i, cnode_data_merged.cnode_id, 'ncohesion_nsd_low')
                self.add_merged_cnode_to_periphery_dict(cnode_i, cnode_data_merged.cnode_id, 'ncohesion_nsd_high')
                self.add_merged_cnode_to_periphery_dict(cnode_i, cnode_data_merged.cnode_id, 'ycohesion_ysd_pp')

            #1. Propogate member cnode's boundary nodes to merged cnode's boundary cnodes.
            #2. If member cnodes are cores for any peripheries, add those periphery to merged
            #cnode relationship in class level periphery dict
            for periphery_cnode_id, score in cnode_data_i.boundary_cnode_dict_ycohesion_nsd_low.items():
                cnode_data_merged.boundary_cnode_dict_ycohesion_nsd_low[periphery_cnode_id] = score
                self.add_cnode_to_periphery_dict(periphery_cnode_id, cnode_data_merged.cnode_id, 'ycohesion_nsd_low')

            for periphery_cnode_id, score in cnode_data_i.boundary_cnode_dict_ycohesion_nsd_high.items():
                cnode_data_merged.boundary_cnode_dict_ycohesion_nsd_high[periphery_cnode_id] = score
                self.add_cnode_to_periphery_dict(periphery_cnode_id, cnode_data_merged.cnode_id, 'ycohesion_nsd_high')

            for periphery_cnode_id, score in cnode_data_i.boundary_cnode_dict_ncohesion_ysd.items():
                cnode_data_merged.boundary_cnode_dict_ncohesion_ysd[periphery_cnode_id] = score
                self.add_cnode_to_periphery_dict(periphery_cnode_id, cnode_data_merged.cnode_id, 'ncohesion_ysd')

            for periphery_cnode_id, score in cnode_data_i.boundary_cnode_dict_ncohesion_nsd_low.items():
                cnode_data_merged.boundary_cnode_dict_ncohesion_nsd_low[periphery_cnode_id] = score
                self.add_cnode_to_periphery_dict(periphery_cnode_id, cnode_data_merged.cnode_id, 'ncohesion_nsd_low')

            for periphery_cnode_id, score in cnode_data_i.boundary_cnode_dict_ncohesion_nsd_high.items():
                cnode_data_merged.boundary_cnode_dict_ncohesion_nsd_high[periphery_cnode_id] = score
                self.add_cnode_to_periphery_dict(periphery_cnode_id, cnode_data_merged.cnode_id, 'ncohesion_nsd_high')

            for periphery_cnode_id, score in cnode_data_i.boundary_cnode_dict_ycohesion_ysd_pp.items():
                cnode_data_merged.boundary_cnode_dict_ncohesion_nsd_high[periphery_cnode_id] = score
                self.add_cnode_to_periphery_dict(periphery_cnode_id, cnode_data_merged.cnode_id, 'ycohesion_ysd_pp')


    #Method to add merged cnode to class level periphery dict
    def add_merged_cnode_to_periphery_dict(self, cnode_member_id, cnode_merged_id, periphery_type):
        self.configdata.logger.debug("Debugging from inside add_merged_cnode_to_periphery_dict method"
                                     "of class Phase2Data_WI.")
        cnode_core_set = self.periphery_dict[cnode_member_id][periphery_type]
        #self.add_cnode_to_periphery_dict(cnode_merged_id, cnode_core_set, periphery_type)
        for cnode_core_id in cnode_core_set:
            self.add_cnode_to_periphery_dict(cnode_merged_id, cnode_core_id, periphery_type)


            # cnode_periphery_dict_i = cnode_data_i.periphery_cnode_dict
            #
            # for periphery_cnode_id, relationship_score in cnode_periphery_dict_i.items():
            #     if periphery_cnode_id not in cnode_data_merged.periphery_cnode_dict:
            #         cnode_data_merged.periphery_cnode_dict[periphery_cnode_id] = relationship_score
            #     else:
            #         cnode_data_merged_relationship_score = cnode_data_merged.periphery_cnode_dict[periphery_cnode_id]
            #         cnode_data_merged_relationship_score.typeA_score += relationship_score.typeA_score
            #         cnode_data_merged_relationship_score.typeB_score += relationship_score.typeB_score
            #         cnode_data_merged.relationship_score.typeC_score += relationship_score.typeC_score
            #         cnode_data_merged.relationship_score.typeD_score += relationship_score.typeD_score

    # #Method to add a boundary dict to the merged cnode
    # def add_boundary_set_to_merged_cnode(self, boundary_dict, cnode_data_merged):
    #     self.configdata.logger.debug("Debugging from inside add_boundary_set_merged_cnode method of Phase2Data_WI class.")
    #
    #     for periphery_cnode_id, score in boundary_dict.items():
    #         cnode_data_merged.boundary_cnode_dict_ycohesion_nsd[periphery_cnode_id] = score


    # #Method to update phase 2 matrices upon creation of a merged cnode
    # def update_phase2_matrices(self, merger_set, cluster_label_new):
    #     #************************
    #     #Update Matrices
    #     #************************
    #     cnode_merged_data = self.cnodes_dict[cluster_label_new]
    #     if(cnode_merged_data.isDirty == True):
    #         cnode_merged_data.calculate_cnode_secondary_fields()
    #
    #     #Update ProjectionM and OutreachM and CM
    #     projection_new_row = []
    #     #projection_new_column = []
    #
    #     outreach_new_row = []
    #
    #     CM_new_row = []
    #
    #     #print("Shape c-SM before phase 2 execute loop starts")
    #     #print(np.shape(np.array(self.c_SM)))
    #     #Update value of projection, outreach and CM for each currently existing cluster
    #     for cnode_current_id in range(0, len(self.c_SM)):
    #         cnode_current_data = self.cnodes_dict[cnode_current_id]
    #         #num_nodes_current_cluster = NumNodesM_List[current_cluster_no][0]
    #
    #         if(cnode_current_data.active == True):
    #             if(cnode_current_data.isDirty == True):
    #                 cnode_current_data.calculate_cnode_secondary_fields()
    #
    #
    #             ##############################################
    #             #Updates for Projection List (Inside the loop)
    #             #############################################
    #
    #             #Create a new row for new cluster label and for column: current cluster label
    #             #This new row will be fully built first in the loop and then added as a whole outside the loop.
    #             #A special case: Merged cluster's Projection value with cluster label 1 and cluster label 2 to
    #             # be set to 0 manually.
    #             projection_new_row_value = self.projectionM[cnode_id_1][cnode_current_id] + self.projectionM[cnode_id_2][cnode_current_id]
    #             if projection_new_row_value < 0 or cnode_current_id == cnode_id_1 or cnode_current_id == cnode_id_2:
    #                 projection_new_row_value = -1
    #
    #             projection_new_row.append(projection_new_row_value)
    #             #projection_new_column.append(ProjectionM_List[current_cluster_no][cluster_label_1] + ProjectionM_List[current_cluster_no][cluster_label_2])
    #
    #             #Add new projection value in the new column for new cluster label and row: current_cluster_label
    #             #This new column. row value will be added in the for loop one by one.
    #             projection_new_column_value = self.projectionM[cnode_current_id][cnode_id_1] + self.projectionM[cnode_current_id][cnode_id_2]
    #             if projection_new_column_value < 0 or cnode_current_id == cnode_id_1 or cnode_current_id == cnode_id_2:
    #                 projection_new_column_value = -1
    #
    #             self.projectionM[cnode_current_id].append(projection_new_column_value)
    #
    #
    #             ############################################
    #             #Updates for Outreach List (Inside the loop)
    #             ############################################
    #             #Calculate the new outreach value between the current cluster and the new cluster
    #             #A special case: Outreach value between new cluster and cluster label 1 and
    #             #cluster label 2 needs to be set manually= -1
    #             outreach_new_value = self.outreachM[cnode_id_1][cnode_current_id] + self.outreachM[cnode_id_2][cnode_current_id]
    #
    #             if outreach_new_value < 0 or cnode_current_id == cnode_id_1 or cnode_current_id == cnode_id_2:
    #                 outreach_new_value = -1
    #
    #             outreach_new_row.append(outreach_new_value)
    #             self.outreachM[cnode_current_id].append(outreach_new_value)
    #
    #             ###############################################
    #             #Updates for CM List (Inside the loop)
    #             ###############################################
    #             if outreach_new_value == -1 or projection_new_row_value == -1:
    #                 CM_new_row_value = -1
    #             else:
    #                 CM_new_row_value = (outreach_new_value * projection_new_row_value)/(((float)(cnode_merged_data.num_nodes * (float)(cnode_merged_data.num_nodes) * (float) (cnode_current_data.num_nodes))))
    #
    #             if outreach_new_value == -1 or projection_new_column_value == -1:
    #                 CM_new_column_value = -1
    #             else:
    #                 CM_new_column_value = (outreach_new_value * projection_new_column_value)/ ((float) (cnode_current_data.num_nodes * cnode_current_data.num_nodes * cnode_merged_data.num_nodes))
    #
    #             CM_new_row.append(CM_new_row_value)
    #             self.c_SM[cnode_current_id].append(CM_new_column_value)
    #
    #         elif(cnode_current_data.active == False):
    #             #The current cnode is not active
    #             #most probably because it has already merged to form
    #             #some new cnode.
    #
    #             projection_new_row_value = -1
    #             projection_new_row.append(projection_new_row_value)
    #             projection_new_column_value = -1
    #             self.projectionM[cnode_current_id].append(projection_new_column_value)
    #
    #             outreach_new_value = -1
    #             outreach_new_row.append(outreach_new_value)
    #             self.outreachM[cnode_current_id].append(outreach_new_value)
    #
    #             CM_new_row_value = -1
    #             CM_new_column_value = -1
    #             CM_new_row.append(CM_new_row_value)
    #             self.c_SM[cnode_current_id].append(CM_new_column_value)
    #
    #
    #
    #         #Nullify values for matrices for cnode_id_1 and cnode_id_2
    #         #with all other cnodes as the new merged cnode represents them
    #         #both now
    #         self.projectionM[cnode_id_1][cnode_current_id] = -1
    #         self.projectionM[cnode_id_2][cnode_current_id] = -1
    #         self.projectionM[cnode_current_id][cnode_id_1] = -1
    #         self.projectionM[cnode_current_id][cnode_id_2] = -1
    #
    #         self.outreachM[cnode_id_1][cnode_current_id] = -1
    #         self.outreachM[cnode_id_2][cnode_current_id] = -1
    #         self.outreachM[cnode_current_id][cnode_id_1] = -1
    #         self.outreachM[cnode_current_id][cnode_id_2] = -1
    #
    #         self.c_SM[cnode_id_1][cnode_current_id] = -1
    #         self.c_SM[cnode_id_2][cnode_current_id] = -1
    #         self.c_SM[cnode_current_id][cnode_id_1] = -1
    #         self.c_SM[cnode_current_id][cnode_id_2] = -1
    #
    #
    #     ###############################################
    #     #Updates for Projection List (Outside the loop)
    #     ###############################################
    #
    #     projection_new_row.append(-1) #Projection of new cluster with self = -1
    #     #Add the row for the new cluster to ProjectionM
    #     self.projectionM.append(projection_new_row)
    #
    #
    #     ###############################################
    #     #Updates for Outreach List (Outside the loop)
    #     ###############################################
    #     outreach_new_row.append(-1) #Outreach of new cluster with itself
    #     #Add the new row for the new cluster to OutreachM
    #     self.outreachM.append(outreach_new_row)
    #
    #     #############################################
    #     #Updates for CM (Outside the loop)
    #     #############################################
    #     CM_new_row.append(-1)
    #     #Add the row for the new cluster to CM
    #     self.c_SM.append(CM_new_row)


    #Method to calculate the overlap matrix
    def calculate_overlap_matrix(self):
        self.configdata.logger.debug("Debugging from inside calculate_overlap_matrix method.")

        #initialize c_SM
        self.c_OM = [[-1] * self.num_clusters for i in range(self.num_clusters)]
        om_i = 0
        om_j = 0
        for i in range(0, self.next_cluster_label):
            cnode_i = self.cnodes_dict[i]
            if cnode_i.active == True:
                if cnode_i.isDirty == True:
                    cnode_i.calculate_cnode_secondary_fields()
                om_j = om_i + 1
                if i != self.next_cluster_label:
                    for j in range(i+1, self.next_cluster_label):
                        cnode_j = self.cnodes_dict[j]

                        if cnode_j.active == True:

                            if cnode_j.isDirty == True:
                                cnode_j.calculate_cnode_secondary_fields()


                            overlapij_numerator = (float) ((len(cnode_i.node_set.intersection(cnode_j.node_set)))*(len(cnode_i.node_set.intersection(cnode_j.node_set))))
                            overlapij_denominator = (float)(cnode_i.num_nodes * cnode_j.num_nodes)
                            self.c_OM[om_i][om_j] = overlapij_numerator/overlapij_denominator
                            self.c_OM[om_j][om_i] = self.c_OM[om_i][om_j]
                            om_j = om_j + 1
                    om_i = om_i + 1


    def MKNN_phase2_overlap(self):
        self.configdata.logger.debug("Debugging from inside MKNN_phase2_overlap"
                                     "method of class Phase2Data_WI.")

        flag_merge = False

        #Calculate overlap matrix
        self.calculate_overlap_matrix()

        #Create a dictionary of sets containing set of cnodes to be
        #merged together based upon the overlap matrix.
        sets_dict = self.create_merger_set_dict()

        #merge the cnodes in the sets defined by sets_dict
        #all at once.

        for set_num, merger_set in sets_dict.items():
            if len(merger_set) > 1:
                #print("set number")
                #print(str(set_num))
                #print("merger sets")
                #Initialize a new cnode object for the merged cnode.
                flag_merge = True
                cnode_data_merged = CNodeData_WI(self.next_cluster_label, -1, -1, -1, self.graphdata, self.configdata)

                self.merge_cnodes(merger_set, cnode_data_merged)

                #Add the new cnode object to cnodes_dict
                self.cnodes_dict[cnode_data_merged.cnode_id] = cnode_data_merged

                #Update clustering statisics on first merge with an MKNN neighbor.
                self.update_next_cluster_label()

                #Update the number of clusters
                self.update_num_clusters()
                #
                # for cnode_i in merger_set:
                #     print(str(cnode_i))

        if flag_merge == True:
            self.recalculate_matrices_for_Phase2_next_iteration()

    #Method to create a dictionary of sets containing
    #set of cnodes to be merged together based upon
    # the overlap matrix.
    def create_merger_set_dict(self):
        self.configdata.logger.debug("Debugging from inside "
                                     "create_merger_set_dict "
                                     "method of Phase2Data_WI class.")
        membership_dict = {}
        sets_dict = {}
        next_available_set_num = 0
        set_i = -1
        for i in range(0, self.num_clusters):
            cnode_i = self.cnode_id_map[i]
            #Decide self set membership of cnode_i
            if(cnode_i in membership_dict):
                #Get the set to which node_i currently belongs to
                set_i = membership_dict[cnode_i]
            else:
                membership_dict[cnode_i] = next_available_set_num
                set_i = next_available_set_num
                merger_sets = set()
                merger_sets.add(cnode_i)
                sets_dict[set_i] = merger_sets
                next_available_set_num = next_available_set_num + 1

            #Based upon self set membership,
            #update the set membership of all its cnode neighbors
            #where overlap>=0.8
            for j in range(0, self.num_clusters):
                cnode_j = self.cnode_id_map[j]
                if(i != j and self.c_OM[i][j] >= self.OVERLAP_THRESHOLD):
                    if(cnode_j in membership_dict):
                        set_j = membership_dict[cnode_j]
                        if set_i != set_j:
                            merger_sets_j = sets_dict[set_j]
                            for cnode_k in merger_sets_j:
                                membership_dict[cnode_k] = set_i
                                #merge set_j into set_i
                                sets_dict[set_i].add(cnode_k)
                            #merge set_j into set_i
                            #set_i = set_i.union(set_j)
                            del sets_dict[set_j]
                    else:
                        membership_dict[cnode_j] = set_i
                        sets_dict[set_i].add(cnode_j)

        return sets_dict

    #Method to extract core periphery relationships
    def extract_core_periphery_relationships(self):
        self.configdata.logger.debug("Debugging from inside extract_core_"
                                     "periphery_relationships method of "
                                     "Phase2Data_WI class.")
        for cnode_id, cnode_data in self.cnodes_dict.items():
            if cnode_data.active == True:
                self.extract_core_periphery_relationships_typeA(cnode_data) #ycohesion_nsd_low
                self.extract_core_periphery_relationships_typeB(cnode_data) #ncohesion_ysd
                self.extract_core_periphery_relationships_typeC(cnode_data) #ncohesion_nsd_low
                self.extract_core_periphery_relationships_typeD(cnode_data) #ncohesion_nsd_high
                self.extract_core_periphery_relationships_typeE(cnode_data) #periphery-periphery relationship
                self.extract_core_periphery_relationships_typeF(cnode_data) #ycohesion_nsd_high

    #Method to extract core periphery relationships of Type A
    #ycohesion nsd_low
    def extract_core_periphery_relationships_typeA(self, cnode_data):
        self.configdata.logger.debug("Debugging from inside extract_core_periphery_relationships_typeA"
                                     "of Phase2Data_WI class.")
        for boundary_cnode_id, boundary_score in cnode_data.boundary_cnode_dict_ycohesion_nsd_low.items():

            if self.cnodes_dict[boundary_cnode_id].active == True:
                self.add_boundary_cnode_to_periphery(boundary_cnode_id, cnode_data, 'A')
            else:
                all_boundary_cnode_set = set(self.cnodes_dict[boundary_cnode_id].cnode_GMKNN_clabel_dict.keys())
                for all_boundary_cnode_id in all_boundary_cnode_set:
                    if self.cnodes_dict[all_boundary_cnode_id].active == True:
                        self.add_boundary_cnode_to_periphery(all_boundary_cnode_id, cnode_data, 'A')
                        # if cnode_cnode_id in cnode_data.periphery_cnode_dict:
                        #     cnode_relationship_score = cnode_data.periphery_cnode_dict[cnode_cnode_id]
                        # else:
                        #     cnode_relationship_score = CNodeRelationshipScore()
                        #     cnode_data.periphery_cnode_dict[cnode_cnode_id] = cnode_relationship_score
                        #
                        # #cnode_relationship_score.typeA_score = cnode_relationship_score.typeA_score + boundary_score
                        # cnode_relationship_score.typeA_score = cnode_relationship_score.typeA_score + 1


    #Method to extract core periphery relationships of Type F
    #ycohesion nsd_high
    def extract_core_periphery_relationships_typeF(self, cnode_data):
        self.configdata.logger.debug("Debugging from inside extract_core_periphery_relationships_typeF"
                                     "of Phase2Data_WI class.")
        for boundary_cnode_id, boundary_score in cnode_data.boundary_cnode_dict_ycohesion_nsd_high.items():
            if self.cnodes_dict[boundary_cnode_id].active == True:
                self.add_boundary_cnode_to_periphery(boundary_cnode_id, cnode_data, 'F')
            else:
                all_boundary_cnode_set = set(self.cnodes_dict[boundary_cnode_id].cnode_GMKNN_clabel_dict.keys())
                for all_boundary_cnode_id in all_boundary_cnode_set:
                    if self.cnodes_dict[all_boundary_cnode_id].active == True:
                        self.add_boundary_cnode_to_periphery(all_boundary_cnode_id, cnode_data, 'F')
                        # if cnode_cnode_id in cnode_data.periphery_cnode_dict:
                        #     cnode_relationship_score = cnode_data.periphery_cnode_dict[cnode_cnode_id]
                        # else:
                        #     cnode_relationship_score = CNodeRelationshipScore()
                        #     cnode_data.periphery_cnode_dict[cnode_cnode_id] = cnode_relationship_score
                        #
                        # #cnode_relationship_score.typeA_score = cnode_relationship_score.typeA_score + boundary_score
                        # cnode_relationship_score.typeA_score = cnode_relationship_score.typeA_score + 1

    #Method to extract core periphery relationships of Type B
    #ncohesion ysd
    def extract_core_periphery_relationships_typeB(self, cnode_data):
        self.configdata.logger.debug("Debugging from inside extract_core_periphery_relationships_typeB"
                                     "of Phase2Data_WI class.")

        for boundary_cnode_id, boundary_score in cnode_data.boundary_cnode_dict_ncohesion_ysd.items():
            if self.cnodes_dict[boundary_cnode_id].active == True:
                self.add_boundary_cnode_to_periphery(boundary_cnode_id, cnode_data, 'B')
            else:
                all_boundary_cnode_set = set(self.cnodes_dict[boundary_cnode_id].cnode_GMKNN_clabel_dict.keys())
                for all_boundary_cnode_id in all_boundary_cnode_set:
                    if self.cnodes_dict[all_boundary_cnode_id].active == True:
                        self.add_boundary_cnode_to_periphery(all_boundary_cnode_id, cnode_data, 'B')


        #
        # for cnode_id, boundary_score in cnode_data.boundary_cnode_dict_ncohesion_ysd.items():
        #     cnode_cnode_id_set = set(self.cnodes_dict[cnode_id].cnode_GMKNN_clabel_dict.keys())
        #     for cnode_cnode_id in cnode_cnode_id_set:
        #         if self.cnodes_dict[cnode_cnode_id].active == True:
        #             if cnode_cnode_id in cnode_data.periphery_cnode_dict:
        #                 cnode_relationship_score = cnode_data.periphery_cnode_dict[cnode_cnode_id]
        #             else:
        #                 cnode_relationship_score = CNodeRelationshipScore()
        #                 cnode_data.periphery_cnode_dict[cnode_cnode_id] = cnode_relationship_score
        #
        #             #cnode_relationship_score.typeB_score = cnode_relationship_score.typeB_score + boundary_score
        #             cnode_relationship_score.typeB_score = cnode_relationship_score.typeB_score + 1



    #Method to extract core periphery relationships of Type C
    #ncohesion nsd low
    def extract_core_periphery_relationships_typeC(self, cnode_data):
        self.configdata.logger.debug("Debugging from inside extract_core_periphery_relationships_typeC")

        for boundary_cnode_id, boundary_score in cnode_data.boundary_cnode_dict_ncohesion_nsd_low.items():
            if self.cnodes_dict[boundary_cnode_id].active == True:
                self.add_boundary_cnode_to_periphery(boundary_cnode_id, cnode_data, 'C')
            else:
                all_boundary_cnode_set = set(self.cnodes_dict[boundary_cnode_id].cnode_GMKNN_clabel_dict.keys())
                for all_boundary_cnode_id in all_boundary_cnode_set:
                    if self.cnodes_dict[all_boundary_cnode_id].active == True:
                        self.add_boundary_cnode_to_periphery(all_boundary_cnode_id, cnode_data, 'C')


        #
        # for cnode_id, boundary_score in cnode_data.boundary_cnode_dict_ncohesion_nsd_low.items():
        #     cnode_cnode_id_set = set(self.cnodes_dict[cnode_id].cnode_GMKNN_clabel_dict.keys())
        #     for cnode_cnode_id in cnode_cnode_id_set:
        #         if self.cnodes_dict[cnode_cnode_id].active == True:
        #             if cnode_cnode_id in cnode_data.periphery_cnode_dict:
        #                 cnode_relationship_score = cnode_data.periphery_cnode_dict[cnode_cnode_id]
        #             else:
        #                 cnode_relationship_score = CNodeRelationshipScore()
        #                 cnode_data.periphery_cnode_dict[cnode_cnode_id] = cnode_relationship_score
        #
        #             #cnode_relationship_score.typeC_score = cnode_relationship_score.typeC_score + boundary_score
        #             cnode_relationship_score.typeC_score = cnode_relationship_score.typeC_score + 1


    #Method to extract core periphery relationships of Type D
    #ncohesion nsd high
    def extract_core_periphery_relationships_typeD(self, cnode_data):
        self.configdata.logger.debug("Debugging from inside extract_core_periphery_relationships_typeD")

        for boundary_cnode_id, boundary_score in cnode_data.boundary_cnode_dict_ncohesion_nsd_high.items():
            if self.cnodes_dict[boundary_cnode_id].active == True:
                self.add_boundary_cnode_to_periphery(boundary_cnode_id, cnode_data, 'D')
            else:
                all_boundary_cnode_set = set(self.cnodes_dict[boundary_cnode_id].cnode_GMKNN_clabel_dict.keys())
                for all_boundary_cnode_id in all_boundary_cnode_set:
                    if self.cnodes_dict[all_boundary_cnode_id].active == True:
                        self.add_boundary_cnode_to_periphery(all_boundary_cnode_id, cnode_data, 'D')

        #
        # for cnode_id, boundary_score in cnode_data.boundary_cnode_dict_ncohesion_nsd_high.items():
        #     cnode_cnode_id_set = set(self.cnodes_dict[cnode_id].cnode_GMKNN_clabel_dict.keys())
        #     for cnode_cnode_id in cnode_cnode_id_set:
        #         if self.cnodes_dict[cnode_cnode_id].active == True:
        #             if cnode_cnode_id in cnode_data.periphery_cnode_dict:
        #                 cnode_relationship_score = cnode_data.periphery_cnode_dict[cnode_cnode_id]
        #             else:
        #                 cnode_relationship_score = CNodeRelationshipScore()
        #                 cnode_data.periphery_cnode_dict[cnode_cnode_id] = cnode_relationship_score
        #
        #             #cnode_relationship_score.typeD_score = cnode_relationship_score.typeD_score + boundary_score
        #             cnode_relationship_score.typeD_score = cnode_relationship_score.typeD_score + 1

    #Method to extract core periphery relationships of Type E
    #ycohesion ysd_pp
    def extract_core_periphery_relationships_typeE(self, cnode_data):
        self.configdata.logger.debug("Debugging from inside extract_core_periphery_relationships_typeE"
                                     "of Phase2Data_WI class.")

        for boundary_cnode_id, boundary_score in cnode_data.boundary_cnode_dict_ycohesion_ysd_pp.items():
            if self.cnodes_dict[boundary_cnode_id].active == True:
                self.add_boundary_cnode_to_periphery(boundary_cnode_id, cnode_data, 'E')
            else:
                all_boundary_cnode_set = set(self.cnodes_dict[boundary_cnode_id].cnode_GMKNN_clabel_dict.keys())
                for all_boundary_cnode_id in all_boundary_cnode_set:
                    if self.cnodes_dict[all_boundary_cnode_id].active == True:
                        self.add_boundary_cnode_to_periphery(all_boundary_cnode_id, cnode_data, 'E')



    #Add a boundary cnode to periphery of core cnode
    def add_boundary_cnode_to_periphery(self, boundary_cnode_id, cnode_data, type):
        self.configdata.logger.debug("Debugging from inside add_boundary_cnode_to_periphery method of"
                                     "class Phase2Data_WI.")
        if boundary_cnode_id in cnode_data.periphery_cnode_dict:
            cnode_relationship_score = cnode_data.periphery_cnode_dict[boundary_cnode_id]
        else:
            cnode_relationship_score = CNodeRelationshipScore()
            cnode_data.periphery_cnode_dict[boundary_cnode_id] = cnode_relationship_score

        #cnode_relationship_score.typeA_score = cnode_relationship_score.typeA_score + boundary_score
        if type == 'A':
            cnode_relationship_score.typeA_score = cnode_relationship_score.typeA_score + 1
        elif type == 'B':
            cnode_relationship_score.typeB_score = cnode_relationship_score.typeB_score + 1
        elif type == 'C':
            cnode_relationship_score.typeC_score = cnode_relationship_score.typeC_score + 1
        elif type == 'D':
            cnode_relationship_score.typeD_score = cnode_relationship_score.typeD_score + 1
        elif type == 'E':
            cnode_relationship_score.typeE_score = cnode_relationship_score.typeE_score + 1
        elif type == 'F':
            cnode_relationship_score.typeF_score = cnode_relationship_score.typeF_score + 1


    #Method to extract core periphery relationships
    def extract_global_core_periphery_relationships(self):
        self.configdata.logger.debug("Debugging from inside extract_core_periphery_relations method of Phase2Data_WI class.")
        #Order cnodes as per cohesion (This is already present as cluster initiator order.,
        #Extract core periphery relationships for boundary cnodesets type A, B and C in this order.
        #print("Inside extract global core periphery relationships.")
        for i in range(self.num_clusters):
            cnode_id = self.cnode_cluster_initiator_list[self.num_clusters - i - 1]
            cnode_data = self.cnodes_dict[cnode_id]
            # print("Cnode id:")
            # print(str(cnode_id))
            # print("No. of peripheries")
            # print(str(len(cnode_data.periphery_cnode_dict.keys())))
            for periphery_cnode_id, relationship_score in cnode_data.periphery_cnode_dict.items():

                if self.cnode_relationship_dict.contains_relationship(cnode_id, periphery_cnode_id):
                    pass
                else:
                    relationship_score.classify_periphery_cnode_type()


                    if relationship_score.aggregate_type == "A":
                        #if self.cnode_cluster_initiator_list.index(periphery_cnode_id) > self.cnode_cluster_initiator_list.index(cnode_id):
                        if cnode_data.mean_edges > self.cnodes_dict[periphery_cnode_id].mean_edges:
                            print("CP type A found")
                            print("Core")
                            print(str(cnode_id))
                            print("Periphery")
                            print((str(periphery_cnode_id)))

                            self.calculate_relationship_scores(relationship_score, cnode_id, periphery_cnode_id)

                            cnode_data.set_cnode_CP_status(ClusterStatus.core)
                            self.cnodes_dict[periphery_cnode_id].set_cnode_CP_status(ClusterStatus.periphery)

                            cnode_relationship = CNodeRelationship(cnode_id, periphery_cnode_id, CNodeRelationshipType.core_periphery, relationship_score)
                            self.cnode_relationship_dict.put_relationship_object(cnode_id, periphery_cnode_id, cnode_relationship)

                    elif relationship_score.aggregate_type == "C":
                        #if self.cnode_cluster_initiator_list.index(periphery_cnode_id) > self.cnode_cluster_initiator_list.index(cnode_id):
                        if cnode_data.mean_edges > self.cnodes_dict[periphery_cnode_id].mean_edges:
                            print("CP type C found")
                            print("Core")
                            print(str(cnode_id))
                            print("Periphery")
                            print((str(periphery_cnode_id)))

                            self.calculate_relationship_scores(relationship_score, cnode_id, periphery_cnode_id)

                            cnode_data.set_cnode_CP_status(ClusterStatus.core)
                            self.cnodes_dict[periphery_cnode_id].set_cnode_CP_status(ClusterStatus.periphery)

                            cnode_relationship = CNodeRelationship(cnode_id, periphery_cnode_id, CNodeRelationshipType.core_periphery, relationship_score)
                            self.cnode_relationship_dict.put_relationship_object(cnode_id, periphery_cnode_id, cnode_relationship)

                    elif relationship_score.aggregate_type == "B":

                        #Check for the possibility of a type C relationship
                        if self.cnodes_dict[periphery_cnode_id].num_nodes != 1 and cnode_data.num_nodes != 1 and abs(self.cnodes_dict[periphery_cnode_id].mean_edges - cnode_data.mean_edges) >= self.MEAN_DIFF:
                            pass
                        else:
                            #if cnode_data.mean_edges > self.cnodes_dict[periphery_cnode_id].mean_edges:
                            if cnode_data.cohesion > self.cnodes_dict[periphery_cnode_id].cohesion:
                                print("CP type B found")
                                print("Core")
                                print(str(cnode_id))
                                print("Periphery")
                                print((str(periphery_cnode_id)))

                                self.calculate_relationship_scores(relationship_score, cnode_id, periphery_cnode_id)

                                cnode_data.set_cnode_CP_status(ClusterStatus.core)
                                self.cnodes_dict[periphery_cnode_id].set_cnode_CP_status(ClusterStatus.periphery)
                                #self.set_cluster_CP_status(cnode_id)
                                #self.set_cluster_CP_status(periphery_cnode_id)

                                cnode_relationship = CNodeRelationship(cnode_id, periphery_cnode_id, CNodeRelationshipType.core_core, relationship_score)
                                self.cnode_relationship_dict.put_relationship_object(cnode_id, periphery_cnode_id, cnode_relationship)
                            else:
                                print("CP type B found")
                                print("Core")
                                print(str(periphery_cnode_id))
                                print("Periphery")
                                print((str(cnode_id)))

                                self.calculate_relationship_scores(relationship_score, periphery_cnode_id, cnode_id)

                                cnode_data.set_cnode_CP_status(ClusterStatus.periphery)
                                self.cnodes_dict[periphery_cnode_id].set_cnode_CP_status(ClusterStatus.core)
                                #self.set_cluster_CP_status(cnode_id)
                                #self.set_cluster_CP_status(periphery_cnode_id)

                                cnode_relationship = CNodeRelationship(periphery_cnode_id, cnode_id, CNodeRelationshipType.core_core, relationship_score)
                                self.cnode_relationship_dict.put_relationship_object(periphery_cnode_id, cnode_id, cnode_relationship)



                        ###############################
                        # if cnode_data.mean_edges > self.cnodes_dict[periphery_cnode_id].mean_edges:
                        # #if cnode_data.cohesion > self.cnodes_dict[periphery_cnode_id].cohesion:
                        #     print("CP type B found")
                        #     print("Core")
                        #     print(str(cnode_id))
                        #     print("Periphery")
                        #     print((str(periphery_cnode_id)))
                        #
                        #     self.calculate_relationship_scores(relationship_score, cnode_id, periphery_cnode_id)
                        #
                        #     #cnode_data.set_cnode_CP_status(ClusterStatus.core)
                        #     #self.cnodes_dict[periphery_cnode_id].set_cnode_CP_status(ClusterStatus.periphery)
                        #     self.set_cluster_CP_status(cnode_id)
                        #     self.set_cluster_CP_status(periphery_cnode_id)
                        #
                        #     cnode_relationship = CNodeRelationship(cnode_id, periphery_cnode_id, CNodeRelationshipType.core_core, relationship_score)
                        #     self.cnode_relationship_dict.put_relationship_object(cnode_id, periphery_cnode_id, cnode_relationship)
                        # elif cnode_data.mean_edges <= self.cnodes_dict[periphery_cnode_id].mean_edges:
                        #     print("CP type B found")
                        #     print("Core")
                        #     print(str(periphery_cnode_id))
                        #     print("Periphery")
                        #     print((str(cnode_id)))
                        #
                        #     self.calculate_relationship_scores(relationship_score, periphery_cnode_id, cnode_id)
                        #
                        #     #Check for the possibility of a type C relationship
                        #     if self.cnodes_dict[periphery_cnode_id].mean_edges - cnode_data.mean_edges >= self.MEAN_DIFF:
                        #         relationship_score.aggregate_type = "C"
                        #         cnode_data.set_cnode_CP_status(ClusterStatus.periphery)
                        #         self.cnodes_dict[periphery_cnode_id].set_cnode_CP_status(ClusterStatus.core)
                        #         cnode_relationship = CNodeRelationship(periphery_cnode_id, cnode_id, CNodeRelationshipType.core_periphery, relationship_score)
                        #     else:
                        #         self.set_cluster_CP_status(cnode_id)
                        #         self.set_cluster_CP_status(periphery_cnode_id)
                        #         cnode_relationship = CNodeRelationship(periphery_cnode_id, cnode_id, CNodeRelationshipType.core_core, relationship_score)
                        #
                        #
                        #
                        #     self.cnode_relationship_dict.put_relationship_object(periphery_cnode_id, cnode_id, cnode_relationship)

                    elif relationship_score.aggregate_type == "D":
                        if self.cnodes_dict[periphery_cnode_id].mean_edges > cnode_data.mean_edges:
                            print("CP type D found")
                            print("Periphery")
                            print(str(cnode_id))
                            print("Core")
                            print((str(periphery_cnode_id)))

                            relationship_score.aggregate_type = "C"
                            self.calculate_relationship_scores(relationship_score, periphery_cnode_id, cnode_id)

                            cnode_data.set_cnode_CP_status(ClusterStatus.periphery)
                            self.cnodes_dict[periphery_cnode_id].set_cnode_CP_status(ClusterStatus.core)

                            cnode_relationship = CNodeRelationship(periphery_cnode_id, cnode_id, CNodeRelationshipType.core_periphery, relationship_score)
                            self.cnode_relationship_dict.put_relationship_object(periphery_cnode_id, cnode_id, cnode_relationship)
                    elif relationship_score.aggregate_type == "F":
                        if self.cnodes_dict[periphery_cnode_id].mean_edges > cnode_data.mean_edges:
                            print("CP type F found")
                            print("Periphery")
                            print(str(cnode_id))
                            print("Core")
                            print((str(periphery_cnode_id)))

                            relationship_score.aggregate_type = "AF"
                            self.calculate_relationship_scores(relationship_score, periphery_cnode_id, cnode_id)

                            cnode_data.set_cnode_CP_status(ClusterStatus.periphery)
                            self.cnodes_dict[periphery_cnode_id].set_cnode_CP_status(ClusterStatus.core)

                            cnode_relationship = CNodeRelationship(periphery_cnode_id, cnode_id, CNodeRelationshipType.core_periphery, relationship_score)
                            self.cnode_relationship_dict.put_relationship_object(periphery_cnode_id, cnode_id, cnode_relationship)

                    elif relationship_score.aggregate_type == "E":
                        print("Type E CP found")
                        print("Core")
                        print(str(cnode_id))
                        print("Periphery")
                        print((str(periphery_cnode_id)))

                        self.calculate_relationship_scores(relationship_score, cnode_id, periphery_cnode_id)

                        #I think that type E relationship occurs only between two peripheries.
                        cnode_data.set_cnode_CP_status(ClusterStatus.periphery)
                        self.cnodes_dict[periphery_cnode_id].set_cnode_CP_status(ClusterStatus.periphery)


                        cnode_relationship = CNodeRelationship(cnode_id, periphery_cnode_id, CNodeRelationshipType.periphery_periphery, relationship_score)

                        self.cnode_relationship_dict.put_relationship_object(cnode_id, periphery_cnode_id, cnode_relationship)

                    # if relationship_score.typeE_score == 0:
                    #     if self.cnode_cluster_initiator_list.index(periphery_cnode_id) > self.cnode_cluster_initiator_list.index(cnode_id):
                    #         print("CP found")
                    #         print("Core")
                    #         print(str(cnode_id))
                    #         print("Periphery")
                    #         print((str(periphery_cnode_id)))
                    #
                    #         self.calculate_relationship_scores(relationship_score, cnode_id, periphery_cnode_id)
                    #
                    #         cnode_data.set_cnode_CP_status(ClusterStatus.core)
                    #         self.cnodes_dict[periphery_cnode_id].set_cnode_CP_status(ClusterStatus.periphery)
                    #
                    #         cnode_relationship = CNodeRelationship(cnode_id, periphery_cnode_id, CNodeRelationshipType.core_periphery, relationship_score)
                    #         self.cnode_relationship_dict.put_relationship_object(cnode_id, periphery_cnode_id, cnode_relationship)
                    # else:
                    #         print("Type E CP found")
                    #         print("Core")
                    #         print(str(cnode_id))
                    #         print("Periphery")
                    #         print((str(periphery_cnode_id)))
                    #
                    #         self.calculate_relationship_scores(relationship_score, cnode_id, periphery_cnode_id)
                    #
                    #         cnode_data.set_cnode_CP_status(ClusterStatus.core)
                    #         self.cnodes_dict[periphery_cnode_id].set_cnode_CP_status(ClusterStatus.periphery)
                    #
                    #
                    #         cnode_relationship = CNodeRelationship(cnode_id, periphery_cnode_id, CNodeRelationshipType.core_periphery, relationship_score)
                    #
                    #         self.cnode_relationship_dict.put_relationship_object(cnode_id, periphery_cnode_id, cnode_relationship)

    def set_cluster_CP_status(self, cnode_data_id):
        self.configdata.logger.debug("Debugging from inside set_cluster_CP_status methpd of Phase2Data_WI class.")

        status = ClusterStatus.none
        if cnode_data_id in self.periphery_dict:
            if self.periphery_dict[cnode_data_id]['ycohesion_nsd_low'] or self.periphery_dict[cnode_data_id]['ncohesion_nsd_low'] or self.periphery_dict[cnode_data_id]['ycohesion_ysd_pp'] :
                status = ClusterStatus.periphery
            else:
                status = ClusterStatus.core
        else:
            status = ClusterStatus.core

        self.cnodes_dict[cnode_data_id].set_cnode_CP_status(status)

    def calculate_relationship_scores(self, relationship_score, cnode_id, periphery_cnode_id):
        self.configdata.logger.debug("Debugging from inside calculate_relationship_scores method of "
                                     "class Phase2Data_WI.")
        #relationship_score.classify_periphery_cnode_type()
        (composite_score, reverse_composite_score, composite_score_3, edge_weight_score, structure_score, structure_score_1) = self.calculate_composite_cnode_relationship_score(cnode_id,periphery_cnode_id)
        relationship_score.composite_score = composite_score
        relationship_score.reverse_composite_score = reverse_composite_score
        relationship_score.composite_score_3 = composite_score_3
        relationship_score.edge_weight_score = edge_weight_score
        relationship_score.structure_score = structure_score
        relationship_score.structure_score_1 = structure_score_1


    def calculate_composite_cnode_relationship_score(self, cnode_id, periphery_cnode_id):
        self.configdata.logger.debug("Debugging from inside calculate_composite_cnode_relationship_score method of class Phase2Data_WI.")
        cnode_data = self.cnodes_dict[cnode_id]
        periphery_cnode_data = self.cnodes_dict[periphery_cnode_id]

        cnode_data.calculate_cnode_secondary_fields()
        periphery_cnode_data.calculate_cnode_secondary_fields()

        composite_score = self.calculate_composite_score(cnode_data.mean_edges, periphery_cnode_data.mean_edges, cnode_data.standard_deviation_edges)
        reverse_composite_score = self.calculate_composite_score(cnode_data.mean_edges, periphery_cnode_data.mean_edges, periphery_cnode_data.standard_deviation_edges)

        composite_score_3 = self.calculate_composite_score_3(cnode_data, periphery_cnode_data)

        (edge_weight_score, structure_score, structure_score_1)  = self.calculate_edge_weight_and_structure_score(cnode_data, periphery_cnode_data)

        return (composite_score, reverse_composite_score, composite_score_3, edge_weight_score, structure_score, structure_score_1)

    def calculate_composite_score(self, mean_cnode, mean_periphery_cnode, sd_cnode):
        self.configdata.logger.debug("Debugging from inside calculate_composite_score method of Phase2Data_WI class.")
        if sd_cnode != 0:
            composite_score = abs(mean_cnode - mean_periphery_cnode)/sd_cnode
        else:
            composite_score = 0
        return composite_score

    #Consider periphery and connection edge set separately to calculate
    #edge weight based score
    def calculate_composite_score_3(self, cnode_data, periphery_cnode_data):
        self.configdata.logger.debug("Debugging from inside calculate_composite_score_3 method of Phase2Data_WI class")
        edgeset = cnode_data.external_edge_dict[EdgeType.primary].intersection(periphery_cnode_data.external_edge_dict[EdgeType.primary])
        mean_edgeset = cnode_data.calculate_mean_edgeset(edgeset)
        composite_score = self.calculate_composite_score(cnode_data.mean_edges, periphery_cnode_data.mean_edges, cnode_data.standard_deviation_edges)
        composite_score = composite_score + self.calculate_composite_score(cnode_data.mean_edges, mean_edgeset, cnode_data.standard_deviation_edges)
        return composite_score

    #Consider periphery and the connecting edge set together to calculate
    #edge weight score
    def calculate_edge_weight_and_structure_score(self, cnode_data, periphery_cnode_data):
        self.configdata.logger.debug("Debugging from inside calcualte_edge_weight_score_4 method of class Phase2Data_WI.")

        edgeset = cnode_data.external_edge_dict[EdgeType.primary].intersection(periphery_cnode_data.external_edge_dict[EdgeType.primary])
        edgeset.update(periphery_cnode_data.internal_edge_dict[EdgeType.primary])

        #Calculate edge weight based score
        mean_edgeset = cnode_data.calculate_mean_edgeset(edgeset)
        edge_weight_score = self.calculate_composite_score(cnode_data.mean_edges, mean_edgeset, cnode_data.standard_deviation_edges)

        #Calculate structure based score
        edgeset.update(cnode_data.internal_edge_dict[EdgeType.primary])
        num_nodes_merged = cnode_data.num_nodes + periphery_cnode_data.num_nodes - len(cnode_data.node_set.intersection(periphery_cnode_data.node_set))
        structure_density_edgeset = cnode_data.calculate_struct_density_edgeset(num_nodes_merged, len(edgeset))
        structure_score = cnode_data.struct_density - structure_density_edgeset

        structure_score_1 = structure_density_edgeset

        return (edge_weight_score, structure_score, structure_score_1)
