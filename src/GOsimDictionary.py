__author__ = 'divya'

class GOsimDictionary(object):
    def __init__(self):
        self.GOsim_dict = dict()

    def get_relationship_object(self, goid_1, goid_2):
        if goid_1 < goid_2:
            return self.GOsim_dict[(goid_1, goid_2)]
        else:
            return self.GOsim_dict[(goid_2, goid_1)]

    def put_relationship_object(self, goid_1, goid_2, simscore_object):
        if False == self.contains_relationship(goid_1, goid_2):
            if goid_1 < goid_2:
                self.GOsim_dict[(goid_1, goid_2)] = simscore_object
            else:
                self.GOsim_dict[(goid_2, goid_1)] = simscore_object

    def contains_relationship(self, goid_1, goid_2):
        if (goid_1, goid_2) in self.GOsim_dict or (goid_2, goid_1) in self.GOsim_dict:
            return True
        else:
            return False