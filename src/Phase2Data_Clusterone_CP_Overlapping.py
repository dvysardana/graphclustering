__author__ = 'divya'


from Phase2Data_Clusterone_CP import Phase2Data_Clusterone_CP
from CNodeData_Clusterone_CP import CNodeData_Clusterone_CP
from EdgeData import EdgeType
from EvaluationData_Clusterone_CP import EvaluationData_Clusterone_CP
from AlgorithmName import AlgorithmName
from CNodeRelationshipScore import CNodeRelationshipScore
from CNodeRelationshipType import CNodeRelationshipType
from CNodeRelationship import CNodeRelationship
from CNodeRelationshipDictionary import CNodeRelationshipDictionary
from CNodeData import ClusterStatus

class Phase2Data_Clusterone_CP_Overlapping(Phase2Data_Clusterone_CP):
    def __init__(self, graphdata, configdata, cnodes_dict, next_cluster_label, num_clusters):
        super(Phase2Data_Clusterone_CP_Overlapping, self).__init__(graphdata, configdata, cnodes_dict, next_cluster_label, num_clusters)

        self.MERGE_THRESHOLD = 3 #Periphery cnodes less than this size are merged with all their cores.


    #Method for execute phase of clusterone
    def clusterone_phase2_execute(self):
        self.configdata.logger.debug("Debugging from inside clusterone_phase2_execute method of cladd Phase2Data_Clusterone_CP.")

        #Call base class method
        super().clusterone_phase2_execute()

        #Extract inter cnode relationships
        self.extract_core_periphery_relationships()

        #Extract global core periphery relationships
        self.extract_global_core_periphery_relationships()

        #Form overlapping clusters
        self.form_overlapping_clusters()

    def form_overlapping_clusters(self):
        self.configdata.logger.debug("Debugging from inside Phase2Data_WI_Overlapping class's form_overlapping_clusters method.")

        for (cnode1_id, cnode2_id), cnode_relationship in self.cnode_relationship_dict.cnode_relationship_dict.items():
            core_cnode_id = cnode_relationship.cnode1_id
            periphery_cnode_id = cnode_relationship.cnode2_id
            core_cnode_data = self.cnodes_dict[core_cnode_id]
            periphery_cnode_data = self.cnodes_dict[periphery_cnode_id]
            core_status = core_cnode_data.cnode_CP_status
            periphery_status = periphery_cnode_data.cnode_CP_status
            overlapping_nodeset = set()
            if cnode_relationship.relationship_score.aggregate_type == "A":

                if periphery_cnode_data.num_nodes < self.MERGE_THRESHOLD:

                    #Define the cnode which will be expanded with overlapping nodes
                    sink_cnode_data = core_cnode_data

                    #Define the source cnode from which overlapping nodes will be extracted
                    source_cnode_data = periphery_cnode_data

                    self.perform_overlap(sink_cnode_data, source_cnode_data, overlapping_nodeset)

                elif core_cnode_data.num_nodes < self.MERGE_THRESHOLD:
                    sink_cnode_data = periphery_cnode_data

                    #Define the source cnode from which overlapping nodes will be extracted
                    source_cnode_data = core_cnode_data

                    self.perform_overlap(sink_cnode_data, source_cnode_data, overlapping_nodeset)


            elif cnode_relationship.relationship_score.aggregate_type == "B":
                if periphery_cnode_data.num_nodes < self.MERGE_THRESHOLD:

                    #Define the cnode which will be expanded with overlapping nodes
                    sink_cnode_data = core_cnode_data

                    #Define the source cnode from which overlapping nodes will be extracted
                    source_cnode_data = periphery_cnode_data

                    self.perform_overlap(sink_cnode_data, source_cnode_data, overlapping_nodeset)

                elif core_cnode_data.num_nodes < self.MERGE_THRESHOLD:
                    sink_cnode_data = periphery_cnode_data

                    #Define the source cnode from which overlapping nodes will be extracted
                    source_cnode_data = core_cnode_data

                    self.perform_overlap(sink_cnode_data, source_cnode_data, overlapping_nodeset)

                #else:

                    # #Define the cnode which will be expanded with overlapping nodes
                    # sink_cnode_data = periphery_cnode_data
                    # sink_cnode_id = periphery_cnode_id
                    #
                    # #Define the source cnode from which overlapping nodes will be extracted
                    # source_cnode_data = core_cnode_data
                    # source_cnode_id = core_cnode_id

            # elif cnode_relationship.relationship_score.aggregate_type == "C":
            #     if periphery_cnode_data.num_nodes < self.MERGE_THRESHOLD:
            #
            #         #Define the cnode which will be expanded with overlapping nodes
            #         sink_cnode_data = core_cnode_data
            #
            #         #Define the source cnode from which overlapping nodes will be extracted
            #         source_cnode_data = periphery_cnode_data
            #
            #         self.perform_overlap(sink_cnode_data, source_cnode_data, overlapping_nodeset)

            # elif cnode_relationship.relationship_score.aggregate_type == "AF":
            #     if periphery_cnode_data.num_nodes < self.MERGE_THRESHOLD:
            #
            #         #Define the cnode which will be expanded with overlapping nodes
            #         sink_cnode_data = core_cnode_data
            #
            #         #Define the source cnode from which overlapping nodes will be extracted
            #         source_cnode_data = periphery_cnode_data
            #
            #         self.perform_overlap(sink_cnode_data, source_cnode_data, overlapping_nodeset)
            #
            #     elif core_cnode_data.num_nodes < self.MERGE_THRESHOLD:
            #         sink_cnode_data = periphery_cnode_data
            #
            #         #Define the source cnode from which overlapping nodes will be extracted
            #         source_cnode_data = core_cnode_data
            #
            #         self.perform_overlap(sink_cnode_data, source_cnode_data, overlapping_nodeset)
            #
            # elif cnode_relationship.relationship_score.aggregate_type == "E":
            #     if periphery_cnode_data.num_nodes < self.MERGE_THRESHOLD:
            #
            #         #Define the cnode which will be expanded with overlapping nodes
            #         sink_cnode_data = core_cnode_data
            #
            #         #Define the source cnode from which overlapping nodes will be extracted
            #         source_cnode_data = periphery_cnode_data
            #
            #         self.perform_overlap(sink_cnode_data, source_cnode_data, overlapping_nodeset)
            #
            #     elif core_cnode_data.num_nodes < self.MERGE_THRESHOLD:
            #         sink_cnode_data = periphery_cnode_data
            #
            #         #Define the source cnode from which overlapping nodes will be extracted
            #         source_cnode_data = core_cnode_data
            #
            #         self.perform_overlap(sink_cnode_data, source_cnode_data, overlapping_nodeset)

    def perform_overlap(self, sink_cnode_data, source_cnode_data, overlapping_nodeset):

        shared_edgeset = sink_cnode_data.calculate_shared_edge_set(source_cnode_data)

        #Using the shared edgeset, calculate the node_ids to overlap with
        for edge_id in shared_edgeset:
            if self.graphdata.edge_dict[edge_id].node1_id in source_cnode_data.node_set:
                overlapping_nodeset.add(self.graphdata.edge_dict[edge_id].node1_id)
            elif self.graphdata.edge_dict[edge_id].node2_id in source_cnode_data.node_set:
                overlapping_nodeset.add(self.graphdata.edge_dict[edge_id].node2_id)

        #Add overlapping_nodeset to the sink.
        for node_id in overlapping_nodeset:
            #Add overlapping node to the other cnodeset
            sink_cnode_data.node_set.add(node_id)
            #Add overlapping membership to the node's cluster label dictionary
            self.graphdata.node_dict[node_id].clusterone_clabel_dict[sink_cnode_data.cnode_id] = sink_cnode_data.cnode_id
        #Recalculate cnode statistics
        sink_cnode_data.calculate_cnode_secondary_fields()


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
                    elif relationship_score.aggregate_type == "A":
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
