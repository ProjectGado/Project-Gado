'''
Created on Dec 3, 2010

@author: Tom Smith
'''
import json as j

class RobotData(object):
    '''
    classdocs
    '''
    arm_pos = None
    actuator_pos_d = None
    actuator_pos_s = None
    pump_level = None
    light_value = None
    last_level = None
    pump_current = None

    def __init__(self):
        '''
        Constructor
        '''
        
    def processJSON(self, json):
        in_data = j.loads(json)
        self.arm_pos = in_data['arm_pos']
        self.actuator_pos_d = in_data['actuator_pos_d']
        self.actuator_pos_s = in_data['actuator_pos_s']
        self.pump_level = in_data['pump_level']
        self.light_value = in_data['light_value']
        self.last_level = in_data['last_level']
        self.pump_current = in_data['pump_current']
        
        
        
        