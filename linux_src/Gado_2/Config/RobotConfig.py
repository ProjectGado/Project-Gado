'''
Created on Oct 11, 2011

@author: Bootup Baltimore
'''
import json
import re
class RobotConfig(object):
    '''
    classdocs
    '''
    c = None

    def __init__(self):
        '''
        Constructor
        '''
        file = open('./Config/robot_config.txt')
        file_contents = file.read()
        file_contents = re.sub('\s', '', file_contents)
        file_contents = str(file_contents)
        self.c = json.loads(file_contents)
            
        
