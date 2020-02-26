__author__ = 'divya'


from GraphData import GraphData
from NodeData_Gene import NodeData_Gene
from Misc.go_enrichment_processor import go_enrichment_processor
import numpy as np
import os
from CNodeData_WI_Gene import GO_term_type
from Misc.gsesame import GsesameGene, GsesameGO
from Misc.oboio import *
import pandas as pd
from GOsimDictionary import GOsimDictionary
from GOsimscore import GOsimscore
from EdgeData import EdgeType

class GraphData_Gene(GraphData):

    def __init__(self, go_type, go_size, go_sim_type, go_obo_file, gene_syn_file):
        super(GraphData_Gene, self).__init__()
        self.goea = go_enrichment_processor()
        self.SM_GO = np.matrix(np.identity(self.num_nodes), copy=False)
        self.GO_SIM_TYPE = go_sim_type #resnick, lin, semantic, icnp
        self.GO_TYPE = go_type #BP, CC, MF
        self.GO_SIZE = go_size #No. of GO_TYPE nodes

        self.GORels = np.matrix(np.identity(self.GO_SIZE), copy=False)
        self.GO_codes = {}
        #GOFILE_all = "/Users/divya/Documents/input/Misc/go-basic.obo"
        GOFILE_all = go_obo_file
        OBIO = OboIO()
        TERMS = OBIO.get_graph(GOFILE_all)

        self.gsesame_gene = GsesameGene(TERMS)

        self.GOsim_dict = GOsimDictionary()

        self.gene_syn_dict = dict()

        #self.read_gene_synonyms_file(gene_syn_file)


    #Override the base class method to create a node
    def create_node(self, node_id, node_code):

        if((node_id not in self.node_dict)):

            #For the node_code (or LocusTag), get the corresponding gene_id and gene_symbol
            nodedata_gene = NodeData_Gene(node_id, node_code, self)
            self.node_dict.update({node_id:nodedata_gene})

    # #Override the base class method to create edge objects for all primary and secondary edges
    # def create_edge_objects(self):
    #     if self.isDirty == True:
    #         self.calculate_num_nodes()
    #
    #     #SM_secondary = self.SM - self.SM_orig
    #     #Create a secondary edge for each non zero entry in this matrix.
    #     for i in range(0, self.num_nodes):
    #         for j in range(0, self.num_nodes):
    #             if(i < j):
    #                 if self.SM_orig[i, j] == 0 and self.SM[i,j] != 0:
    #                     self.create_edge(i, j, self.SM[i,j], EdgeType.secondary)
    #                 elif self.SM_orig[i,j] != 0:
    #                     self.create_edge(i, j, self.SM[i,j], EdgeType.primary)




    # #Set up GOsim based SM_GO matrix.
    # def setup_SM_GO(self, inp_rel_filename, inp_gene2go_file):
    #     self.logger.debug("Debugging from inside setup_SM_GO method of class GraphData_Gene.")
    #
    #     #Read the names for expanded input relationship file
    #     inp_filename_GOsim_codes = os.path.split(inp_rel_filename)[0] + "/GOsim/" + os.path.split(inp_rel_filename)[1].split(".")[0] + "_GOsim_codes.txt"
    #     inp_filename_GOsim_labels = os.path.split(inp_rel_filename)[0] + "/GOsim/" + os.path.split(inp_rel_filename)[1].split(".")[0] + "_GOsim_labels.txt"
    #
    #     #Check for the existence of GOsim file
    #     #if the GOsim file already exists, read it,
    #     if(os.path.isfile(inp_filename_GOsim_codes)):
    #         #1. Read SM from the saved expanded file.
    #         self.logger.debug("The GOsim based SM matrix is already stored in a file, reading it.")
    #         self.read_GOsim_SM(inp_filename_GOsim_codes)
    #         self.logger.debug("GOsim based matrix read into SM_GO.")
    #         #self.SM = self.SM + self.SM_GO
    #         self.SM = self.SM_GO
    #         self.SM = self.SM+np.matrix(np.identity(self.num_nodes), copy=False)
    #     else:
    #         self.logger.debug("The GOsim based SM matrix doesn't exist, so it will be read from gene2GO file.")
    #         self.create_GOsim_SM(inp_gene2go_file)
    #         self.logger.debug("GOsim based SM matrix has been created.")
    #         self.SM = self.SM_GO
    #         self.save_GOsim_SM(inp_filename_GOsim_codes, inp_filename_GOsim_labels)
    #         self.logger.debug("GOsim based SM matrix has been saved.")
    #         self.SM_GO = self.SM_GO+np.matrix(np.identity(self.num_nodes), copy=False)

    def setup_GO_sim(self, inp_rel_filename):
        #Input GOsim file
        inp_GOsim_file = os.path.split(inp_rel_filename)[0] + "/GOsim/go_sim_" + str(self.GO_TYPE) + ".txt"
        self.create_GO_relationship_matrix(inp_GOsim_file)

    #Read GO relationships
    def create_GO_relationship_matrix(self, inp_gosim_filename):
        self.logger.debug("Debugging from inside create_GO_matrix method of class GraphData_Gene.")

        ###########################
        # Read the relations file
        ###########################
        file_rels = pd.read_csv(
            filepath_or_buffer= inp_gosim_filename,
            header=None,
            sep=' ')

        file_rels.columns = ['goid1', 'goid2', 'resnick', 'lin', 'semantic', 'icnp']
        list_index = 0
        GOArray = np.zeros(shape=(self.GO_SIZE, self.GO_SIZE))
        #Populate GOsim_dict with GO relationships
        for i in range(file_rels.shape[0]):

            if str(file_rels['goid1'][i]) in self.GO_codes:
                go_i = self.GO_codes[str(file_rels['goid1'][i])]


            else:
                self.GO_codes[str(file_rels['goid1'][i])] = list_index
                go_i = list_index
                list_index = list_index + 1

            if str(file_rels['goid2'][i]) in self.GO_codes:
                go_j = self.GO_codes[str(file_rels['goid2'][i])]


            else:
                self.GO_codes[str(file_rels['goid2'][i])] = list_index
                go_j = list_index
                list_index = list_index + 1



            #gosim_score = GOsimscore(float(file_rels[self.GO_SIM_TYPE][i]))
            GOArray[go_i,go_j] = float(file_rels[self.GO_SIM_TYPE][i])
            GOArray[go_j,go_i] = GOArray[go_i,go_j]
            #self.GOsim_dict.put_relationship_object(str(file_rels['goid1'][i]), str(file_rels['goid2'][i]), gosim_score)

        self.GORels = np.matrix(GOArray, float)
