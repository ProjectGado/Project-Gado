import logging, os, sys
from gado.functions import *

#Defintions
LOGGING_LEVEL = logging.ERROR

class Logger:
    
    def __init__(self, moduleName):
        
        #Make sure we have a logging directory we can write to
        try:
            path = os.mkdir(os.path.join(gadodir(), 'Logs'))
        except:
            if os.name == 'nt':
                path = os.path.join(gadodir(), 'Logs')
            else:
                path = os.path.join('.', 'Logs')
            pass
            
        #Get an instance of the logger with the passed in module name
        self.logger = logging.getLogger(moduleName)
        
        #Set the currently selected log level
        self.logger.setLevel(LOGGING_LEVEL)
        
        #Create the file handler
        fh = logging.FileHandler(os.path.join(path, 'gado.log'))
        fh.setLevel(LOGGING_LEVEL)
        
        # create console handler and set level to debug
        ch = logging.StreamHandler()
        ch.setLevel(LOGGING_LEVEL)
        
        # create formatter
        formatter = logging.Formatter('%(levelname)s - %(name)s - %(asctime)s: \n\t%(message)s\n')
        
        # add formatter to ch
        ch.setFormatter(formatter)
        fh.setFormatter(formatter)
        
        # add ch to logger
        self.logger.addHandler(ch)
        
        #Add the file handler to the logger
        self.logger.addHandler(fh)
        
    def getLoggerInstance(self):
        
        #Return an instance of the configured logger object
        return self.logger