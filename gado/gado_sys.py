from gado.Robot import Robot
import thread
import subprocess
import re
import platform
import _winreg
import itertools
from threading import Thread
import serial
from gado.functions import *
import time, os
from gado.pytesser import *
from gado.Webcam import *
import Queue
from gado.gui.ProgressBar import *
from gado.GadoGui import GadoGui
from gado.Scanner import Scanner
from gado.Webcam import Webcam

class WebcamThread(Thread):
    def __init__(self):
        pass
    def __init__(self, webcam):
        self.webcam = webcam
    
        #Connect the webcam
        self.webcam.connect()
        
        #Call superclass' init function
        Thread.__init__(self)
        
    def run(self):
        '''
        Takes a picture of the back of the image
        '''
        self.image = 'output.png'
        print "In webcam thread, taking picture"
        self.webcam.saveImage("tttest.jpg", self.webcam.returnImage())
    
    def get_image(self):
        return self.image

#FUCK ALL OF THIS. SCANNER DOES NOT PLAY WELL WITH THREADS, WE'LL DO IT SERIAL.
class ScannerThread(Thread):
    def __init__(self, scanner):
        
        self.scanner = Scanner()
        
        #Init the superclass
        Thread.__init__(self)
        
    def run(self):
        
        #self.scanner.connectToScannerGui()
        #self.scanner.setDPI("300")
        #newScanner = Scanner()
        print "before call in thread"
        self.scanner.connectToScannerGui()
        time.sleep(2)
        self.scanner.scanImage("C:\Users\Robert\Downloads", "scannedImage.png")
        print "after call in thread"
        '''
        self.scanner.scan("C:\Users\Robert", "newScan.png")
        self.scanner.scanImage("C:\Users\Robert", "newScan2.png")
        print "in the damn scanner thread, what's wrong?"
        '''
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
    def __init__(self, robot):
        self.robot = robot
        #self.action = action
        
        #Call superclass' init function
        Thread.__init__(self)
        
        #init the queue so we can receive messages from the GUI thread
        self.queue = Queue.Queue()
    
    def run():
        cmd = 'self.%s' % self.action
        exec(cmd)
    #Do a single run on the robot's scanning procedure
    def run(self):
        #cmd = 'self.%s' % self.action
        #exec(cmd)
        self.robot.start()
        
    def reset(self):
        self.robot.reset()
    
    def in_pile(self):
        self.robot.in_pile()
    
class AutoConnectThread(Thread):
    def __init__(self, gado_sys, progressBar):
        self.gado_sys = gado_sys
        self.progressBar = progressBar
        Thread.__init__(self)
        self.success = False
    
    def run(self):
        self.connected = self.gado_sys.connect()
        
        #Stop the progress bar window
        self.progressBar.stop(self.connected)
        self.progressBar.destroy()

