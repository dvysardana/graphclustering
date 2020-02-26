__author__ = 'divya'

from Phase2Data_WI import Phase2Data_WI
from Misc.go_enrichment_processor import go_enrichment_processor
from Misc.gsesame import GsesameGene, GsesameGO
from Misc.oboio import *
from CNodeData_WI_Gene import CNodeData_WI_Gene

class Phase2Data_WI_Gene(Phase2Data_WI):
    def __init__(self, graphdata, configdata, K, cnodes_dict, next_cluster_label, num_clusters):
        super(Phase2Data_WI_Gene, self).__init__(graphdata, configdata, K, cnodes_dict, next_cluster_label, num_clusters)

        self.goea = go_enrichment_processor()

        self.c_SM_GO = []

        GOFILE_all = "/Users/divya/Documents/input/Misc/go-basic.obo"
        OBIO = OboIO()
        TERMS = OBIO.get_graph(GOFILE_all)

        self.gsesame_gene = GsesameGene(TERMS)
        self.GO_TYPE = self.configdata.GO_TYPE  #GO term type used for calculating gene-gene functional similarity

        self.cnode_functional_sort_list = []

    def initialize_phase(self):
        self.configdata.logger.debug("Debugging from inside initialize_phase method of class Phase2Data_WI.")

        #Perform enrichment analysis for all cnodes from phase 1
        self.cnode_enrichment_processor()

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

    # #Override base class method to add filtering of clusters
    # def execute_phase(self):
    #     self.configdata.logger.debug("Debugging from inside Phase2Data_WI_Gene_Post class's execute_phase method.")
    #
    #     #execute phase
    #     self.MKNN_phase2_execute()
    #
    #     #merge highly overlapping cnodes
    #     self.MKNN_phase2_overlap()
    #
    #     self.filter_clusters()
    #
    #     #extract core periphery relationships
    #     self.extract_core_periphery_relationships()
    #
    #     #extract global core periphery relationships
    #     self.extract_global_core_periphery_relationships()

    #Prepare and perform enrichment for all cnodes from phase 1.
    def cnode_enrichment_processor(self):
        self.configdata.logger.debug("Debugging from inside perform_cnode_enrichment method of class Phase2Data_WI_Gene.")
        self.create_go_enrichment_object()
        self.perform_cnode_enrichment()

    #Create the go enrichment object.
    def create_go_enrichment_object(self):
        self.configdata.logger.debug("Logging from inside create_go_enrichment_object method from Phase2Data_WI_Gene class.")
        print("Creating enrichment object.")
        #Load GO file
        self.goea.obodag = self.goea.load_GO_file(self.configdata.go_obo_file)

        #Load GO-gene associations file
        self.goea.geneid2gos = self.goea.load_GO_gene_associations_file(self.configdata.gene2go_file)

        #Get GO enrichment object
        self.goea.goeaobj = self.goea.get_go_enrichment_object()

    #CNode enrichment processor
    def perform_cnode_enrichment(self):
        self.configdata.logger.debug("Debugging from inside cnode_enrichment method of class Phase2Data_WI_Gene")
        print('performing cnrichment analysis for all cnodes.')
        study_genes_set = set()
        for cnode_id, cnode_data in self.cnodes_dict.items():

            if cnode_data.active == True:

                #Get input geneset for enrichment
                study_genes_set = cnode_data.node_gene_id_locustag_dict

                #Output from enrichment analysis code: significant GO terms
                goea_results_sig = self.goea.run_goea(study_genes_set)
                """Get all study items (e.g., geneids)."""

                cnode_data.reset_gene_GO_terms_dict()
                for rec in goea_results_sig:
                    cnode_data.gene_GO_terms_dict[rec.NS].append(rec.GO)
                    #print(rec.GO)
                    #print("|")
                    #print(rec.NS)
                    #print("|")
                    #print(cnode_data.gene_GO_terms_dict[rec.NS])

    #Method to override super class method
    #to redirect code to use GO version of
    #c_SM calculation
    def calculate_c_SM(self):
        self.calculate_c_SM_GO()
        #self.calculate_c_SM_Zhen()
        #self.calculate_c_SM_WI_1()

    def calculate_c_SM_GO(self):
        self.configdata.logger.debug("Debugging from inside calculate_C_SM_GO method of Phase2Data_WI_Gene class.")

        self.c_SM_GO = [[-1] * self.num_clusters for i in range(self.num_clusters)]
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

                            #####################
                            #calculate self.c_SM_GO[cm_i][cm_j] over here
                            if(len(cnode_i.gene_GO_terms_dict[self.GO_TYPE]) != 0 and len(cnode_j.gene_GO_terms_dict[self.GO_TYPE]) != 0):
                                #self.c_SM_GO[cm_i][cm_j] = self.gsesame_gene.scores(cnode_i.gene_GO_terms_dict[self.GO_SIM_TYPE], cnode_j.gene_GO_terms_dict[self.GO_SIM_TYPE])
                                self.c_SM_GO[cm_i][cm_j] = self.calculate_gene_sim((cnode_i.gene_GO_terms_dict[self.GO_TYPE], cnode_j.gene_GO_terms_dict[self.GO_TYPE]))
                            else:
                                self.c_SM_GO[cm_i][cm_j] = 0
                            self.c_SM_GO[cm_j][cm_i] = self.c_SM_GO[cm_i][cm_j]

                            #print("semantic similarity:")
                            print(self.c_SM_GO[cm_i][cm_j])
                            #print(",")
                            ####################

                            # linkageij = 0
                            # shared_edgeset = cnode_i.calculate_shared_edge_set(cnode_j)
                            # #sum_shared = sum(shared_edgeset)
                            # sum_shared = cnode_i.calculate_sum_edgeset(shared_edgeset)
                            # if cnode_i.outsim == 0 or cnode_j.outsim == 0:
                            #     linkageij = 0
                            # else:
                            #     linkageij = (float)((float)(sum_shared)/(float)(cnode_i.outsim)) + (float)((float)(sum_shared)/(float)(cnode_j.outsim))
                            #
                            # #self.c_SM[i][j] = linkageij
                            # #self.c_SM[j][i] = linkageij
                            # self.c_SM[cm_i][cm_j] = linkageij
                            # self.c_SM[cm_j][cm_i] = linkageij
                            cm_j = cm_j + 1



                    cm_i = cm_i + 1

        self.c_SM = self.c_SM_GO
        print("c_SM generated.")


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
            if goterm in self.graphdata.GO_codes and inp_goterm in self.GO_codes:
                scores.append(self.graphdata.GORels[self.graphdata.GO_codes[inp_goterm], self.graphdata.GO_codes[goterm]])
            # if self.GOsim_dict.contains_relationship(inp_goterm, goterm):
            #     scores.append(self.GOsim_dict.get_relationship_object(inp_goterm, goterm).sim_score)
        #check for empty scores list
        if len(scores) != 0:
            return max(scores)
        else:
            return 0



    #Overriding the base class method for implementing phase 2 for GO
    #so as to use CNodeData_WI_Gene
    ##Old: and so as to add enrichment analysis step after each iteration.
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
                                    cnode_data_merged = CNodeData_WI_Gene(clabel_current, -1, -1, -1, self.graphdata, self.configdata)

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
                self.perform_cnode_enrichment()
                self.recalculate_matrices_for_Phase2_next_iteration()
            else:

                continueFlag = False
                break

            #If next_clusterLabel in previous iteration = next cluster label in current iteration:
            #end the loop, else
            #Recalculate cluster initiator order.
            #Recalculate MKNN neighbors for each node.

    #Calculate avg. gene pair functional similarity per cluster
    def filter_clusters(self):
        for cnode_id, cnode_data in self.cnodes_dict.items():
            if cnode_data.active == True and cnode_data.num_nodes >= 3:
                cnode_data.calculate_avg_func_gene_pair_sim()
                self.cnode_functional_sort_list.append((cnode_id, cnode_data.avg_func_gene_pair_sim))
                if cnode_data.avg_func_gene_pair_sim < self.configdata.SIM_CUTOFF:
                    cnode_data.active = False
                    self.num_clusters = self.num_clusters - 1

        self.cnode_functional_sort_list = sorted(self.cnode_functional_sort_list, key = lambda x:x[1], reverse = True)

        target1 = open("/Users/divya/Documents/output/Dissertation/manual/Semisupervised/Postprocessing/cnode_func_sim_GMKNN.txt", 'a')
        for (cnode_id, func_sim) in self.cnode_functional_sort_list:
            target1.write(str(cnode_id))
            target1.write(" ")
            target1.write(str(self.cnodes_dict[cnode_id].num_nodes))
            target1.write(" ")
            target1.write(str(func_sim))
            target1.write("\n")
