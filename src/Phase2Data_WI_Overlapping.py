__author__ = 'divya'

from Phase2Data_WI import Phase2Data_WI
from CNodeData_WI import CNodeData_WI
from EdgeData import EdgeType
from CNodeRelationshipScore import CNodeRelationshipScore
from CNodeRelationship import CNodeRelationship
from CNodeRelationshipType import CNodeRelationshipType
from EvaluationData_WI import EvaluationData_WI
from AlgorithmName import AlgorithmName
from CNodeRelationshipDictionary import CNodeRelationshipDictionary
from CNodeData import ClusterStatus

class Phase2Data_WI_Overlapping(Phase2Data_WI):

    def __init__(self, graphdata, configdata, K, cnodes_dict, next_cluster_label, num_clusters):
        super(Phase2Data_WI_Overlapping, self).__init__(graphdata, configdata, K, cnodes_dict, next_cluster_label, num_clusters)

        self.MERGE_THRESHOLD = 3 #Periphery cnodes less than this size are merged with all their cores.

    def execute_phase(self):
        self.configdata.logger.debug("Debugging from inside Phase2Data_WI_Overlapping class's execute_phase method.")

        #execute phase
        self.MKNN_phase2_execute()

        #merge highly overlapping cnodes
        self.MKNN_phase2_overlap()

        #extract core periphery relationships
        self.extract_core_periphery_relationships()

        #extract global core periphery relationships
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

                #else:
                elif core_cnode_data.num_nodes < self.MERGE_THRESHOLD:
                    sink_cnode_data = periphery_cnode_data

                    #Define the source cnode from which overlapping nodes will be extracted
                    source_cnode_data = core_cnode_data

                    self.perform_overlap(sink_cnode_data, source_cnode_data, overlapping_nodeset)


            elif cnode_relationship.relationship_score.aggregate_type == "C":
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

            elif cnode_relationship.relationship_score.aggregate_type == "AF":
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

            elif cnode_relationship.relationship_score.aggregate_type == "Ec":
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
            self.graphdata.node_dict[node_id].GMKNN_clabel_dict[sink_cnode_data.cnode_id] = sink_cnode_data.cnode_id
        #Recalculate cnode statistics
        sink_cnode_data.calculate_cnode_secondary_fields()