class GadoSystem():
    
    def __init__(self, dbi, robot, tk, scanner, connect_timeout=30, image_path='images', **kargs):
        self.robot = robot
        self.scanner = scanner
        self.dbi = dbi
        self.camera = Webcam()
        self.tk = tk
        self.selected_set = None
        self.image_path = image_path
        
        #set the settings to the default
        self._armPosition = 0
        self._actuatorPosition = 0
        
        
        if not self.robot.connected():
            progressBar = ProgressBar(root=tk)
            
            connectionThread = AutoConnectThread(self, progressBar)
            connectionThread.start()
            
            progressBar.mainloop()
            
            if not connectionThread.connected:
                tkMessageBox.showerror("Auto Connection", "Unable to find robot, please check that is plugged in or consult the manual.")
                exit()
        
        self.gui = GadoGui(self.tk, self.dbi, self)
        self.gui.mainloop()
    
    def set_seletcted_set(self, set_id):
        self.selected_set = None
    
    def updateSettings(self):
        self.robot.updateSettings(**import_settings())
    
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
        #currentSetup = self.robot.returnGadoInfo()
        
        #print "Current setup: %s" % currentSetup
        return self._armPosition
    
    def getActuatorPosition(self):
        return self._actuatorPosition
    
    def _intialize(self):
        self.sthread = ScannerThread('initialize')
        self.scanner_initializing = True
        self.sthread.start()
        self.robot.reset()
        
    def _prep_next(self):
        # Warmup!
        self.wthread = WebcamThread()
        self.wthread.start()
        self.robot.in_pile()
    
    def pause(self):
        pass#self.robotThread.pause()
    
    def reset(self):
        self.robot.reset()
    
    def _sanity_checks(self):
        _a = 'a'
        if not self.started:
            self.started = id(_a)
        
        if self.started != id(_a):
            tkMessageBox.showerror("Initialization Error",
                "The Robot has already been started")
            return False
        
        if not self.selected_set:
            tkMessageBox.showerror("Initialization Error",
                "Please choose a set from the Artifact Set dropdown list.")
            self.started = False
            return False
        
        if not self.robot.connected():
            tkMessageBox.showerror("Initialization Error",
                "Lost connection to the robot, please try restarting.")
            self.started = False
            return False
        self.robot.reset()
        
        if not self.scanner.connected():
            tkMessageBox.showerror("Initialization Error",
                "Lost connection to the scanner, please try restarting.")
            self.started = False
            return False
        
        if self.started != id(_a):
            tkMessageBox.showerror("Initialization Error",
                "Please only click start once.")
            return False
        
        self.robot._moveActuator(self.robot.actuator_up_value)
        time.sleep(2)
        
        return True
        
    
    def start(self):
        '''
        Starts the scanning process for the current in pile
        '''
        #Come back and make the sanity checks real
        #if not self._sanity_checks():
        #    return False
        
        #The actual looping should be happening here, instead of in Robot.py
        #Robot.py should just run the loop once and all conditions/vars will be stored here
        #self.robotThread = RobotThread(self.robot)
        print "attempting to save picture"
        self.camera.savePicture("backside.jpg")
        completed = False
        print "attempting to check for barcode"
        completed = check_for_barcode("backside.jpg")
        
        while not completed:
            # New Artifact!
            print "attempting to add an artifact"
            artifact_id = self.dbi.add_artifact(self.selected_set)
            back_fn = 'images/%s_back.jpg' % artifact_id
            front_fn = 'images/%s_front.jpg' % artifact_id
            os.rename('backside.jpg', back_fn)
            self.gui.changeWebcamImage(back_fn)
            print "attempting to add an image"
            image_id = self.dbi.add_image(artifact_id, back_fn, False)
            
            print "attempting to go pick up an object"
            self.robot.pickUpObject()
            
            print "attempting to move object to scanner"
            self.robot.scanObject()
            
            print "attempting to scan"
            self.scanner.scanImage2(front_fn)
            self.gui.changeScannedImage(front_fn)
            image_id = self.dbi.add_image(artifact_id, front_fn, True)
            
            self.robot.moveToOut()
            self.camera.savePicture("backside.jpg")
            completed = check_for_barcode('backside.jpg')
            
        print "Done with robot loop" 
        '''# Sanity check
        if not self.robot.connected():
            raise Exception("No robot connected")
        
        # Warm things up!
        self._initialize()
        
        image = self._prep_next()
        while not (self._check_barcode(image)):
            
            # Grab the image
            # Move the image to the scanner
            
            # Is the scanner ready?
            # Scan
            
            # THREADED
            # Pick the image up and move to out pile
            # Retrieve the scanned image
            
            self._prep_next()
        
        pass
        '''
    

    
    def connect(self):
        '''
        Connect to the Gado.
        
        If a port is specified in the settings, then try to connect to it
        Otherwise scan through ports attempting to connect to the Robot
        '''
        settings = import_settings()
        if 'gado_port' in settings:
            success = self.robot.connect(settings['gado_port'])
            if success:
                return True
        return _connect(self.robot)

    
    def disconnect(self):
        '''
        I'm not sure why we would want to disconnect the robot
        '''
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
    
    def _scan_image(self):
        '''
        Instructs the scanner to scan the image
        This does not transfer the image to the computer yet
        '''
        pass
    
    def _transfer_image(self):
        pass


    
def enumerate_serial_ports():
    """
    Uses the Win32 registry to return an
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

def _connect(robot, save_settings=True):
    '''
    Scan through ports attempting to connect to the robot.
    If save_settings is True, then save the port information.
    '''
    for port in enumerate_serial_ports():
        print "attempting port %s" % port
        success = robot.connect(port)
        if success:
            if save_settings:
                export_settings(gado_port=port)
            return True
    return False