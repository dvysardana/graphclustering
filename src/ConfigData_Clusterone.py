__author__ = 'divya'

from ConfigData import ConfigData

class ConfigData_Clusterone(ConfigData):

    def __init__(self, code_dir, data_dir, log_dir):
        super(ConfigData_Clusterone, self).__init__(code_dir, data_dir, log_dir)

    def do_config(self):
        self.do_config_variables()
        self.do_config_logger()
        self.do_config_clusterone()

    def do_config_clusterone(self):
        pass


