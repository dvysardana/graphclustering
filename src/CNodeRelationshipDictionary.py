__author__ = 'divya'

class CNodeRelationshipDictionary(object):
    def __init__(self):
        self.cnode_relationship_dict = dict()

    def get_relationship_object(self, cnode_1, cnode_2):
        if cnode_1 < cnode_2:
            return self.cnode_relationship_dict[(cnode_1, cnode_2)]
        else:
            return self.cnode_relationship_dict[(cnode_2, cnode_1)]

    def put_relationship_object(self, cnode_1, cnode_2, relationship_object):
        if False == self.contains_relationship(cnode_1, cnode_2):
            if cnode_1 < cnode_2:
                self.cnode_relationship_dict[(cnode_1, cnode_2)] = relationship_object
            else:
                self.cnode_relationship_dict[(cnode_2, cnode_1)] = relationship_object

    def contains_relationship(self, cnode_1, cnode_2):
        if (cnode_1, cnode_2) in self.cnode_relationship_dict or (cnode_2, cnode_1) in self.cnode_relationship_dict:
            return True
        else:
            return False


