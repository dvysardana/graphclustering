__author__ = 'divya'

from Phase2Data_WI import Phase2Data_WI

class Phase2Data_WI_semisupervised(Phase2Data_WI):

    def __init__(self, graphdata, configdata, K, cnodes_dict, next_cluster_label, num_clusters):
        super(Phase2Data_WI_semisupervised, self).__init__(graphdata, configdata, K, cnodes_dict, next_cluster_label, num_clusters)

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
        #self.form_overlapping_clusters()

    #Override the base class method for Phase2_execute
    def MKNN_phase2_execute(self):
        pass

    #Override the base class method to calculate c_SM
    def calculate_c_SM(self):
       pass