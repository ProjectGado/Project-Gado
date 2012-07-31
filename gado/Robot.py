import serial
import RobotData
import Config.RobotConfig

class Robot(object):
    
    #Globals
    global serialConnection
    
    #Constants
    MOVE_ARM = 'a'
    MOVE_ACTUATOR = 's'
    
    def __init__(self, commPort):
        #Initialize the serial connection to the robot
        self.serialConnection = serial.Serial(commPort, 115200)
        
    def moveArm(self, degree):
        self.serialConnection.write("%s%s" % (degree, self.MOVE_ARM))
        
    def moveActuator(self, stroke):
        self.serialConnection.write("%s%s" % (stroke, self.MOVE_ACTUATOR))