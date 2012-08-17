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
import gado.messages as messages
from gado.db import DBFactory, DBInterface

class AutoConnectThread(Thread):
    def __init__(self, gado_sys, progressBar):
        self.gado_sys = gado_sys
        self.progressBar = progressBar
        Thread.__init__(self)
        self.success = False
    
    def run(self):
        self.connected = self.gado_sys.connect()
        
        #Stop the progress bar window
        print "calling stop"
        self.progressBar.stop(self.connected)

DEFAULT_SETTINGS = {'baudrate' :115200,
                    "db_directory": "databases",
                    "db_filename": "db.sqlite",
                    "image_path": "images"}

DEFAULT_SCANNED_IMAGE = 'scanned.tiff'
DEFAULT_CAMERA_IMAGE = 'backside.jpg'

class GadoSystem():
    
    def __init__(self, q, l):
        self.q = q
        self.l = l
        try:
            settings = import_settings()
        except:
            export_settings(**DEFAULT_SETTINGS)
            
            # We're going to launch the wizard!
            # It's going to save stuff.
            
            settings = import_settings()
        
        self.tk = Tk
        self.scanner = Scanner(**settings)
        self.robot = Robot(**settings)
        self.db = DBFactory(**settings).get_db()
        self.dbi = DBInterface(self.db)
        self.camera = Webcam(**settings)
        self._load_settings()
        
        self.selected_set = None
        
        #set the settings to the default
        self._armPosition = 0
        self._actuatorPosition = 0
    
    def _load_settings(self, image_path='images/', **kargs):
        self.image_path = image_path
    
    def mainloop(self):
        dbi = self.dbi
        q = self.q
        robot = self.robot
        l = self.l
        
        #add_to_queue(q, l, messages.READY)
        
        while True:
            expecting_return = False
            try:
                msg = fetch_from_queue(q, l)
                if msg:
                    print "gado_sys\tfetched message from queue", msg
                if msg[0] == messages.ADD_ARTIFACT_SET_LIST:
                    expecting_return = True
                    i = dbi.add_artifact_set(**msg[1])
                    add_to_queue(q, l, messages.RETURN, i)
                
                elif msg[0] == messages.ARTIFACT_SET_LIST:
                    expecting_return = True
                    l = dbi.artifact_set_list()
                    add_to_queue(q, l, messages.RETURN, i)
                
                elif msg[0] == messages.DELETE_ARTIFACT_SET_LIST:
                    expecting_return = True
                    dbi.delete_artifact_set(msg[1])
                    add_to_queue(q, l, messages.RETURN)
                
                elif msg[0] == messages.DROP:
                    expecting_return = True
                    success = robot.dropActuator()
                    add_to_queue(q, l, messages.RETURN, success)
                
                elif msg[0] == messages.LIFT:
                    expecting_return = True
                    success = robot.lift()
                    add_to_queue(q, l, messages.RETURN, success)
                    
                elif msg[0] == messages.MOVE_DOWN:
                    expecting_return = True
                    self.robot.move_actuator(up = False)
                    add_to_queue(q, l, messages.RETURN)
                    
                elif msg[0] == messages.MOVE_UP:
                    expecting_return = True
                    self.robot.move_actuator(up = True)
                    add_to_queue(q, l, messages.RETURN)
                    
                elif msg[0] == messages.MOVE_LEFT:
                    expecting_return = True
                    self.robot.move_arm(clockwise=False)
                    add_to_queue(q, l, messages.RETURN)
                
                elif msg[0] == messages.MOVE_RIGHT:
                    expecting_return = True
                    self.robot.move_arm(clockwise=True)
                    add_to_queue(q, l, messages.RETURN)
                
                elif msg[0] == messages.RELOAD_SETTINGS:
                    expecting_return = True
                    settings = import_settings()
                    self.robot.updateSettings(**settings)
                    del self.camera
                    self.camera = Webcam(**settings)
                    del self.scanner
                    self.scanner = Scanner(**settings)
                    self._load_settings(**settings)
                    add_to_queue(q, l, messages.RETURN)
                
                elif msg[0] == messages.RESET:
                    expecting_return = True
                    self.robot.reset()
                    add_to_queue(q, l, messages.RETURN)
                
                elif msg[0] == messages.ROBOT_CONNECT:
                    expecting_return = True
                    success = self.connect()
                    add_to_queue(q, l, messages.RETURN)
                
                elif msg[0] == messages.SCANNER_CONNECT:
                    expecting_return = True
                    del self.scanner
                    self.scanner = Scanner(**import_settings())
                    add_to_queue(q, l, messages.RETURN)
                
                elif msg[0] == messages.SCANNER_PICTURE:
                    expecting_return = True
                    self.scanner.scanImage2(DEFAULT_SCANNED_IMAGE)
                    add_to_queue(q, l, messages.RETURN, DEFAULT_SCANNED_IMAGE)

                elif msg[0] == messages.SET_SELECTED_ARTIFACT_SET:
                    expecting_return = True
                    self.selected_set = msg[1]
                    add_to_queue(q, l, messages.RETURN)

                elif msg[0] == messages.START:
                    expecting_return = True
                    self.start()
                    add_to_queue(q, l, messages.RETURN)

                elif msg[0] == messages.WEBCAM_CONNECT:
                    expecting_return = True
                    del self.camera
                    self.camera = Webcam(**import_settings())
                    add_to_queue(q, l, messages.RETURN)

                elif msg[0] == messages.WEBCAM_PICTURE:
                    expecting_return = True
                    self.camera.savePicture(DEFAULT_CAMERA_IMAGE)
                    add_to_queue(q, l, messages.RETURN, DEFAULT_CAMERA_IMAGE)
                    
                elif msg[0] == messages.WEIGHTED_ARTIFACT_SET_LIST:
                    expecting_return = True
                    li = self.dbi.weighted_artifact_set_list()
                    print "here's the weighted dropdown", li
                    add_to_queue(q, l, messages.RETURN, arguments=li)
                    print 'and there it sent!'
                else:
                    add_to_queue(q, l, msg[0], (msg[1] if len(msg) > 1 else None))
            except:
                print "EXCEPTION GENERATED"
                raise
                if expecting_return:
                    try:
                        add_to_queue(q, l, msg[0], (msg[1] if len(msg) > 1 else None))
                    except:
                        print 'nothing to add back to the queue? taking a brief nap'
                        time.sleep(1)
    
    def set_seletcted_set(self, set_id):
        self.selected_set = None
    
    def _sanity_checks(self):
        print 'gado_sys\tin sanity checks'
        if not self.selected_set:
            print 'gado_sys\tfailed sanity check on selected_set'
            #tkMessageBox.showerror("Initialization Error",
            #    "Please choose a set from the Artifact Set dropdown list.")
            self.started = False
            return False
        
        if not self.robot.connected():
            print 'gado_sys\tfailed sanity check on robot.connected'
            #tkMessageBox.showerror("Initialization Error",
            #    "Lost connection to the robot, please try restarting.")
            self.connect()
            if not self.robot.connected():
                print "gado_sys\tCOMPLETELY FAILED ON robot.connected"
                return False
        self.robot.reset()
        
        if not self.scanner.connected():
            print 'gado_sys\tfailed sanity check on scanner.connected'
            #tkMessageBox.showerror("Initialization Error",
            #    "Lost connection to the scanner, please try restarting.")
            self.started = False
            return False
        
        self.robot._moveActuator(self.robot.actuator_up_value)
        time.sleep(2)
        
        return True
    
    def _checkMessages(self):
        '''
        Controls the gado loop
        
        Returns True if the process should continue
        Returns False if the process should after the current loop
        Resets and raises an error if things need to stop.
        
        '''
        if self.q.empty():
            return True
        msg = fetch_from_queue(self.q, self.l)
        if msg[0] == messages.STOP:
            raise Exception('STOP CALLED')
        elif msg[0] == messages.RESET:
            self.robot.reset()
            raise Exception('RESET CALLED')
        elif msg[0] == messages.LAST_ARTIFACT:
            return False
        else:
            add_to_queue(self.q, self.l, msg[0], (msg[1] if len(msg) > 1 else None))
        return True
    
    def start(self):
        '''
        Starts the scanning process for the current in pile
        '''
        #Come back and make the sanity checks real
        if not self._sanity_checks():
            return False
        
        #The actual looping should be happening here, instead of in Robot.py
        #Robot.py should just run the loop once and all conditions/vars will be stored here
        #self.robotThread = RobotThread(self.robot)
        print "checking for messages"
        self._checkMessages()
        print 'attempting to save picture'
        self.camera.savePicture("backside.jpg")
        self._checkMessages()
        print "attempting to check for barcode"
        completed = check_for_barcode("backside.jpg")
        
        while not completed:
            # New Artifact!
            print "attempting to add an artifact"
            completed = self._checkMessages() & completed
            artifact_id = self.dbi.add_artifact(self.selected_set)
            
            back_fn = '%s%s_back.jpg' % (self.image_path, artifact_id)
            front_fn = '%s%s_front.jpg' % (self.image_path, artifact_id)
            os.rename('backside.jpg', back_fn)
            add_to_queue(self.q, self.l, messages.SET_WEBCAM_PICTURE, back_fn)
            
            print "attempting to add an image"
            image_id = self.dbi.add_image(artifact_id, back_fn, False)
            
            print "attempting to go pick up an object"
            completed = self._checkMessages() & completed
            self.robot.pickUpObject()
            
            print "attempting to move object to scanner"
            completed = self._checkMessages() & completed
            self.robot.scanObject()
            
            print "attempting to scan"
            completed = self._checkMessages() & completed
            self.scanner.scanImage2(front_fn)
            add_to_queue(self.q, self.l, messages.SET_SCANNER_PICTURE, front_fn)
            image_id = self.dbi.add_image(artifact_id, front_fn, True)
            
            completed = self._checkMessages() & completed
            self.robot.moveToOut()
            self.camera.savePicture("backside.jpg")
            completed = check_for_barcode('backside.jpg')
        print "Done with robot loop"
    
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