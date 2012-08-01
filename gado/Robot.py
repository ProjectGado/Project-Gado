import serial


#Constants
MOVE_ARM = 'a'
MOVE_ACTUATOR = 's'
MOVE_VACUUM = 'v'

HANDSHAKE = '0' # checks to see if we're actually talking to the robot
LOWER_AND_LIFT = 'l' # runs a routine on the robot to pick up an artifact
PLACE_ON_SCANNER = '2' # runs a routine to move an artifact to the scanner
DROP_ON_OUT_PILE = '3' # runs a routine to drop on the out pile
RESET_TO_HOME = '4' # runs a routine to move the arm home

class Robot(object):
    #Globals
    global serialConnection
    global settings
    
    
    def __init__(self, arm_home_value, arm_in_value, arm_out_value, actuator_home_value, baudrate, **kargs):
        #Grab settings
        self.arm_home_value = arm_home_value
        self.arm_in_value = arm_in_value
        self.arm_out_value = arm_out_value
        self.actuator_home_value = actuator_home_value
        self.baudrate = baudrate
        self.serialConnection = None
        
        
    def connect(self, port):
        '''
        Connects to the physcial robot on a certain COM port
        Returns true if it hears back correctly, else false
        '''
        
        serialConnection = serial.Serial(port, self.baudrate)
        if serialConnection.isOpen():
            serialConnection.write(HANDSHAKE)
            # HOW DO WE RECEIVE A RESPONSE?
            success = True
            if success:
                serialConnection.write(RESET_TO_HOME)
                self.serialConnection = serialConnection
                return True
        return False
    
    def disconnect(self):
        pass
    
    def connected(self):
        '''
        Checks to see if the robot is connected
        '''
        if self.serialConnection:
            serialConnection.write(HANDSHAKE)
            success = True
            # HOW DO WE RECEIVE A RESPONSE?
            if success:
                return True
        self.serialConnection = False
        return False
    
    
    #Move the robot's arm to the specified degree (between 0-180)
    def _moveArm(self, degree):
        self.serialConnection.write("%s%s" % (degree, self.MOVE_ARM))
    
    #Move the robot's actuator to the specified stroke
    def _moveActuator(self, stroke):
        self.serialConnection.write("%s%s" % (stroke, self.MOVE_ACTUATOR))
    
    #Turn on the vacuum to the power level: value
    def _vacuumOn(self, boolean):
        '''
            
        '''
        self.serialConnection.write("%s%s" % (value, self.MOVE_VACUUM))        
    
    #Reset the robot to the home position
    def reset(self):
        self._moveArm(self.arm_home_value)
        self._moveActuator(self.actuator_home_value)
        self._vacuumOn(False)
    
    #Move the actuator until the click sensor is engaged, then turn on the vacuum and raise
    #the actuator. The bulk of this code is going to be executed from the arduino's firmware
    def pickUpObject(self):
        self.serialConnection.write("%s" % self.LOWER_AND_LIFT)
    
    
    #Start the robot's scanning procedure
    def start(self):
        
        #reset the robot to the default values
        self.reset()
        
        
        completed = False
        while not completed:
            pass
        
        
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
    
    def in_pile(self):
        self.moveArm(self.arm_in_value)
    
    def listCommPorts(self):
        return self.serialConnection.tools.list_ports()