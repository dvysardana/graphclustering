__author__ = 'divya'

import logging as lg

#All configuration for the logger lies here
class logger_class:
    currentdate_str = ''
    log_dir = ''
    log_level = ''

    def __init__(self, currentdate, log_dir, logger_level):
        self.currendate = currentdate
        self.log_dir = log_dir
        self.log_level = logger_level

    def get_logger(self, name):

        handler_file_name = self.log_dir + '/'+ 'GMKNN' + self.currentdate_str + '.log'

        logger = lg.getLogger(name)

        #create a logging format
        formatter = lg.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

        #create a file handler
        handler_file = lg.FileHandler(handler_file_name)
        handler_file.setFormatter(formatter)

        #create a stream handler
        handler_console = lg.StreamHandler()
        handler_console.setFormatter(formatter)

        #set the logger level
        if self.log_level == 'INFO':
            logger.setLevel(lg.INFO)
            handler_file.setLevel(lg.INFO)
            handler_console.setLevel(lg.INFO)
            logger.addHandler(handler_console)
        else:
            logger.setLevel(lg.DEBUG)
            handler_file.setLevel(lg.DEBUG)


        #add the handlers to the logger
        logger.addHandler(handler_file)

        #logger.info("Testing logger with a handler")

        return logger