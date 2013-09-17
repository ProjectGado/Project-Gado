'''
Created on Aug 17, 2010

@author: Tom Smith
'''

import serial
import time
import RobotData
import Config.RobotConfig


class Robot(object):
    '''
    classdocs
    '''
    com_port = ''
    ser = ''
    data = RobotData.RobotData()
    conf = None
    props = None

    """ My configuration """



    def __init__(self, com_port):
        '''
        Constructor
        '''
        self.com_port = com_port
        self.ser = serial.Serial(com_port, 115200)
        self.conf = Config.RobotConfig.RobotConfig()
        self.props = self.conf.c['robot_props']
        
    def connect(self):
        self.sendCommand('d')
        
    def goHome(self):
        self.sendRawActuatorWithBlocking(self.props['actuator_home_pos'])
        #self.sendRawActuatorWithBlocking(150)
        self.sendRawArmWithoutBlocking(self.props['arm_home_pos'])
        time.sleep(float(self.props['arm_traverse_time']))
        
    def sendRawActuatorWithoutBlocking(self, position):
        self.sendCommand("%ss" % (position), False)
        
    def sendRawActuatorWithBlocking(self, position):
        """ s command """
        self.sendCommand("%ss" % position, True)
        last_actuator_s = self.data.actuator_pos_s
        time.sleep(.5)
        self.sendCommand("d", True)
        while abs(int(self.data.actuator_pos_s) - int(last_actuator_s)) > 1:
            time.sleep(.1)
            last_actuator_s = self.data.actuator_pos_s
            self.sendCommand("d", True)
            
    def sendRawArmWithoutBlocking(self, position):
        self.sendCommand("%sa" % position, True)

    def sendRawArmTimeBlocking(self, position):
        degrees_to_cover = abs(int(self.data.arm_pos) - int(position))
        self.sendCommand("%sa" % position, True)
        seconds_per_degree = float(self.props['arm_traverse_time']) / float(self.props['arm_traverse_degrees'])
        total_time = float(degrees_to_cover) * float(seconds_per_degree)
        time.sleep(total_time)
            
    def sendVacuum(self, value):
        self.sendCommand("%sv" % value, True)
        
    def lowerAndLiftInternal(self):   
        self.sendCommand("l", True)    
            
    def sendCommand(self, command, read=True):
         '''Sends a command to the robot'''
         print command
         self.ser.write(command)
         ser_in = ''
         #Wait until the robot has completed the command
         if read:
             while(ser_in == ""):
                 ser_in = self.ser.readline()
                 #print ser_in
                 if ser_in[0] == "{":
                     self.data.processJSON(ser_in)
                     self.status = ser_in