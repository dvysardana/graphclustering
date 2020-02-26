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

        self.read_gene_synonyms_file(gene_syn_file)


    #Override the base class method to create a node
    def create_node(self, node_id, node_code):

        if((node_id not in self.node_dict)):

            #For the node_code (or LocusTag), get the corresponding gene_id and gene_symbol
            nodedata_gene = NodeData_Gene(node_id, node_code, self)
            self.node_dict.update({node_id:nodedata_gene})

    #Override the base class method to create edge objects for all primary and secondary edges
    def create_edge_objects(self):
        if self.isDirty == True:
            self.calculate_num_nodes()

        #SM_secondary = self.SM - self.SM_orig
        #Create a secondary edge for each non zero entry in this matrix.
        for i in range(0, self.num_nodes):
            for j in range(0, self.num_nodes):
                if(i < j):
                    if self.SM_orig[i, j] == 0 and self.SM[i,j] != 0:
                        self.create_edge(i, j, self.SM[i,j], EdgeType.secondary)
                    elif self.SM_orig[i,j] != 0:
                        self.create_edge(i, j, self.SM[i,j], EdgeType.primary)




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

    def setup_SM_GO_1(self, inp_rel_filename, inp_gene2go_file):
        self.logger.debug("Debugging from inside setup_SM_GO_1 matrix")

        #Read the names for expanded input relationship file
        inp_filename_GOsim_SM_codes = os.path.split(inp_rel_filename)[0] + "/GOsim/" + os.path.split(inp_rel_filename)[1].split(".")[0] + "_" + str(self.GO_TYPE) + "_" + str(self.GO_SIM_TYPE)  + "_GOsim_codes.txt"
        inp_filename_GOsim_SM_labels = os.path.split(inp_rel_filename)[0] + "/GOsim/" + os.path.split(inp_rel_filename)[1].split(".")[0] + "_" + str(self.GO_TYPE) + "_" + str(self.GO_SIM_TYPE) + "_GOsim_labels.txt"

        #Input GOsim file
        inp_GOsim_file = os.path.split(inp_rel_filename)[0] + "/GOsim/go_sim_" + str(self.GO_TYPE) + ".txt"

        #Check for the existence of GO sim SM file
        if(os.path.isfile(inp_filename_GOsim_SM_codes)):
            #Read SM from saved file.
            self.logger.info("The GOsim SM is already stored in a file, reading it.")
            self.read_GOsim_SM(inp_filename_GOsim_SM_codes)
            self.logger.info("GOsim based SM matrix read into SM_GO.")
            self.SM = self.SM_GO
            self.SM = self.SM + np.matrix(np.identity(self.num_nodes), copy=False)
        else:
            self.logger.info("The GOsimbased matrix SM_GO doesn't exist, so it will be created.")
            self.create_GOsim_SM(inp_gene2go_file, inp_GOsim_file)
            self.logger.info("GOsim based SM matrix has been created.")
            self.SM = self.SM_GO
            self.save_GOsim_SM(inp_filename_GOsim_SM_codes, inp_filename_GOsim_SM_labels)
            self.logger.info("GOsim based SM matrix has been saved.")
            self.SM_GO = self.SM_GO + np.matrix(np.identity(self.num_nodes), copy=False)

    def read_GOsim_SM(self, inp_filename_GOsim_codes):
        self.logger.debug("Debugging from inside read_GOsim_SM method of GraphData_Gene class.")
        SMArray = np.zeros(shape=(self.num_nodes, self.num_nodes))

        self.logger.info('reading the GO_sim SM relations file')
        gosim_file_rels = pd.read_csv(
            filepath_or_buffer=inp_filename_GOsim_codes,
            header=None,
            sep=' ')

        gosim_file_rels.columns = ['node_code_1', 'node_code_2', 'edge_weight']

        for i in range(gosim_file_rels.shape[0]):
            # SMArray[gosim_file_rels['node_code_1'][i],gosim_file_rels['node_code_2'][i]] = gosim_file_rels['edge_weight'][i]
            # SMArray[gosim_file_rels['node_code_2'][i], gosim_file_rels['node_code_1'][i]] = gosim_file_rels['edge_weight'][i]

            if self.SM_orig[gosim_file_rels['node_code_1'][i], gosim_file_rels['node_code_2'][i]] == 0 and self.SM[gosim_file_rels['node_code_1'][i],gosim_file_rels['node_code_2'][i]] != 0:
                SMArray[gosim_file_rels['node_code_1'][i],gosim_file_rels['node_code_2'][i]] = float(gosim_file_rels['edge_weight'][i])/10
                SMArray[gosim_file_rels['node_code_2'][i], gosim_file_rels['node_code_1'][i]] = float(gosim_file_rels['edge_weight'][i])/10

            elif self.SM_orig[gosim_file_rels['node_code_1'][i], gosim_file_rels['node_code_2'][i]] != 0:
                SMArray[gosim_file_rels['node_code_1'][i],gosim_file_rels['node_code_2'][i]] = (float(gosim_file_rels['edge_weight'][i])/10 + self.SM_orig[gosim_file_rels['node_code_1'][i], gosim_file_rels['node_code_2'][i]])/2
                SMArray[gosim_file_rels['node_code_2'][i], gosim_file_rels['node_code_1'][i]] = (float(gosim_file_rels['edge_weight'][i])/10 + self.SM_orig[gosim_file_rels['node_code_1'][i], gosim_file_rels['node_code_2'][i]])/2


        self.SM_GO = np.matrix(SMArray, float)
        #self.SM_GO = self.SM_GO/10

        #set the diagonal elements of SM to 1
        #self.SM_GO = self.SM_GO + np.matrix(np.identity(self.num_nodes), copy=False)




    # #Create GO semantic similarity based SM
    # def create_GOsim_SM(self, inp_gene2go_file):
    #     self.logger.debug("Debugging from inside create_GOsim_SM method of class GraphData_Gene.")
    #     geneid2gos = self.goea.load_GO_gene_associations_file_with_categories(inp_gene2go_file)
    #     #print(geneid2gos[851969])
    #     #print("num nodes:")
    #     #print(self.num_nodes)
    #     SMArray = np.zeros(shape=(self.num_nodes, self.num_nodes))
    #     for i in range(0, self.num_nodes):
    #         for j in range(0, self.num_nodes):
    #             sim = 0
    #             if i<j:
    #                 # print(str(self.node_dict[i].gene_id))
    #                 # print(",")
    #                 # print(geneid2gos[self.node_dict[i].gene_id][self.GO_SIM_TYPE])
    #                 # print("|")
    #                 # print(str(self.node_dict[j].gene_id))
    #                 # print(",")
    #                 # print(geneid2gos[self.node_dict[j].gene_id][self.GO_SIM_TYPE])
    #                 if self.node_dict[i].gene_id in geneid2gos and self.node_dict[j].gene_id in geneid2gos:
    #                     if len(geneid2gos[self.node_dict[i].gene_id][self.GO_TYPE]) != 0 and len(geneid2gos[self.node_dict[j].gene_id][self.GO_TYPE]) != 0:
    #                         sim = self.gsesame_gene.scores(geneid2gos[self.node_dict[i].gene_id][self.GO_TYPE], geneid2gos[self.node_dict[j].gene_id][self.GO_TYPE])
    #                     else:
    #                         sim = 0
    #                 else:
    #                     sim = 0
    #
    #                 SMArray[i,j] = sim
    #                 SMArray[j,i] = sim
    #
    #                 #print("Gene similarity:")
    #                 print(sim)
    #                 print(",")
    #
    #     self.SM_GO = np.matrix(SMArray)
    #     #set the diagonal elements of SM to 1
    #     #self.SM_GO = self.SM_GO+np.matrix(np.identity(self.num_nodes), copy=False)
    #     #print(self.SM_GO)


    def create_GOsim_SM(self, inp_gene2go_file, inp_GOsim_file):
        self.logger.debug("Debugging from inside create_GOSim_SM method of class GraphData_Gene.")

        #Read the GO-GO associations
        print("Creating GO terms dictionary.")
        #self.create_GO_relationship_dict(inp_GOsim_file)
        self.create_GO_relationship_matrix(inp_GOsim_file)
        print("GO terms dictionary created.")
        #Read the gene-GO associations
        print("Read Gene2go file.")
        geneid2gos = self.goea.load_GO_gene_associations_file_with_categories(inp_gene2go_file)
        print("Gene2go file read.")

        #Use gneid2gos and the GOsimdict created above to create SM_GO
        print("Creating SM_GO.")
        SMArray = np.zeros(shape=(self.num_nodes, self.num_nodes))
        for i in range(0, self.num_nodes):
            for j in range(0, self.num_nodes):
                sim = 0
                if i<j:
                    if self.node_dict[i].gene_id in geneid2gos and self.node_dict[j].gene_id in geneid2gos:
                        if len(geneid2gos[self.node_dict[i].gene_id][self.GO_TYPE]) != 0 and len(geneid2gos[self.node_dict[j].gene_id][self.GO_TYPE]) != 0:
                            sim = self.calculate_gene_sim(geneid2gos[self.node_dict[i].gene_id][self.GO_TYPE], geneid2gos[self.node_dict[j].gene_id][self.GO_TYPE])
                            #sim = self.gsesame_gene.scores(geneid2gos[self.node_dict[i].gene_id][self.GO_TYPE], geneid2gos[self.node_dict[j].gene_id][self.GO_TYPE])
                        else:
                            sim = 0


                    else:
                        sim = 0

                    SMArray[i,j] = sim
                    SMArray[j,i] = sim

                    print("Gene similarity:")
                    print(sim)
                    print(",")

        self.SM_GO = np.matrix(SMArray)
        print("SM_GO created.")


    #Save the matrix SM_GO (codes + labels) for later use
    def save_GOsim_SM(self, inp_filename_GOsim_codes, inp_filename_GOsim_labels):
        self.logger.debug("Debugging from inside save_GOsim_SM method of class GraphData_Gene.")

        target1 = open(inp_filename_GOsim_codes, 'a')
        target2 = open(inp_filename_GOsim_labels, 'a')

        for i in range(0, self.num_nodes):
            for j in range(0, self.num_nodes):
                if(i < j and self.SM[i, j] != -1 and self.SM[i, j] != 0):
                    target1.write(str(i))
                    target2.write(str(self.node_codes[i]))
                    target1.write(" ")
                    target2.write(" ")
                    target1.write(str(j))
                    target2.write(str(self.node_codes[j]))
                    target1.write(" ")
                    target2.write(" ")
                    target1.write(str(self.SM[i, j]))
                    target2.write(str(self.SM[i, j]))
                    target1.write("\n")
                    target2.write("\n")

    #Read GO relationships
    def create_GO_relationship_dict(self, inp_gosim_filename):
        self.logger.debug("Debugging from inside create_GO_matrix method of class GraphData_Gene.")

        ###########################
        # Read the relations file
        ###########################
        file_rels = pd.read_csv(
            filepath_or_buffer= inp_gosim_filename,
            header=None,
            sep=' ')

        file_rels.columns = ['goid1', 'goid2', 'resnick', 'lin', 'semantic', 'icnp']

        #Populate GOsim_dict with GO relationships
        for i in range(file_rels.shape[0]):
            gosim_score = GOsimscore(float(file_rels[self.GO_SIM_TYPE][i]))
            self.GOsim_dict.put_relationship_object(str(file_rels['goid1'][i]), str(file_rels['goid2'][i]), gosim_score)

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

    #Calculate score between two go lists related to two genes.
    def calculate_gene_sim(self, golist_1, golist_2):
        sim1 = 0
        for goterm in golist_1:
            sim1 = sim1 + self.calculate_goterm_golist_score(goterm, golist_2)
        sim2 = 0
        for goterm in golist_2:
            sim2 = sim2 + self.calculate_goterm_golist_score(goterm, golist_1)
        #print("sim1:")
        #print(str(sim1))
        #print("sim2:")
        #print(str(sim2))
        score = float(sim1 + sim2) / float(len(golist_1) + len(golist_2))
        return score

    #Calculate semantic similarity between a goterm and a golist.
    def calculate_goterm_golist_score(self, inp_goterm, inp_golist):
        scores = []
        for goterm in inp_golist:
            if goterm in self.GO_codes and inp_goterm in self.GO_codes:
                scores.append(self.GORels[self.GO_codes[inp_goterm], self.GO_codes[goterm]])
            # if self.GOsim_dict.contains_relationship(inp_goterm, goterm):
            #     scores.append(self.GOsim_dict.get_relationship_object(inp_goterm, goterm).sim_score)
        #check for empty scores list
        if len(scores) != 0:
            return max(scores)
        else:
            return 0

    def read_gene_synonyms_file(self, syn_filename):
        """Read yeast synonyms file and store in a dictionary."""
        ###########################
        # Read the synonyms file
        ###########################
        file_rels = pd.read_csv(
            filepath_or_buffer= syn_filename,
            header=None,
            sep='\t')

        file_rels.columns = ['geneid', 'gene_syns']

        for i in range(file_rels.shape[0]):
            gene_locustags = str(file_rels['gene_syns']).split("|")
            for gene_locustag in gene_locustags:
                self.gene_syn_dict[gene_locustag] = str(file_rels['geneid'][i])
