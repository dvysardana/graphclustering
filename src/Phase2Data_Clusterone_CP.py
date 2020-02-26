__author__ = 'divya'

from Phase2Data_Clusterone import Phase2Data_Clusterone
from CNodeData_Clusterone_CP import CNodeData_Clusterone_CP
from EdgeData import EdgeType
from EvaluationData_Clusterone_CP import EvaluationData_Clusterone_CP
from AlgorithmName import AlgorithmName
from CNodeRelationshipScore import CNodeRelationshipScore
from CNodeRelationshipType import CNodeRelationshipType
from CNodeRelationship import CNodeRelationship
from CNodeRelationshipDictionary import CNodeRelationshipDictionary
from CNodeData import ClusterStatus

class Phase2Data_Clusterone_CP(Phase2Data_Clusterone):
    def __init__(self, graphdata, configdata, cnodes_dict, next_cluster_label, num_clusters):
        super(Phase2Data_Clusterone_CP, self).__init__(graphdata, configdata, cnodes_dict, next_cluster_label, num_clusters)
        self.cnode_relationship_dict = CNodeRelationshipDictionary()

        self.cnode_cluster_initiator_list = [] #List containing cnodes sorted in descending cohesion order.


    def evaluate_phase(self):
        self.configdata.logger.debug("Debugging from inside evaluate_phase method of Phase2Data_Clusterone.")
        self.phase1_evaluation_data = EvaluationData_Clusterone_CP(self.graphdata, self.configdata, self.K, self.phase, self.num_clusters, self.cnodes_dict, self.cnode_relationship_dict, AlgorithmName.Clusterone)
        self.phase1_evaluation_data.calculate_evaluation_measures_for_one_K()

    #Method for execute phase of clusterone
    def clusterone_phase2_execute(self):
        self.configdata.logger.debug("Debugging from inside clusterone_phase2_execute method of cladd Phase2Data_Clusterone_CP.")

        #Call base class method
        super().clusterone_phase2_execute()

        #Extract inter cnode relationships
        self.extract_core_periphery_relationships()

        #Extract global core periphery relationships
        self.extract_global_core_periphery_relationships()

    #Overriding base class method
    #Method to create a new cnode upon merging of cnodes in merger_set
    def create_merged_cnode(self, merger_set):
        self.configdata.logger.debug("Debugging from inside create_merged_cnode method.")
        #Create a new cnode object
        #cluster_label_new = self.next_cluster_label
        cluster_label_new = min(list(merger_set))

        cnode_data_merged = CNodeData_Clusterone_CP(cluster_label_new, -1, -1, -1, self.graphdata, self.configdata)

       #Add the new cnode object to cnodes_dict
        #self.cnodes_dict[cluster_label_new] = cnode_data_merged

       #Add nodes to new cnode
        self.add_nodes_to_merged_cnode(merger_set, cnode_data_merged)

        #Add edges to new cnode
        #primary
        self.add_edges_to_merged_cnode(merger_set, cnode_data_merged, EdgeType.primary)

        #Add the boundary sets from all merging cnodes
        self.add_boundary_sets_to_merged_cnode(merger_set, cnode_data_merged)

        #Run the clustering statistics for the new cnode
        #this also sets the active and dirty flags.
        cnode_data_merged.calculate_cnode_secondary_fields()

        return cnode_data_merged

    #Method to add nodes to merged cnode
    def add_boundary_sets_to_merged_cnode(self, merger_set, cnode_data_merged):
        self.configdata.logger.debug("Debugging from inside add_boundary_sets_to_merged_cnode method of Phase2Data_Clusterone class.")
        #cnode_data_merged = self.cnodes_dict[cluster_label_new]
        cluster_label_new = cnode_data_merged.cnode_id
        cnode_node_set = cnode_data_merged.node_set
        for cnode_i in merger_set:
            cnode_data_i = self.cnodes_dict[cnode_i]
            self.create_merged_boundary_set(cnode_data_i.boundary_node_dict_ycohesion_nsd, cnode_data_merged.boundary_node_dict_ycohesion_nsd, cnode_node_set)
            self.create_merged_boundary_set(cnode_data_i.boundary_node_dict_ncohesion_ysd, cnode_data_merged.boundary_node_dict_ncohesion_ysd, cnode_node_set)
            self.create_merged_boundary_set(cnode_data_i.boundary_node_dict_ncohesion_nsd_low, cnode_data_merged.boundary_node_dict_ncohesion_nsd_low, cnode_node_set)
            self.create_merged_boundary_set(cnode_data_i.boundary_node_dict_ncohesion_nsd_high, cnode_data_merged.boundary_node_dict_ncohesion_nsd_high, cnode_node_set)

    #Method to create a merged boundary set
    def create_merged_boundary_set(self, inp_boundary_dict, merged_boundary_dict, cnode_node_set):
        self.configdata.logger.debug("Debbuging from inside create_merged_boundary_set method of Phase2Data_Clusterone_CP class.")
        for node_id, boundary_score  in inp_boundary_dict.items():
            if node_id not in cnode_node_set:
                if node_id in merged_boundary_dict:
                    merged_boundary_dict[node_id] = merged_boundary_dict[node_id] + boundary_score
                else:
                    merged_boundary_dict[node_id] = boundary_score

    #Method to extract core periphery relationships
    def extract_core_periphery_relationships(self):
        self.configdata.logger.debug("Debugging from inside extract_core_periphery_relationships method of Phase2Data_Clusterone class.")
        for cnode_id, cnode_data in self.cnodes_dict.items():
            self.extract_core_periphery_relationships_typeA(cnode_data)
            self.extract_core_periphery_relationships_typeB(cnode_data)
            self.extract_core_periphery_relationships_typeC(cnode_data)
            self.extract_core_periphery_relationships_typeD(cnode_data)


    #Method to extract core periphery relationships of Type A
    #ycohesion nsd
    def extract_core_periphery_relationships_typeA(self, cnode_data):
        self.configdata.logger.debug("Debugging from inside extract_core_periphery_relationships_typeA")
        for node_id, boundary_score in cnode_data.boundary_node_dict_ycohesion_nsd.items():
            node_cnode_id_set = set(self.graphdata.node_dict[node_id].clusterone_clabel_dict.keys())
            for node_cnode_id in node_cnode_id_set:
                if node_cnode_id in cnode_data.periphery_cnode_dict:
                    cnode_relationship_score = cnode_data.periphery_cnode_dict[node_cnode_id]
                else:
                    cnode_relationship_score = CNodeRelationshipScore()
                    cnode_data.periphery_cnode_dict[node_cnode_id] = cnode_relationship_score

                #cnode_relationship_score.typeA_score = cnode_relationship_score.typeA_score + boundary_score
                cnode_relationship_score.typeA_score = cnode_relationship_score.typeA_score + 1


    #Method to extract core periphery relationships of Type B
    #ncohesion ysd
    def extract_core_periphery_relationships_typeB(self, cnode_data):
        self.configdata.logger.debug("Debugging from inside extract_core_periphery_relationships_typeB")
        for node_id, boundary_score in cnode_data.boundary_node_dict_ncohesion_ysd.items():
            node_cnode_id_set = set(self.graphdata.node_dict[node_id].clusterone_clabel_dict.keys())
            for node_cnode_id in node_cnode_id_set:
                if node_cnode_id in cnode_data.periphery_cnode_dict:
                    cnode_relationship_score = cnode_data.periphery_cnode_dict[node_cnode_id]
                else:
                    cnode_relationship_score = CNodeRelationshipScore()
                    cnode_data.periphery_cnode_dict[node_cnode_id] = cnode_relationship_score

                #cnode_relationship_score.typeB_score = cnode_relationship_score.typeB_score + boundary_score
                cnode_relationship_score.typeB_score = cnode_relationship_score.typeB_score + 1



    #Method to extract core periphery relationships of Type C
    #ncohesion nsd low
    def extract_core_periphery_relationships_typeC(self, cnode_data):
        self.configdata.logger.debug("Debugging from inside extract_core_periphery_relationships_typeC")
        for node_id, boundary_score in cnode_data.boundary_node_dict_ncohesion_nsd_low.items():
            node_cnode_id_set = set(self.graphdata.node_dict[node_id].clusterone_clabel_dict.keys())
            for node_cnode_id in node_cnode_id_set:
                if node_cnode_id in cnode_data.periphery_cnode_dict:
                    cnode_relationship_score = cnode_data.periphery_cnode_dict[node_cnode_id]
                else:
                    cnode_relationship_score = CNodeRelationshipScore()
                    cnode_data.periphery_cnode_dict[node_cnode_id] = cnode_relationship_score

                #cnode_relationship_score.typeC_score = cnode_relationship_score.typeC_score + boundary_score
                cnode_relationship_score.typeC_score = cnode_relationship_score.typeC_score + 1


    #Method to extract core periphery relationships of Type D
    #ncohesion nsd high
    def extract_core_periphery_relationships_typeD(self, cnode_data):
        self.configdata.logger.debug("Debugging from inside extract_core_periphery_relationships_typeD")
        for node_id, boundary_score in cnode_data.boundary_node_dict_ncohesion_nsd_high.items():
            node_cnode_id_set = set(self.graphdata.node_dict[node_id].clusterone_clabel_dict.keys())
            for node_cnode_id in node_cnode_id_set:
                if node_cnode_id in cnode_data.periphery_cnode_dict:
                    cnode_relationship_score = cnode_data.periphery_cnode_dict[node_cnode_id]
                else:
                    cnode_relationship_score = CNodeRelationshipScore()
                    cnode_data.periphery_cnode_dict[node_cnode_id] = cnode_relationship_score

                #cnode_relationship_score.typeD_score = cnode_relationship_score.typeD_score + boundary_score
                cnode_relationship_score.typeD_score = cnode_relationship_score.typeD_score + 1

    #Method to extract global core periphery relationships
    def extract_global_core_periphery_relationships(self):
        self.configdata.logger.debug("Debugging from inside extract_global_core_periphery_relationships method of class Phase2Data_Clusterone_CP.")

        sorted_cnode_ids = sorted(list(self.cnodes_dict.keys()))

        #self.sort_cnodes_cohesion_order()

        for cnode_id in sorted_cnode_ids:
        #for cnode_id in self.cnode_cluster_initiator_list:
        #for cnode_id, cnode_data in sorted(self.cnodes_dict.iteritems(), key=lambda (k,v): (v,k)):
            cnode_data = self.cnodes_dict[cnode_id]
            for periphery_cnode_id, relationship_score in cnode_data.periphery_cnode_dict.items():
                if self.cnode_relationship_dict.contains_relationship(cnode_id, periphery_cnode_id):
                    pass
                else:
                    relationship_score.classify_periphery_cnode_type()
                    #if periphery_cnode_id > cnode_id:
                    #if cnode_data.cohesion > self.cnodes_dict[periphery_cnode_id].cohesion:
                    if relationship_score.aggregate_type == "C":
                        if cnode_data.mean_edges > self.cnodes_dict[periphery_cnode_id].mean_edges:
                        #if cnode_data.mean_edges > self.cnodes_dict[periphery_cnode_id].mean_edges or cnode_data.struct_density > self.cnodes_dict[periphery_cnode_id].struct_density:
                        #     print("Periphery id")
                        #     print(str(periphery_cnode_id))
                        #     print("Core id")
                        #     print(str(cnode_id))
                        #     print(",")
                        #     #Form a core periphery relationship between cnode_id and periphery_cnode_id
                            #Classify periphery as type A, type B, type C or type D

                            # relationship_score.classify_periphery_cnode_type()
                            # (composite_score, reverse_composite_score, composite_score_3) = self.calculate_composite_cnode_relationship_score(cnode_id,periphery_cnode_id)
                            # relationship_score.composite_score = composite_score
                            # relationship_score.reverse_composite_score = reverse_composite_score
                            # relationship_score.composite_score_3 = composite_score_3

                            #Set cnode CP status for both core and periphery
                            cnode_data.set_cnode_CP_status(ClusterStatus.core)
                            self.cnodes_dict[periphery_cnode_id].set_cnode_CP_status(ClusterStatus.periphery)

                            #Calculate different types of relationship scores.
                            self.calculate_relationship_scores(relationship_score, cnode_id, periphery_cnode_id)

                            cnode_relationship = CNodeRelationship(cnode_id, periphery_cnode_id, CNodeRelationshipType.core_periphery, relationship_score)
                            self.cnode_relationship_dict.put_relationship_object(cnode_id, periphery_cnode_id, cnode_relationship)
                    elif relationship_score.aggregate_type == "B":
                        #if cnode_data.mean_edges > self.cnodes_dict[periphery_cnode_id].mean_edges:
                        if cnode_data.cohesion > self.cnodes_dict[periphery_cnode_id].cohesion:
                        #if cnode_data.mean_edges > self.cnodes_dict[periphery_cnode_id].mean_edges or cnode_data.struct_density > self.cnodes_dict[periphery_cnode_id].struct_density:


                            # #Set cnode CP status for both core and periphery
                            # if cnode_data.cnode_CP_status != ClusterStatus.periphery:
                            #     cnode_data.set_cnode_CP_status(ClusterStatus.core)
                            # #self.cnodes_dict[periphery_cnode_id].set_cnode_CP_status(ClusterStatus.periphery)
                            # if self.cnodes_dict[periphery_cnode_id].cnode_CP_status != ClusterStatus.periphery:
                            #     self.cnodes_dict[periphery_cnode_id].set_cnode_CP_status(ClusterStatus.core)

                            #Set cnode CP status for both core and periphery

                            cnode_data.set_cnode_CP_status(ClusterStatus.core)
                            #self.cnodes_dict[periphery_cnode_id].set_cnode_CP_status(ClusterStatus.periphery)

                            self.cnodes_dict[periphery_cnode_id].set_cnode_CP_status(ClusterStatus.periphery)

                            #Calculate different types of relationship scores.
                            self.calculate_relationship_scores(relationship_score, cnode_id, periphery_cnode_id)

                            cnode_relationship = CNodeRelationship(cnode_id, periphery_cnode_id, CNodeRelationshipType.core_core, relationship_score)
                            self.cnode_relationship_dict.put_relationship_object(cnode_id, periphery_cnode_id, cnode_relationship)

                    elif relationship_score.aggregate_type == "D":
                        if cnode_data.mean_edges < self.cnodes_dict[periphery_cnode_id].mean_edges:
                        #if cnode_data.mean_edges > self.cnodes_dict[periphery_cnode_id].mean_edges or cnode_data.struct_density > self.cnodes_dict[periphery_cnode_id].struct_density:
                        #     print("Periphery id")
                        #     print(str(periphery_cnode_id))
                        #     print("Core id")
                        #     print(str(cnode_id))
                        #     print(",")
                        #     #Form a core periphery relationship between cnode_id and periphery_cnode_id
                            #Classify periphery as type A, type B, type C or type D

                            # relationship_score.classify_periphery_cnode_type()
                            # (composite_score, reverse_composite_score, composite_score_3) = self.calculate_composite_cnode_relationship_score(cnode_id,periphery_cnode_id)
                            # relationship_score.composite_score = composite_score
                            # relationship_score.reverse_composite_score = reverse_composite_score
                            # relationship_score.composite_score_3 = composite_score_3

                            relationship_score.aggregate_type = "C"

                            #Set cnode CP status for both core and periphery
                            cnode_data.set_cnode_CP_status(ClusterStatus.periphery)
                            self.cnodes_dict[periphery_cnode_id].set_cnode_CP_status(ClusterStatus.core)

                            #Calculate different types of relationship scores.
                            self.calculate_relationship_scores(relationship_score, periphery_cnode_id, cnode_id)

                            cnode_relationship = CNodeRelationship(periphery_cnode_id, cnode_id, CNodeRelationshipType.core_periphery, relationship_score)
                            self.cnode_relationship_dict.put_relationship_object(periphery_cnode_id, cnode_id, cnode_relationship)


        # print("Number of cnode core periphery relationships:")
        # print(str(len(list(self.cnode_relationship_dict.cnode_relationship_dict.keys()))))

    # def calculate_composite_cnode_relationship_score(self, cnode_id, periphery_cnode_id):
    #     self.configdata.logger.debug("Debugging from inside calculate_composite_cnode_relationship_score method of class Phase2Data_Clusterone_CP.")
    #     cnode_data = self.cnodes_dict[cnode_id]
    #     periphery_cnode_data = self.cnodes_dict[periphery_cnode_id]
    #
    #     cnode_data.calculate_cnode_secondary_fields()
    #     periphery_cnode_data.calculate_cnode_secondary_fields()
    #
    #     composite_score = self.calculate_composite_score(cnode_data.mean_edges, periphery_cnode_data.mean_edges, cnode_data.standard_deviation_edges)
    #     reverse_composite_score = self.calculate_composite_score(cnode_data.mean_edges, periphery_cnode_data.mean_edges, periphery_cnode_data.standard_deviation_edges)
    #
    #     composite_score_3 = self.calculate_composite_score_3(cnode_data, periphery_cnode_data)
    #
    #     return (composite_score, reverse_composite_score, composite_score_3)

    #Method to sort cnodes as per cohesion to get the cnode cluster initiator order.
    def sort_cnodes_cohesion_order(self):
        self.configdata.logger.debug("Debugging from inside sort_cnodes_cohesion_order method of class Phase2Data_Clusterone_CP.")
        cnode_sort_list = []
        for cnode_id, cnode_data in self.cnodes_dict.items():
            if cnode_data.active == True:
                cnode_sort_list.append((cnode_id, cnode_data.cohesion))
            #cnode_data.initialize_MKNN(self.K)


        cnode_sort_list = sorted(cnode_sort_list, key = lambda x:x[1], reverse = True)
        self.cnode_cluster_initiator_list = [x for (x,y) in cnode_sort_list]


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
        self.configdata.logger.debug("Debugging from inside calculate_composite_score method of Phase2Data_Clusterone_CP class.")
        if sd_cnode != 0:
            composite_score = abs(mean_cnode - mean_periphery_cnode)/sd_cnode
        else:
            composite_score = 0
        return composite_score

    def calculate_composite_score_3(self, cnode_data, periphery_cnode_data):
        self.configdata.logger.debug("Debugging from inside calculate_composite_score_3 method of Phase2Data_Clusterone_CP class")
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