import serial
import platform
import time
import sys

#Constants
MOVE_ARM = 'a'
MOVE_ACTUATOR = 's'
MOVE_VACUUM = 'v'
RETURN_CURRENT_SETTINGS = 'd'

HANDSHAKE = 'h' # checks to see if we're actually talking to the robot
LOWER_AND_LIFT = 'l' # runs a routine on the robot to pick up an artifact
PLACE_ON_SCANNER = '2' # runs a routine to move an artifact to the scanner
DROP_ON_OUT_PILE = '3' # runs a routine to drop on the out pile
RESET_TO_HOME = '4' # runs a routine to move the arm home

HANDSHAKE_VALUE = 'Im a robot!'

class Robot(object):
    #Globals
    global serialConnection
    
    
    def __init__(self, arm_home_value, arm_in_value, arm_out_value, actuator_home_value, baudrate, actuator_up_value, **kargs):
        #Grab settings
        self.arm_home_value = arm_home_value
        self.arm_in_value = arm_in_value
        self.arm_out_value = arm_out_value
        self.actuator_home_value = actuator_home_value
        self.baudrate = baudrate
        self.actuator_up_value = actuator_up_value
        self.serialConnection = None
        
    #Take in a dictionary of all of the robot settings and make these the current settings
    #It is important that all robot specific settings are passed, otherwise things may break
    def updateSettings(self, **kwargs):
        
        #try and update
        try:
            self.arm_home_value = kwargs['arm_home_value']
            self.arm_in_value = kwargs['arm_in_value']
            self.arm_out_value = kwargs['arm_out_value']
            self.actuator_home_value = kwargs['actuator_home_value']
            self.actuator_up_value = kwargs['actuator_up_value']
            self.baudrate = kwargs['baudrate']
        except:
            print "Error when trying to update robot settings... (Make sure all settings were passed)\n Error: %s" % sys.exc_info()[0]
        
    def returnGadoInfo(self):
        if self.serialConnection.isOpen():
            self.serialConnection.write(RETURN_CURRENT_SETTINGS)
            
            #Read back response, if any
            response = self.serialConnection.read(1000)
            
            return response
        else:
            return ""
        
    def connect(self, port):
        '''
        Connects to the physcial robot on a certain COM port
        Returns true if it hears back correctly, else false
        '''
        try:
            #Open a serial connection to this serial port
            self.serialConnection = serial.Serial(port, self.baudrate, timeout=1)
        except:
            print "ERROR CONNECTING TO SERIAL PORT: %s" % port
            return False
        
        #Delay for 2 seconds because pyserial can't immediately communicate
        time.sleep(2)
        
        if self.serialConnection.isOpen():
            #Initiate the handshake with the (potential) robot
            self.serialConnection.write(HANDSHAKE)
            
            #give it a second to respond
            time.sleep(1)
            
            #Read back response (if any) and check to see if it matches the expected value
            response = self.serialConnection.read(100)
            
            if response == HANDSHAKE_VALUE:
                return True
        return False
    
    def disconnect(self):
        if self.serialConnection.isOpen():
            self.serialConnection.close()
    
    def connected(self):
        '''
        Checks to see if the robot is connected
        '''
        if self.serialConnection.isOpen():
            self.serialConnection.write(HANDSHAKE)
            
            #Read back response from (tentative) robot
            response = self.serialConnection.read(100)
            print "Got serial response: %s, with port %s and baud %s" % (response, self.serialConnection.port, self.serialConnection.baudrate)
            
            if response == HANDSHAKE_VALUE:
                return True
            
        #self.serialConnection = False
        return False
        
    
    #Move the robot's arm to the specified degree (between 0-180)
    def _moveArm(self, degree):
        self.serialConnection.write("%s%s" % (degree, MOVE_ARM))
        
        #Flush the serial line so we don't get any overflows in the event
        #that many commands are trying to be sent at once
        self.clearSerialBuffers()
        
    
    #Move the robot's actuator to the specified stroke
    def _moveActuator(self, stroke):
        self.serialConnection.write("%s%s" % (stroke, MOVE_ACTUATOR))
    
        #Flush the serial line so we don't get any overflows in the event
        #that many commands are trying to be sent at once
        self.clearSerialBuffers()
        
        
    #Turn on the vacuum to the power level: value
    def _vacuumOn(self, value):
        '''
            
        '''
        self.serialConnection.write("%s%s" % (value, MOVE_VACUUM))        
    
    #Clear all buffers on the serial line
    def clearSerialBuffers(self):
        
        if self.serialConnection.isOpen():
            self.serialConnection.flushInput()
            self.serialConnection.flushOutput()
            self.serialConnection.flush()
        
    #Reset the robot to the home position
    def reset(self):
        self._moveArm(self.arm_home_value)
        self._moveActuator(self.actuator_up_value)
        self._vacuumOn(0)
    
    #Move the actuator until the click sensor is engaged, then turn on the vacuum and raise
    #the actuator. The bulk of this code is going to be executed from the arduino's firmware
    def pickUpObject(self):
        self.serialConnection.write("%s" % self.LOWER_AND_LIFT)
    
    
    #Start the robot's scanning procedure
    def start(self):
        
        #reset the robot to the default values
        self.reset()
        print "Starting the fucking robot"
        '''
        completed = False
        while not completed:
            pass
        '''
        
        ##CODE TO TAKE A PICTURE OF THE BACK OF TEH IMAGE##
        
        ##CHECK TO SEE IF WE FOUND A BARCODE (END OF STACK)##
        
        ##IF NOT, LOWER AND LIFT##
        #self.pickUpObject()
        
        ##MOVE TO SCANNER AND DROP UNTIL WE HIT IT##
        #self.moveArm(self.settings['scanner_location'])
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
    
    '''#Reset all aspects of the robot
    def reset(self):
        self.resetArm()
        self.resetActuator()
    '''
    def in_pile(self):
        self.moveArm(self.arm_in_value)
    
    def listCommPorts(self):
        return self.serialConnection.tools.list_ports()