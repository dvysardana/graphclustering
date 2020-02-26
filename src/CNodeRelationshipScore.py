__author__ = 'divya'

class CNodeRelationshipScore(object):
    def __init__(self):
        self.typeA_score = 0 #ycohesion_nsd_low
        self.typeB_score = 0 #ncohesion_ysd
        self.typeC_score = 0 #ncohesion_nsd_low
        self.typeD_score = 0 #ncohesion_nsd_high
        self.typeE_score = 0 #periphery-periphery
        self.typeF_score = 0 #ycohesion_nsd_high
        self.aggregate_type = ""
        self.composite_score = 0
        self.reverse_composite_score = 0
        self.composite_score_3 = 0
        self.edge_weight_score = 0
        self.structure_score = 0
        self.structure_score_1 = 0

    #Method to classify a periphery cnode type (A,B,C,D) based upon maximum type score
    def classify_periphery_cnode_type(self):
        type = ""
        max_score = max([self.typeA_score, self.typeB_score, self.typeC_score, self.typeD_score, self.typeF_score])
        if self.typeE_score != 0:
            type = "E"
        else:
            if max_score == self.typeA_score:
                type = "A"
            elif max_score == self.typeB_score:
                type = "B"
            elif max_score == self.typeC_score:
                type = "C"
            elif max_score == self.typeD_score:
                type = "D"
            elif max_score == self.typeF_score:
                type = "F"
        self.aggregate_type = type
        #return type