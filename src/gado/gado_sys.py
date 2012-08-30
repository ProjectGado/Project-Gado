from src.gado.Robot import Robot
import thread
import subprocess
import re
import platform
import _winreg
import itertools
from threading import Thread
import serial
from src.gado.functions import *
import time, os
from src.gado.pytesser import *
from src.gado.Webcam import *
import Queue
from src.gado.gui.ProgressBar import *
from src.gado.GadoGui import GadoGui
from src.gado.Scanner import Scanner
from src.gado.Webcam import Webcam
import src.gado.messages as messages
from src.gado.db import DBFactory, DBInterface
from shutil import move

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
                    "image_path": "images/",
                    'wizard_run' : 0}
                    #'webcam_name' : 'Logitech Webcam 905'}

DEFAULT_SCANNED_IMAGE = 'scanned.tiff'
DEFAULT_CAMERA_IMAGE = 'backside.jpg'

class GadoSystem():
    
    def __init__(self, q_in, q_out, recovered=False):
        self.q_in = q_in
        self.q_out = q_out
        settings = import_settings()
        if 'wizard_run' in settings:
            print 'gado_sys\twizard_run in settings %s' % (settings['wizard_run'])
        if not settings:
            print "gado_sys\tNo pre-existing settings detected"
            export_settings(**DEFAULT_SETTINGS)
            if not recovered: add_to_queue(self.q_out, messages.LAUNCH_WIZARD)
        elif 'wizard_run' in settings and int(settings['wizard_run']) == 0:
            print "gado_sys\tThe wizard was never run (at least to completion)"
            if not recovered: add_to_queue(self.q_out, messages.LAUNCH_WIZARD)
        else:
            if not recovered: add_to_queue(self.q_out, messages.READY)
        
        self.tk = Tk
        self.scanner = Scanner(**settings)
        self.robot = Robot(**settings)
        self.connect()
        self.db = DBFactory(**settings).get_db()
        self.dbi = DBInterface(self.db)
        self.camera = Webcam(**settings)
        self._load_settings(**settings)
        
        self.selected_set = None
        self.started = False
        
        #set the settings to the default
        self._armPosition = 0
        self._actuatorPosition = 0
    
    def _load_settings(self, image_path='images\\', **kargs):
        self.image_path = image_path
    
    def mainloop(self):
        dbi = self.dbi
        q = self.q_out
        robot = self.robot
        
        #add_to_queue(q, messages.READY)
        
        while True:
            expecting_return = False
            try:
                msg = fetch_from_queue(self.q_in)
                if msg:
                    print "gado_sys\tfetched message from queue", msg
                if msg[0] == messages.ADD_ARTIFACT_SET_LIST:
                    expecting_return = True
                    i = dbi.add_artifact_set(**msg[1])
                    add_to_queue(q, messages.RETURN, i)
                
                elif msg[0] == messages.ARTIFACT_SET_LIST:
                    expecting_return = True
                    i = dbi.artifact_set_list()
                    add_to_queue(q, messages.RETURN, i)
                
                elif msg[0] == messages.DELETE_ARTIFACT_SET_LIST:
                    expecting_return = False
                    dbi.delete_artifact_set(msg[1])
                
                elif msg[0] == messages.DROP:
                    expecting_return = False
                    success = robot.dropActuator()
                    add_to_queue(q, messages.RETURN, success)
                
                elif msg[0] == messages.LIFT:
                    expecting_return = False
                    robot.lift()
                    
                elif msg[0] == messages.MOVE_DOWN:
                    expecting_return = True
                    stroke = self.robot.move_actuator(up = False)
                    add_to_queue(q, messages.RETURN, stroke)
                    
                elif msg[0] == messages.MOVE_UP:
                    expecting_return = True
                    stroke = self.robot.move_actuator(up = True)
                    add_to_queue(q, messages.RETURN, stroke)
                    
                elif msg[0] == messages.MOVE_LEFT:
                    expecting_return = True
                    degree = self.robot.move_arm(clockwise=False)
                    add_to_queue(q, messages.RETURN, degree)
                
                elif msg[0] == messages.MOVE_RIGHT:
                    expecting_return = True
                    degree = self.robot.move_arm(clockwise=True)
                    add_to_queue(q, messages.RETURN, degree)
                
                elif msg[0] == messages.RELOAD_SETTINGS:
                    expecting_return = False
                    settings = import_settings()
                    self.robot.updateSettings(**settings)
                    del self.camera
                    self.camera = Webcam(**settings)
                    del self.scanner
                    self.scanner = Scanner(**settings)
                    self._load_settings(**settings)
                
                elif msg[0] == messages.RESET:
                    expecting_return = False
                    self.robot.reset()
                
                elif msg[0] == messages.ROBOT_CONNECT:
                    expecting_return = True
                    success = self.connect()
                    add_to_queue(q, messages.RETURN, robot.connected())
                
                elif msg[0] == messages.SCANNER_CONNECT:
                    expecting_return = True
                    try: del self.scanner
                    except: pass
                    self.scanner = Scanner(**import_settings())
                    add_to_queue(q, messages.RETURN, self.scanner.connected())
                
                elif msg[0] == messages.SCANNER_PICTURE:
                    expecting_return = True
                    self.scanner.scanImage(DEFAULT_SCANNED_IMAGE)
                    add_to_queue(q, messages.RETURN, DEFAULT_SCANNED_IMAGE)

                elif msg[0] == messages.SET_SELECTED_ARTIFACT_SET:
                    expecting_return = True
                    self.selected_set = msg[1]

                elif msg[0] == messages.START:
                    expecting_return = False
                    self.start()
                
                elif msg[0] == messages.WEBCAM_LISTING:
                    expecting_return = True
                    self.camera = Webcam()
                
                elif msg[0] == messages.WEBCAM_CONNECT:
                    print 'gado_sys\tWEBCAM_CONNECT switch made it'
                    expecting_return = True
                    if self.camera:
                        print 'gado_sys\tCamera already exists'
                        if self.camera.connected():
                            print 'gado_sys\tAlready connected to the webcam'
                            add_to_queue(q, messages.RETURN, self.camera.connected())
                            return
                        else: self.camera.disconnect()
                    self.camera = Webcam()
                    print 'gado_sys\tself.camera.connected() %s' % self.camera.connected()
                    add_to_queue(q, messages.RETURN, self.camera.connected())

                elif msg[0] == messages.WEBCAM_PICTURE:
                    expecting_return = True
                    self.camera.savePicture(DEFAULT_CAMERA_IMAGE)
                    add_to_queue(q, messages.RETURN, DEFAULT_CAMERA_IMAGE)
                    
                elif msg[0] == messages.WEIGHTED_ARTIFACT_SET_LIST:
                    expecting_return = True
                    li = self.dbi.weighted_artifact_set_list()
                    add_to_queue(q, messages.RETURN, arguments=li)
                elif msg[0] == messages.MAIN_ABANDON_SHIP:
                    add_to_queue(q, messages.GUI_LISTENER_DIE)
                    add_to_queue(self.q_in, messages.MAIN_ABANDON_SHIP)
                    return
                elif msg[0] == messages.STOP or msg[0] == messages.LAST_ARTIFACT or msg[0] == messages.RESET:
                    # These commands are only relevant if the robot is already running.
                    expecting_return = False
                    pass
                elif msg[0] == messages.GIVE_ME_A_ROBOT:
                    add_to_queue(q, messages.RETURN, self.robot)
                else:
                    # add it back to the in queue, was somebody else waiting for that message?
                    add_to_queue(self.q_in, msg[0], (msg[1] if len(msg) > 1 else None))
            except:
                print "EXCEPTION GENERATED"
                raise
                if expecting_return:
                    add_to_queue(q, messages.RETURN)
    
    def set_seletcted_set(self, set_id):
        self.selected_set = None
    
    def _sanity_checks(self):
        print 'gado_sys\tin sanity checks'
        if self.started:
            add_to_queue(self.q_out, messages.DISPLAY_ERROR,
                'The scanning process has already started')
            return False
        
        _a = 'a'
        self.started = id(_a)
        
        if not self.selected_set:
            print 'gado_sys\tfailed sanity check on selected_set'
            add_to_queue(self.q_out, messages.DISPLAY_ERROR,
                'Please select an artifact set from the dropdown.')
            self.started = False
            return False
        
        if not self.robot.connected():
            print 'gado_sys\tfailed sanity check on robot.connected()'
            #tkMessageBox.showerror("Initialization Error",
            #    "Lost connection to the robot, please try restarting.")
            self.connect()
            if not self.robot.connected():
                print "gado_sys\tCOMPLETELY FAILED ON robot.connected()"
                add_to_queue(self.q_out, messages.DISPLAY_ERROR,
                    'Unable to connect to the robot. Try pressing the reset button and then unplugging it and replugging it.')
                self.started = False
                return False
        
        add_to_queue(self.q_out, messages.SET_STATUS_TEXT, 'Connected to the Gado')
        self.robot.reset()
        
        if not self.scanner.connected():
            print 'gado_sys\tfailed sanity check on scanner.connected(), retrying'
            try: del self.scanner
            except: pass
            self.scanner = Scanner(**import_settings())
            if not self.scanner.connected():
                print 'gado_sys\tfailed sanity check on scanner.connected()'
                #tkMessageBox.showerror("Initialization Error",
                #    "Lost connection to the scanner, please try restarting.")
                self.started = False
                add_to_queue(self.q_out, messages.DISPLAY_ERROR,
                    'Unable to connect to the scanner. Try unplugging it and replugging it. You may need to restart this application or run the setup wizard again.')
                return False
        add_to_queue(self.q_out, messages.SET_STATUS_TEXT, 'Connected to the scanner')
        
        if not self.camera.connected():
            print 'gado_sys\tfailed sanity check on camera.connected()'
            add_to_queue(self.q_out, messages.DISPLAY_ERROR,
                'Unable to connect to the scanner. Try unplugging it and replugging it. You may need to restart this application or run the setup wizard again.')
            self.started = False
            return False
        add_to_queue(self.q_out, messages.SET_STATUS_TEXT, 'Connected to the webcam')
        
        self.robot._moveActuator(self.robot.actuator_up_value)
        time.sleep(2)
        
        if self.started != id(_a):
            add_to_queue(self.q_out, messages.DISPLAY_ERROR, 'An unknown error has occurred. Try restarting this application')
            self.started = False
            return False
        
        add_to_queue(self.q_out, messages.SET_STATUS_TEXT, 'Ready to begin scanning')
        
        return True
    
    def _checkMessages(self):
        '''
        Controls the gado loop
        
        Returns True if the process should continue
        Returns False if the process should after the current loop
        Resets and raises an error if things need to stop.
        
        '''
        if self.q_in.empty():
            return True
        msg = fetch_from_queue(self.q_in)
        if msg[0] == messages.STOP:
            add_to_queue(self.q_out, messages.SET_STATUS_TEXT, 'Robot stopped.')
            self.started = False
            self.robot.stop()
            raise Exception('STOP CALLED')
        elif msg[0] == messages.RESET:
            self.robot.reset()
            add_to_queue(self.q_out, messages.SET_STATUS_TEXT, 'Robot reset')
            raise Exception('RESET CALLED')
        elif msg[0] == messages.LAST_ARTIFACT:
            return False
        elif msg[0] == messages.START:
            add_to_queue(self.q_out, messages.DISPLAY_INFO, 'The robot is already running. If it is not, then please restart this application.')
        elif msg[0] == messages.SYSTEM_ABANDON_SHIP:
            self.robot.stop()
            add_to_queue(self.q_in, msg[0])
            raise Exception('Application Terminating')
        else:
            add_to_queue(self.q_out, msg[0], (msg[1] if len(msg) > 1 else None))
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
        self.camera.savePicture(DEFAULT_CAMERA_IMAGE)
        self._checkMessages()
        print "attempting to check for barcode"
        completed = check_for_barcode(DEFAULT_CAMERA_IMAGE)
        
        print 'gado_sys\timage_path %s' % self.image_path
        
        while not completed:
            # New Artifact!
            print "attempting to add an artifact"
            completed = self._checkMessages() & completed
            artifact_id = self.dbi.add_artifact(self.selected_set)
            
            back_fn = '%s%s_back.jpg' % (self.image_path, artifact_id)
            front_fn = '%s%s_front.tiff' % (self.image_path, artifact_id)
            print 'gado_sys\trenaming webcam image to %s' % back_fn
            move(DEFAULT_CAMERA_IMAGE, back_fn)
            #os.rename(DEFAULT_CAMERA_IMAGE, back_fn)
            add_to_queue(self.q_out, messages.SET_WEBCAM_PICTURE, back_fn)
            
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
            self.scanner.scanImage(DEFAULT_SCANNED_IMAGE)
            print 'gado_sys\trenaming scanned images to %s' % front_fn
            move(DEFAULT_SCANNED_IMAGE, front_fn)
            #os.rename(DEFAULT_SCANNED_IMAGE, front_fn)
            add_to_queue(self.q_out, messages.SET_SCANNER_PICTURE, front_fn)
            image_id = self.dbi.add_image(artifact_id, front_fn, True)
            
            completed = self._checkMessages() & completed
            self.robot.moveToOut()
            self.camera.savePicture(DEFAULT_CAMERA_IMAGE)
            completed = check_for_barcode(DEFAULT_CAMERA_IMAGE)
        self.started = False
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