from gado.Robot import Robot
import thread
import subprocess
import re
import platform
import _winreg
import itertools
from threading import Thread
import serial
import time

class WebcamThread(Thread):
    def __init__(self):
        pass
    
    def run(self):
        '''
        Takes a picture of the back of the image
        '''
        pass

class ScannerThread(Thread):
    def __init__(self, funct):
        self.funct
        pass
    
    def run(self):
        cmd = 'self.%s' % self.funct
        exec("cmd")
    
    def initialize(self):
        '''
        "Warms up" the scanner for scanning
        '''
        pass
        
    def transfer(self):
        '''
        Gets the image from the scanner to the machine
        '''
        pass

class RobotThread(Thread):
    def __init__(self, robot, action):
        self.robot = robot
        self.action = action
    
    def run():
        cmd = 'self.%s' % self.action
        exec(cmd)
        
    def reset():
        self.robot.reset()
    
    

class GadoSystem():
    
    def __init__(self, dbi, robot):
        self.robot = robot
        self.dbi = dbi
        
        #set the settings to the default
        self._armPosition = 0
        self._actuatorPosition = 0
    
    def moveArmBackwards(self):
        if self._armPosition > 0:
            self._armPosition -= 1
            self.robot._moveArm(self._armPosition)
        print "Arm position: %s" % self._armPosition
        
        
    def moveArmForward(self):
        if self._armPosition < 180:
            self._armPosition += 1
            self.robot._moveArm(self._armPosition)
        print "Arm position: %s" % self._armPosition

        
    def moveActuatorDown(self):
        if self._actuatorPosition > 0:
            self._actuatorPosition -= 1
            self.robot._moveActuator(self._actuatorPosition)
        print "Actuator Position: %s" % self._actuatorPosition
        
    def moveActuatorUp(self):
        if self._actuatorPosition < 255:
            self._actuatorPosition += 1
            self.robot._moveActuator(self._actuatorPosition)
        print "Actuator Position: %s" % self._actuatorPosition
        
    def getArmPosition(self):
        
        #Get the current setup properties from the Gado
        currentSetup = self.robot.returnGadoInfo()
        
        print "Current setup: %s" % currentSetup
    
    def start(self):
        self.robot._moveArm(100)
        '''# Sanity check
        if not self.robot.connected():
            raise Exception("No robot connected")
        
        # Warmup!
        rthread = RobotThread('')
        self.robot.reset()
        self._initialize_scanner()
        
        #
        image = self._capture_webcam()
        while not (_check_barcode(image)):
            
            
            pass
        
        pass
        '''
    def connect(self, port=None):
        '''
        If port is none, then cycle through all available comm ports
        '''
        print "In connect in gado_sys\n"
        
        if not port:
            #Query the comm ports available on the system
            rawPortList = str(subprocess.check_output(["python", "-m", "serial.tools.list_ports"]))
            ports = re.findall('(COM\d+)', rawPortList)
            
            for port in self.enumerate_serial_ports():
                print "Connecting with port: %s" % port
                success = self.robot.connect(port)
                print "Connected? %s" % (success)
                
                #Found the robot!
                if success:
                    return True
                print "Done with command."
        return False
        '''
                success = self.robot.connect(port)
                print "connected to port: %s" % port
                if self.robot.connected():
                    print "robot connected!"
                    return True
                else:
                    print "robot not connected :()"
                self.robot.disconnect()
        else:
            success = self.robot.connect(port)
            success = self.robot.connected()
            return success
        return False'''
    
    def enumerate_serial_ports(self):
        """ Uses the Win32 registry to return an
            iterator of serial (COM) ports
            existing on this computer.
        """
        path = 'HARDWARE\\DEVICEMAP\\SERIALCOMM'
        try:
            key = _winreg.OpenKey(_winreg.HKEY_LOCAL_MACHINE, path)
        except WindowsError:
            raise IterationError
    
        for i in itertools.count():
            try:
                val = _winreg.EnumValue(key, i)
                yield str(val[1])
            except EnvironmentError:
                break
    
    def disconnect(self):
        pass
        return True
    
    def _capture_webcam(self):
        '''
        Captures a backside view of the next image in queue
        '''
        image = None
        return image
    
    def _check_barcode(self, image):
        '''
        Checks for a barcode within image
        '''
        return True
    
    def _initialize_scanner(self):
        pass
    
    def _scan_image(self):
        '''
        Instructs the scanner to scan the image
        This does not transfer the image to the computer yet
        '''
        pass
    
    def _transfer_image(self):
        pass
    