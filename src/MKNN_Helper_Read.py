__author__ = 'divya'

from MKNN_Helper import MKNN_Helper
from ConfigData import ConfigData

import pandas as pd
import numpy as np
import os

import pygraphml
from pygraphml import Graph
from pygraphml import GraphMLParser
import lxml.etree as et

class MKNN_Helper_Read(MKNN_Helper):

    ###################################################

    def __init__(self):
        super(MKNN_Helper_Read, self).__init__()
        self.raw_filename_karate_dataset = MKNN_Helper.configdata.inp_raw_file
        self.raw_filename_faculty_dataset = MKNN_Helper.configdata.inp_raw_file_faculty_dataset
        self.raw_filename_mips_gold_standard = MKNN_Helper.configdata.raw_mips_gold_standard_file
        self.inp_rel_filename = MKNN_Helper.configdata.inp_rel_file
        self.raw_filename_yeast_evolutionary_rates = MKNN_Helper.configdata.raw_yeast_evolutionary_rates_file
        self.raw_filename_yeast_evolutionary_rates_1 = MKNN_Helper.configdata.raw_yeast_evolutionary_rates_file_1
        self.raw_filename_essential_genes = MKNN_Helper.configdata.raw_essential_genes_file
        self.raw_filename_phyletic_age = MKNN_Helper.configdata.raw_phyletic_age_file
        self.raw_filename_les_miserables = MKNN_Helper.configdata.inp_raw_file_les_miserables

        self.relationship_dict = {}

    def read_Zachary_raw_file(self):
        inp_rel_file = os.path.split(self.raw_filename_karate_dataset)[0] + "/" + os.path.split(self.raw_filename_karate_dataset)[1].split(".")[0] + ".txt"
        target = open(inp_rel_file, 'a')
        ###########################
        # Read the relations file
        ###########################
        print("raw filename")
        print(str(self.raw_filename_karate_dataset))
        print("output filename")
        print(str(inp_rel_file))
        array_file_raw = np.loadtxt(self.raw_filename_karate_dataset)
        num_nodes = array_file_raw.shape[1]
        print(str(num_nodes))

        for i in range(0, num_nodes):
            for j in range(0, num_nodes):
                if(i < j and array_file_raw[34+i][j] != 0):
                    print(str(array_file_raw[34+i][j]))
                    print(",")
                    target.write(str(i+1))
                    target.write(" ")
                    target.write(str(j+1))
                    target.write(" ")
                    target.write(str(((int)(array_file_raw[34+i][j])/10)))
                    target.write("\n")
            print("Row ends")


    #Read a raw graphml file.
    #Min and Max are to be used for normalizing the file
    def read_graphml_dataset_raw_file(self, raw_graphml_filename, mini, maxi):
        # parser = GraphMLParser()
        # g = parser.parse(self.raw_filename_faculty_dataset)
        # nodes = g.BFS()
        # for node in nodes:
        #     print(node)
        #
        # nodes = g.DFS_prefix()
        # for node in nodes:
        #     print(node)
        #g.show()

        inp_rel_file = os.path.split(str(raw_graphml_filename))[0] + "/" + os.path.split(str(raw_graphml_filename))[1].split(".")[0] + ".txt"
        target = open(inp_rel_file, 'a')


        graphml = {
        "graph": "{http://graphml.graphdrawing.org/xmlns}graph",
        "node": "{http://graphml.graphdrawing.org/xmlns}node",
        "edge": "{http://graphml.graphdrawing.org/xmlns}edge",
        "data": "{http://graphml.graphdrawing.org/xmlns}data",
        "label": "{http://graphml.graphdrawing.org/xmlns}data[@key='label']",
        "x": "{http://graphml.graphdrawing.org/xmlns}data[@key='x']",
        "y": "{http://graphml.graphdrawing.org/xmlns}data[@key='y']",
        "size": "{http://graphml.graphdrawing.org/xmlns}data[@key='size']",
        "r": "{http://graphml.graphdrawing.org/xmlns}data[@key='r']",
        "g": "{http://graphml.graphdrawing.org/xmlns}data[@key='g']",
        "b": "{http://graphml.graphdrawing.org/xmlns}data[@key='b']",
        "weight": "{http://graphml.graphdrawing.org/xmlns}data[@key='weight']",
        "group": "{http://graphml.graphdrawing.org/xmlns}data[@key='group']",
        "id": "{http://graphml.graphdrawing.org/xmlns}data[@key='id']",
        "edgeid": "{http://graphml.graphdrawing.org/xmlns}data[@key='edgeid']"
        }

        tree = et.parse(raw_graphml_filename)
        root = tree.getroot()
        graph = tree.find(graphml.get("graph"))
        nodes = graph.findall(graphml.get("node"))
        edges = graph.findall(graphml.get("edge"))

        node_codes = {}
        code = 0
        for node in nodes:
            attribs = {}
            for data in node.findall(graphml.get('data')):
                #print(data.text)
                attribs[data.get('key')] = data.text
                print((attribs['name']))
                print(",")
                node_codes[str(code)] = attribs['name']
                code = code + 1
                break

        for edge in edges:
            attribs = {}
            #print(edge.attrib['source'], edge.attrib['target'])
            for data in edge.findall(graphml.get('data')):
                attribs[data.get('key')] = data.text
            #print('Edge', edge, 'have weight =', attribs['weight'])

            if self.contains_relationship(node_codes[str(edge.attrib['source'])[1:]], node_codes[str(edge.attrib['target'])[1:]]) == False:
                #self.put_relationship(str(edge.attrib['source'])[1:], str(edge.attrib['target'])[1:], (float)(attribs['weight']))
                self.put_relationship(node_codes[str(edge.attrib['source'])[1:]], node_codes[str(edge.attrib['target'])[1:]], (float)(attribs['weight']))

            else:
                #edge_weight = self.get_relationship(str(edge.attrib['source'])[1:], str(edge.attrib['target'])[1:])
                edge_weight = self.get_relationship(node_codes[str(edge.attrib['source'])[1:]], node_codes[str(edge.attrib['target'])[1:]])
                #edge_weight = edge_weight + (int) (attribs['weight'])
                edge_weight = max(edge_weight, (int) (attribs['weight']))
                self.put_relationship(node_codes[str(edge.attrib['source'])[1:]], node_codes[str(edge.attrib['target'])[1:]], edge_weight)

        #min and max calculated externally so as to leave a gap from
        #actual min and max values to avoid 0 and 1 edge weights.
        #mini = 0
        #maxi = 20

        #Write relationships file
        for (source_node, target_node), edge_weight in self.relationship_dict.items():
            target.write(source_node)
            target.write(" ")
            target.write(target_node)
            target.write(" ")
            target.write(str(self.normalize_value(edge_weight, mini, maxi)))
            target.write("\n")


    def get_relationship(self, node_1, node_2):
        if node_1 < node_2:
            return self.relationship_dict[(node_1, node_2)]
        else:
            return self.relationship_dict[(node_2, node_1)]

    def put_relationship(self, node_1, node_2, edge_weight):
        if node_1 < node_2:
            self.relationship_dict[(node_1, node_2)] = edge_weight
        else:
            self.relationship_dict[(node_2, node_1)] = edge_weight

    def contains_relationship(self, node_1, node_2):
        if (node_1, node_2) in self.relationship_dict or (node_2, node_1) in self.relationship_dict:
            return True
        else:
            return False

    def normalize_value(self, value, min, max):
        return ((float)(value-min)/(float)(max-min))

    def read_node_codes(self):
        inp_filename_node_codes = os.path.split(self.inp_rel_filename)[0] + "/expanded/" + os.path.split(self.inp_rel_filename)[1].split(".")[0] + "_node_codes.txt"
        node_codes_dict = {}

        df = pd.read_csv(inp_filename_node_codes,sep=' ', header = None)
        array_file_codes = np.array(df)

        #array_file_codes = np.loadtxt(inp_filename_node_codes, delimiter=' ')
        #array_file_codes = np.loadtxt(inp_filename_node_codes, delimiter=' ', dtype={'names': ('code', 'node'),'formats': (np.int, '|S15' )})
        num_nodes = array_file_codes.shape[0]
        #num_columns = array_file_codes.shape[0]
        #print(str(num_nodes))
        #print(str(num_columns))
        for i in range(0, num_nodes):
            node_codes_dict[int(array_file_codes[i][1])] = int(array_file_codes[i][0])
            #print(array_file_codes[i][1], str(array_file_codes[i][0]))

        return node_codes_dict

    #Keeping codes as strings
    def read_node_codes_1(self):
        inp_filename_node_codes = os.path.split(self.inp_rel_filename)[0] + "/expanded/" + os.path.split(self.inp_rel_filename)[1].split(".")[0] + "_node_codes.txt"
        node_codes_dict = {}

        df = pd.read_csv(inp_filename_node_codes,sep=' ', header=None)
        array_file_codes = np.array(df)

        #array_file_codes = np.loadtxt(inp_filename_node_codes, delimiter=' ')
        #array_file_codes = np.loadtxt(inp_filename_node_codes, delimiter=' ', dtype={'names': ('code', 'node'),'formats': (np.int, '|S15' )})
        num_nodes = array_file_codes.shape[0]
        #num_columns = array_file_codes.shape[0]
        #print(str(num_nodes))
        #print(str(num_columns))
        for i in range(0, num_nodes):
            node_codes_dict[array_file_codes[i][1]] = array_file_codes[i][0]
            #print(array_file_codes[i][1], str(array_file_codes[i][0]))

        return node_codes_dict



    #Generate Gold standard file for faculty dataset
    def generate_faculty_dataset_gold_standard_file(self):

        gold_standard_file = "/Users/divya/Documents/input/Dissertation/goldstandard/Real/" + os.path.split(self.raw_filename_faculty_dataset)[1].split(".")[0] + "_gold_standard.txt"

        target = open(gold_standard_file, 'a')

        #Parse the graphml file
        graphml = {
        "graph": "{http://graphml.graphdrawing.org/xmlns}graph",
        "node": "{http://graphml.graphdrawing.org/xmlns}node",
        "edge": "{http://graphml.graphdrawing.org/xmlns}edge",
        "data": "{http://graphml.graphdrawing.org/xmlns}data",
        "label": "{http://graphml.graphdrawing.org/xmlns}data[@key='label']",
        "x": "{http://graphml.graphdrawing.org/xmlns}data[@key='x']",
        "y": "{http://graphml.graphdrawing.org/xmlns}data[@key='y']",
        "size": "{http://graphml.graphdrawing.org/xmlns}data[@key='size']",
        "r": "{http://graphml.graphdrawing.org/xmlns}data[@key='r']",
        "g": "{http://graphml.graphdrawing.org/xmlns}data[@key='g']",
        "b": "{http://graphml.graphdrawing.org/xmlns}data[@key='b']",
        "weight": "{http://graphml.graphdrawing.org/xmlns}data[@key='weight']",
        "group": "{http://graphml.graphdrawing.org/xmlns}data[@key='group']",
        "id": "{http://graphml.graphdrawing.org/xmlns}data[@key='id']",
        "edgeid": "{http://graphml.graphdrawing.org/xmlns}data[@key='edgeid']"
        }

        tree = et.parse(self.raw_filename_faculty_dataset)
        root = tree.getroot()
        graph = tree.find(graphml.get("graph"))
        nodes = graph.findall(graphml.get("node"))
        edges = graph.findall(graphml.get("edge"))

        #Read the node codes
        node_codes_dict = self.read_node_codes()

        #Write gold standard file
        for node in nodes:
            attribs = {}
            print(node.attrib['id'])
            for data in node.findall(graphml.get('data')):
                attribs[data.get('key')] = data.text
            print('Node', node, 'have group', attribs['group'])
            target.write(attribs['group'])
            target.write(" ")
            target.write(str(node.attrib['id'])[1:])
            target.write(" ")
            target.write(str(node_codes_dict[int(str(node.attrib['id'])[1:])]))
            target.write("\n")

    #Method to generate gold standard file for Collins, Gavin, Krogan and Krogan_extended datasets
    def generate_PPI_gold_standard_file(self):
        gold_standard_file = "/Users/divya/Documents/input/Dissertation/goldstandard/Real/" + os.path.split(self.inp_rel_filename)[1].split(".")[0] + "_gold_standard.txt"

        cluster_codes_file = "/Users/divya/Documents/input/Dissertation/goldstandard/Real/" + os.path.split(self.inp_rel_filename)[1].split(".")[0] + "_MIPS_complex_codes.txt"


        target = open(gold_standard_file, 'a')

        target1 = open(cluster_codes_file, 'a')

        df = pd.read_csv(self.raw_filename_mips_gold_standard,sep=',', header=None)
        array_file_raw = np.array(df)
        #ßarray_file_raw = np.loadtxt(self.raw_filename_mips_gold_standard, delimiter=',')
        num_cols = array_file_raw.shape[1]
        num_rows = array_file_raw.shape[0]
        print("num_rows:")
        print(str(num_rows))
        print("num_cols:")
        print(str(num_cols))

        #Read the node codes
        node_codes_dict = self.read_node_codes_1()

        mips_complexes_dict = {}
        next_complex_no = 0
        protein_id = 0

        for i in range(0, num_rows):

            if(str(array_file_raw[i][1]) in mips_complexes_dict):
                complex_no = mips_complexes_dict[str(array_file_raw[i][1])]
            else:
                print('complex name:')
                print(str(array_file_raw[i][1]))
                print(str(next_complex_no))
                print(str(array_file_raw[i][0]))
                mips_complexes_dict[str(array_file_raw[i][1])] = next_complex_no
                complex_no = next_complex_no
                next_complex_no = next_complex_no + 1

                    #print(str(complex_no))

            if str(array_file_raw[i][0]) in node_codes_dict:
                target.write(str(complex_no))
                target.write(" ")
                target.write(str(node_codes_dict[str(array_file_raw[i][0])]))
                target.write(" ")
                target.write(str(array_file_raw[i][0]))
                target.write("\n")
            else:
                target.write(str(complex_no))
                target.write(" ")
                target.write(str(protein_id))
                target.write(" ")
                target.write(str(array_file_raw[i][0]))
                target.write("\n")
                protein_id = protein_id + 1

            #print("Row ends")

        self.write_cluster_codes_file(target1, mips_complexes_dict)

    #Method to write cluster codes file for Collins, Gavin, Krogan and Krogan_extended datasets.
    def write_cluster_codes_file(self, target, cluster_codes_dict):
        for complex_name, complex_code in cluster_codes_dict.items():
            target.write(str(complex_code))
            target.write(" ")
            target.write(complex_name)
            target.write("\n")

    #Generate yeast evolutionary rates file with codes for each PPI dataset
    def generate_PPI_yeast_evolutionary_rates_file(self):

        evol_rates_file = "/Users/divya/Documents/input/Dissertation/goldstandard/Real/" + os.path.split(self.inp_rel_filename)[1].split(".")[0] + "_evol_rates.txt"

        target = open(evol_rates_file, 'a')

        df = pd.read_csv(self.raw_filename_yeast_evolutionary_rates_1,sep='\t')
        array_file_raw = np.array(df)
        #ßarray_file_raw = np.loadtxt(self.raw_filename_mips_gold_standard, delimiter=',')
        num_cols = array_file_raw.shape[1]
        num_rows = array_file_raw.shape[0]

        #Read the node codes
        node_codes_dict = self.read_node_codes_1()

        evol_rates_dict = {}

        for i in range(0, num_rows):

            if(str(array_file_raw[i][0]) in evol_rates_dict):
                pass
                #complex_no = mips_complexes_dict[str(array_file_raw[i][1])]
            else:
                evol_rates_dict[str(array_file_raw[i][0])] = float(array_file_raw[i][1])

        count_found = 0
        for yeast in node_codes_dict:
            if yeast in evol_rates_dict:
                count_found = count_found + 1
                target.write(str(node_codes_dict[yeast]))
                target.write(" ")
                target.write(str(yeast))
                target.write(" ")
                target.write(str(evol_rates_dict[yeast]))
                target.write("\n")
            else:
                target.write(str(node_codes_dict[yeast]))
                target.write(" ")
                target.write(str(yeast))
                target.write(" ")
                target.write("-1")
                target.write("\n")


        print("Number of yeasts in dataset:")
        print(str(len(node_codes_dict)))
        print("Count found:")
        print(str(count_found))

    #Generate yeast evolutionary rates file with codes for each PPI dataset
    def generate_PPI_essential_genes_file(self):

        essential_genes_file = "/Users/divya/Documents/input/Dissertation/goldstandard/Real/" + os.path.split(self.inp_rel_filename)[1].split(".")[0] + "_essentiality.txt"

        target = open(essential_genes_file, 'a')

        df = pd.read_csv(self.raw_filename_essential_genes,sep='\t')
        array_file_raw = np.array(df)
        #ßarray_file_raw = np.loadtxt(self.raw_filename_mips_gold_standard, delimiter=',')
        num_cols = array_file_raw.shape[1]
        num_rows = array_file_raw.shape[0]

        #Read the node codes
        node_codes_dict = self.read_node_codes_1()

        essentiality_dict = {}

        for i in range(0, num_rows):
            if('Saccharomyces cerevisiae' in str(array_file_raw[i][0])):
                if(str(array_file_raw[i][3]) in essentiality_dict):
                    pass
                    #complex_no = mips_complexes_dict[str(array_file_raw[i][1])]
                else:
                    essentiality_dict[str(array_file_raw[i][3])] = str(array_file_raw[i][4])

        count_found = 0
        for yeast in node_codes_dict:
            if yeast in essentiality_dict:
                count_found = count_found + 1
                target.write(str(node_codes_dict[yeast]))
                target.write(" ")
                target.write(str(yeast))
                target.write(" ")
                target.write(str(essentiality_dict[yeast]))
                target.write("\n")
            else:
                target.write(str(node_codes_dict[yeast]))
                target.write(" ")
                target.write(str(yeast))
                target.write(" ")
                target.write("N")
                target.write("\n")


        print("Number of yeasts in dataset:")
        print(str(len(node_codes_dict)))
        print("Count found in essential_genes file:")
        print(str(count_found))

    #Generate yeast evolutionary rates file with codes for each PPI dataset
    def generate_PPI_phyletic_age_file(self):

        phyletic_age_file = "/Users/divya/Documents/input/Dissertation/goldstandard/Real/" + os.path.split(self.inp_rel_filename)[1].split(".")[0] + "_phyletic_age.txt"

        target = open(phyletic_age_file, 'a')

        df = pd.read_csv(self.raw_filename_phyletic_age,sep='\t')
        array_file_raw = np.array(df)
        #ßarray_file_raw = np.loadtxt(self.raw_filename_mips_gold_standard, delimiter=',')
        num_cols = array_file_raw.shape[1]
        num_rows = array_file_raw.shape[0]

        #Read the node codes
        node_codes_dict = self.read_node_codes_1()

        phyletic_age_dict = {}

        for i in range(0, num_rows):
            if('Saccharomyces cerevisiae' in str(array_file_raw[i][0])):
                if(str(array_file_raw[i][2]) in phyletic_age_dict):
                    pass
                    #complex_no = mips_complexes_dict[str(array_file_raw[i][1])]
                else:
                    phyletic_age_dict[str(array_file_raw[i][2])] = str(array_file_raw[i][3])

        count_found = 0
        for yeast in node_codes_dict:
            if yeast in phyletic_age_dict:
                count_found = count_found + 1
                target.write(str(node_codes_dict[yeast]))
                target.write(" ")
                target.write(str(yeast))
                target.write(" ")
                target.write(str(phyletic_age_dict[yeast]))
                target.write("\n")
            else:
                target.write(str(node_codes_dict[yeast]))
                target.write(" ")
                target.write(str(yeast))
                target.write(" ")
                target.write("-1")
                target.write("\n")


        print("Number of yeasts in dataset:")
        print(str(len(node_codes_dict)))
        print("Count found in phyletic_age file:")
        print(str(count_found))

if __name__ == "__main__":
    gc = MKNN_Helper_Read()
    #Generate relationship file for Faculty dataset
    #gc.read_Zachary_raw_file()

    #Generate relationships file for Faculty dataset
    #gc.read_graphml_dataset_raw_file(gc.raw_filename_faculty_dataset, 0, 20)

    #Generate gold standard file and complex codes file
    # for PPI dataset.
    #This has to be done after the relationship file
    #and the node codes file have been generated.
    #gc.generate_PPI_gold_standard_file()

    #Generate evolutionary codes file for proteins:
    #gc.generate_PPI_yeast_evolutionary_rates_file()

    #Generate essentiality information about proteins
    #gc.generate_PPI_essential_genes_file()

    #Generate phyletic age information about proteins
    #gc.generate_PPI_phyletic_age_file()

    #Generate relationships file for Literature dataset les miserables
    gc.read_graphml_dataset_raw_file(gc.raw_filename_les_miserables, 0, 20)