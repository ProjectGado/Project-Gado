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
from shutil import move
from default_settings import default_settings
import datetime

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

class GadoSystem():
    
    def __init__(self, q_in, q_out, recovered=False):
        self.q_in = q_in
        self.q_out = q_out
        
        self.load_settings()
        
        if not self.s:
            export_settings(**default_settings())
            self.load_settings()
            add_to_queue(self.q_out, messages.LAUNCH_WIZARD)
        elif 'wizard_run' in self.s and int(self.s['wizard_run']) == 0:
            add_to_queue(self.q_out, messages.LAUNCH_WIZARD)
        else:
            if not recovered:
                add_to_queue(self.q_out, messages.READY)
        add_to_queue(self.q_out, messages.MAIN_READY)
        
        self.db = DBFactory(**self.s).get_db()
        self.dbi = DBInterface(self.db)
        
        self.selected_set = None
        self.started = False
    
    def load_settings(self):
        s = import_settings()
        if s:
            s['scanned_image'] = '%s.%s' % (s['temp_scanned_image'],
                    s['image_front_filetype'].strip('.'))
            s['webcam_image'] = '%s.%s' % (s['temp_webcam_image'],
                    s['image_back_filetype'].strip('.'))
        
        self.s = s
    
    def load(self):
        self.load_settings()
        
        self.scanner = Scanner(**self.s)
        self.robot = Robot(**self.s)
        self.camera = Webcam(**self.s)
    
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
                    print "gado_sys\t" + str(datetime.datetime.now()), "fetched message from queue", msg
                if msg[0] == messages.ADD_ARTIFACT_SET_LIST:
                    expecting_return = False
                    i = dbi.add_artifact_set(**msg[1])
                    #add_to_queue(q, messages.RETURN, i)
                
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
                    self.s = settings
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
                    print 'gado_sys\tWEBCAM_LISTING'
                    expecting_return = True
                    #self.camera = Webcam()
                    opts = self.camera.options()
                    print 'gado_sys\tWEBCAM_LISTING - %s' % opts
                    add_to_queue(q, messages.RETURN, opts)
                
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
                    self.camera = Webcam(**self.s)
                    print 'gado_sys\tself.camera.connected() %s' % self.camera.connected()
                    add_to_queue(q, messages.RETURN, self.camera.connected())

                elif msg[0] == messages.WEBCAM_PICTURE:
                    expecting_return = True
                    self.camera.savePicture(self.s['temp_webcam_image'])
                    add_to_queue(q, messages.RETURN, self.s['temp_webcam_image'])
                    
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
                'Unable to connect to the webcam. Try unplugging it and replugging it. You may need to restart this application or run the setup wizard again.')
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
        print "gado_sys\tchecking for messages"
        self._checkMessages()
        print 'gado_sys\tattempting to save picture'
        
        # Sometimes it gets left behind, get rid of it
        t_webcam_image = '%s.%s' % (self.s['temp_webcam_image'],
                self.s['image_back_filetype'].strip('.'))
        
        t_scanner_image = '%s.%s' % (self.s['temp_scanned_image'],
                self.s['image_front_filetype'].strip('.'))
        
        try: os.remove(t_webcam_image)
        except: pass
        self.camera.savePicture(t_webcam_image)
        self._checkMessages()
        print "gado_sys\tattempting to check for barcode"
        completed = check_for_barcode(t_webcam_image, '')
        
        while not completed:
            # New Artifact!
            print "gado_sys\tattempting to add an artifact"
            completed = self._checkMessages() & completed
            artifact_info = new_artifact(self.dbi, self.selected_set)
            
            front_fn = artifact_info['front_path']
            back_fn = artifact_info['back_path']
            
            print 'gado_sys\trenaming webcam image to %s' % back_fn
            move(t_webcam_image, back_fn)
            add_to_queue(self.q_out, messages.SET_WEBCAM_PICTURE, back_fn)
            
            print "gado_sys\tattempting to go pick up an object"
            completed = self._checkMessages() & completed
            self.robot.pickUpObject()
            
            print "gado_sys\tattempting to move object to scanner"
            completed = self._checkMessages() & completed
            self.robot.scanObject()
            
            print "gado_sys\tattempting to scan"
            completed = self._checkMessages() & completed
            
            # Sometimes it gets left behind :(
            try: os.remove(t_scanner_image)
            except: pass
            self.scanner.scanImage(t_scanner_image)
            
            print 'gado_sys\trenaming scanned images to %s' % front_fn
            move(t_scanner_image, front_fn)
            add_to_queue(self.q_out, messages.SET_SCANNER_PICTURE, front_fn)
            
            completed = self._checkMessages() & completed
            self.robot.moveToOut()
            self.camera.savePicture(t_webcam_image)
            completed = check_for_barcode(t_webcam_image, '')
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
            success = self.robot.connect(self.s.get('gado_port'))
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