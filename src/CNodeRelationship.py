__author__ = 'divya'

class CNodeRelationship(object):
    def __init__(self, cnode1_id, cnode2_id, relationship_type, relationship_score):
        self.cnode1_id = cnode1_id
        self.cnode2_id = cnode2_id
        self.relationship_type = relationship_type
        self.relationship_score = relationship_score