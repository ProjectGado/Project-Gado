import logging

#Defintions
LOGGING_LEVEL = logging.DEBUG

class Logger:
    
    def __init__(self, moduleName):
        
        self.logger = logging.getLogger(moduleName)
        
        self.logger.setLevel(LOGGING_LEVEL)
        
        # create console handler and set level to debug
        ch = logging.StreamHandler()
        ch.setLevel(LOGGING_LEVEL)
        
        # create formatter
        formatter = logging.Formatter('%(levelname)s - %(name)s - %(asctime)s: \n\t%(message)s\n')
        
        # add formatter to ch
        ch.setFormatter(formatter)
        
        # add ch to logger
        self.logger.addHandler(ch)
        
    def getLoggerInstance(self):
        
        return self.logger