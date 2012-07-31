import serial

class Robot(object):
    
    #Globals
    global serialConnection
    global settings
    
    #Constants
    MOVE_ARM = 'a'
    MOVE_ACTUATOR = 's'
    MOVE_VACUUM = 'v'
    LOWER_AND_LIFT = 'l'
    
    def __init__(self, commPort, settings):
        #Grab settings
        self.settings = settings
        
        #Initialize the serial connection to the robot
        self.serialConnection = serial.Serial(commPort, self.settings['baudrate'])
        
    #Move the robot's arm to the specified degree (between 0-180)
    def moveArm(self, degree):
        self.serialConnection.write("%s%s" % (degree, self.MOVE_ARM))
    
    #Move the robot's actuator to the specified stroke
    def moveActuator(self, stroke):
        self.serialConnection.write("%s%s" % (stroke, self.MOVE_ACTUATOR))
    
    #Turn on the vacuum to the power level: value
    def moveVacuum(self, value):
        self.serialConnection.write("%s%s" % (value, self.MOVE_VACUUM))        
    
    #Reset the arm to the home position
    def resetArm(self):
        self.serialConnection.write("%s%s" % (self.settings['arm_home_value'], self.MOVE_ARM))
        
    #Reset the actuator to the home position
    def resetActuator(self):
        self.serialConnection.write("%s%s" % (self.settings['actuator_home_value'], self.MOVE_ACTUATOR))
    
    #Move the actuator until the click sensor is engaged, then turn on the vacuum and raise
    #the actuator. The bulk of this code is going to be executed from the arduino's firmware
    def pickUpObject(self):
        self.serialConnection.write("%s" % self.LOWER_AND_LIFT)
    
    #Start the robot's scanning procedure
    def start(self):
        
        #reset the robot to the default values
        self.reset()
        
        ##CODE TO TAKE A PICTURE OF THE BACK OF TEH IMAGE##
        
        ##CHECK TO SEE IF WE FOUND A BARCODE (END OF STACK)##
        
        ##IF NOT, LOWER AND LIFT##
        self.pickUpObject()
        
        ##MOVE TO SCANNER AND DROP UNTIL WE HIT IT##
        self.moveArm(self.settings['scanner_location'])
        #self.pickUpObject()
        
        ##TURN ON SCANNER AND SCAN THE IMAGE##
        
        ##LIFT ACTUATOR##
        
        ##MOVE ARM TO OUTPUT POSITION##
        
        ##REMOVE POWER TO VACUUM##
        
    
    #Pause the robot in its current step
    def pause(self):
        pass
    
    #Stop the robot process and reset
    def stop(self):
        pass
    
    #Reset all aspects of the robot
    def reset(self):
        self.resetArm()
        self.resetActuator()