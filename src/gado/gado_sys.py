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
from gado.GadoGui import GadoGui
from gado.Scanner import Scanner
from gado.Webcam import Webcam
import gado.messages as messages
from gado.db import DBFactory, DBInterface
from gado.Logger import Logger
from shutil import move
from default_settings import default_settings
import datetime

# This class is responsible for interfacing with all system peripherals (scanner, webcam, robot...)
# It uses two queues for all inter-thread communication
#
#   The in-queue takes all messages passed from the Gui thread
#   The out-queue relays all messages from the system back to the Gui thread
#

class GadoSystem():
    
    def __init__(self, q_in, q_out, recovered=False):
        
        #Instantiate the logger
        loggerObj = Logger(self.__class__.__name__)
        self.logger = loggerObj.getLoggerInstance()
        
        self.logger.info("Initializing the Gado System...")
        
        #Load up both queues
        self.q_in = q_in
        self.q_out = q_out
        
        #Grab the settings from gado.conf (If it exists) and place them into
        #a local object so that they can be used here
        self.load_settings()
        
        #If there are no settings (because there is no gado.conf)
        if not self.s:
            #Grab the default settings and load them into a newly created gado.conf
            export_settings(**default_settings())
            
            #Load those default settings to a local object
            self.load_settings()
            
            #Because there is no gado.conf, we're going to need to launch
            #the configuration wizard so that the user can enter their
            #personal settings
            add_to_queue(self.q_out, messages.LAUNCH_WIZARD)
            
            print 'gado_sys\tasked to launch the wizard'
        
        #Even if we do have a gado.conf file, the wizard has never been run
        #so it needs to get launched for the user's personal preferences
        elif 'wizard_run' in self.s and int(self.s['wizard_run']) == 0:
            add_to_queue(self.q_out, messages.LAUNCH_WIZARD)
            print 'gado_sys\tasked to launch the wizard2'
        
        #If this is the first time the logic thread has been run,
        #tell the gui thread that the system is ready for interactions
        else:
            print 'gado_sys\tnot asked for a wizard'
            if not recovered: add_to_queue(self.q_out, messages.READY)
        
        #Get an instance of the database and the database interface
        self.db = DBFactory(**self.s).get_db()
        self.dbi = DBInterface(self.db)
        
        #Init local vars
        self.selected_set = None
        self.started = False
    
    def load_settings(self):
        '''
        Function which attempts to import the settings stored in gado.conf
        
        If there is no gado.conf (or it is empty) then the settings object
        defaults to None
        '''
    
        s = import_settings()
        if s:
            s['scanned_image'] = '%s.%s' % (s['temp_scanned_image'],
                    s['image_front_filetype'].strip('.'))
            s['webcam_image'] = '%s.%s' % (s['temp_webcam_image'],
                    s['image_back_filetype'].strip('.'))
        
        self.s = s
    
    def load(self):
        '''
        Loads up the settings from gado.conf and instantiates objects for:
            
            The Scanner
            The Robot
            The Webcam
        '''
        
        self.load_settings()
        
        self.scanner = Scanner(**self.s)
        self.robot = Robot(**self.s)
        self.camera = Webcam(**self.s)
    
    def mainloop(self):
        '''
        Repeating loop that constantly checks to see if the in-queue (the Gui) has any new
        messages for the system
        
        A Series of if/elses is then used to determine the appropriate action to take for
        each message received
        '''
    
        #Set database interface, the system-to-gui queue and the robot as local vars
        dbi = self.dbi
        q = self.q_out
        robot = self.robot
        
        #add_to_queue(q, messages.READY)
        
        #Loop until told to stop
        while True:
            expecting_return = False
            try:
                #Grab a message from the gui-to-system queue (if on exists)
                msg = fetch_from_queue(self.q_in)
                
                #Add an new artifact set to the local database
                if msg[0] == messages.ADD_ARTIFACT_SET_LIST:
                    i = dbi.add_artifact_set(**msg[1])
                
                #Grab the full lits of artifact sets and pass it back
                #using the system-to-gui queue
                elif msg[0] == messages.ARTIFACT_SET_LIST:
                    expecting_return = messages.ARTIFACT_SET_LIST
                    i = dbi.artifact_set_list()
                    add_to_queue(q, messages.ARTIFACT_SET_LIST, i)
                
                #Delete a specified artifact set
                elif msg[0] == messages.DELETE_ARTIFACT_SET_LIST:
                    dbi.delete_artifact_set(msg[1])
                
                #Grab the user's settings and either update the settings for
                #the robot, scanner and webcam; or reinstantiate those objects
                #with the new setttings
                elif msg[0] == messages.RELOAD_SETTINGS:
                    settings = import_settings()
                    self.s = settings
                    
                    self.robot.updateSettings(**settings)
                    
                    del self.camera
                    self.camera = Webcam(**settings)
                    
                    del self.scanner
                    self.scanner = Scanner(**settings)
                    
                    self._load_settings(**settings)
                
                #Restart the robot
                elif msg[0] == messages.RESET:
                    self.robot.reset()
                
                #Attempt to connect to the robot (via serial port)
                #Pass back to Gui whether or not it was sucessfull
                elif msg[0] == messages.ROBOT_CONNECT:
                    expecting_return = messages.ROBOT_CONNECT
                    success = self.connect()
                    self.logger.info('ROBOT_CONNECT: %s' % success)
                    add_to_queue(q, messages.ROBOT_CONNECT, robot.connected())
                
                #Delete the current scanner object (if it exists)
                #and instantiate a new one
                #
                #Pass back to Gui whether or not this was sucessfull
                elif msg[0] == messages.SCANNER_CONNECT:
                    expecting_return = messages.SCANNER_CONNECT
                    try: del self.scanner
                    except:
                        self.logger.exception("Exception while connecting to scanner")
                        pass
                    self.scanner = Scanner(**import_settings())
                    add_to_queue(q, messages.SCANNER_CONNECT, self.scanner.connected())
                
                elif msg[0] == messages.SCANNER_CONNECTED:
                    add_to_queue(q, messages.SCANNER_CONNECTED, self.scanner.connected())
                    
                #Scan an inmage using the scanner
                elif msg[0] == messages.SCANNER_PICTURE:
                    expecting_return = messages.SCANNER_PICTURE
                    self.scanner.scanImage(self.s['scanned_image'])
                    add_to_queue(q, messages.SCANNER_PICTURE, self.s['scanned_image'])

                #Set the passed in artifact set as the currently selected
                elif msg[0] == messages.SET_SELECTED_ARTIFACT_SET:
                    self.selected_set = msg[1]

                #Starts the robot's overall procedure for moving/scanning artifacts
                elif msg[0] == messages.START:
                    self.start()
                
                #Grabs a list of available webcams and returns them to the Gui thread
                elif msg[0] == messages.WEBCAM_LISTING:
                    self.logger.debug('WEBCAM_LISTING')
                    expecting_return = messages.WEBCAM_LISTING
                    
                    opts = self.camera.options()
                    self.logger.debug('WEBCAM_LISTING - %s' % opts)
                    add_to_queue(q, messages.WEBCAM_LISTING, opts)
                
                #Attempt to connect to the selected webcam
                elif msg[0] == messages.WEBCAM_CONNECT:
                    self.logger.debug('WEBCAM_CONNECT switch made it')
                    expecting_return = messages.WEBCAM_CONNECT
                    
                    #If the webcam object exists
                    if self.camera:
                        self.logger.info('Camera already exists')
                        #And it is connected
                        if self.camera.connected():
                            self.logger.info('Already connected to the webcam')
                            
                            #Relay that information back to the Gui thread
                            add_to_queue(q, messages.WEBCAM_CONNECT, self.camera.connected())
                            return
                        #Otherwise, disconnect
                        else: self.camera.disconnect()
                        
                    #Reinstantiate the webcam object with the user settings
                    self.camera = Webcam(**import_settings())
                    
                    #Connect to webcam and let the Gui thread know if it was sucessfull
                    self.logger.info('self.camera.connected() %s' % self.camera.connected())
                    add_to_queue(q, messages.WEBCAM_CONNECT, self.camera.connected())
                
                elif msg[0] == messages.WEBCAM_CONNECTED:
                    add_to_queue(q, messages.WEBCAM_CONNECTED, self.camera.connected())
                    
                #Take a picture using the currently connected webcam
                elif msg[0] == messages.WEBCAM_PICTURE:
                    expecting_return = messages.WEBCAM_PICTURE
                    
                    #Save the picture as the temp image name
                    self.camera.savePicture(self.s['webcam_image'])
                    
                    #Pass that name back to the Gui thread
                    add_to_queue(q, messages.WEBCAM_PICTURE, self.s['webcam_image'])
                    
                #Grab a list of artifact sets, with weights so we can figure out the most
                #recently used
                elif msg[0] == messages.WEIGHTED_ARTIFACT_SET_LIST:
                    expecting_return = messages.WEIGHTED_ARTIFACT_SET_LIST
                    li = self.dbi.weighted_artifact_set_list()
                    add_to_queue(q, messages.WEIGHTED_ARTIFACT_SET_LIST, arguments=li)
                
                #Kill the program!!!
                elif msg[0] == messages.MAIN_ABANDON_SHIP:
                    add_to_queue(q, messages.GUI_LISTENER_DIE)
                    add_to_queue(self.q_in, messages.MAIN_ABANDON_SHIP)
                    return
                
                elif msg[0] == messages.STOP or msg[0] == messages.LAST_ARTIFACT or msg[0] == messages.RESET:
                    # These commands are only relevant if the robot is already running.
                    pass
                
                #Pass the robot object to the Gui thread
                elif msg[0] == messages.GIVE_ME_A_ROBOT:
                    add_to_queue(q, messages.GIVE_ME_A_ROBOT, self.robot)
                else:
                    # add it back to the in queue, was somebody else waiting for that message?
                    add_to_queue(self.q_in, msg[0], (msg[1] if len(msg) > 1 else None))
            
            #Something went horribly wrong, if the Gui thread is expecting a response,
            #Tell it things went poorly
            except:
                self.logger.exception("EXCEPTION GENERATED")
                #raise
                if expecting_return:
                    add_to_queue(q, expecting_return)
    
    
    def _sanity_checks(self):
        '''
        Runs a series of checks on the connected peripherals and other components
        of the Gado system
        
        If any of these tests fail, then the Gui thread is notified as to what didn't work so
        the user can take appropriate action
        
        If all the tests pass, then the system is ready to proceed with the scanning process
        '''
        
        self.logger.debug('in sanity checks')
        
        #If the scanning process has started, and a user attempts to start it again
        #Tell the gui to display a message stating that
        if self.started:
            add_to_queue(self.q_out, messages.DISPLAY_ERROR,
                'The scanning process has already started')
            return False
        
        _a = 'a'
        self.started = id(_a)
        
        #User did not select an artifact set from the dropdown
        if not self.selected_set:
            self.logger.error('failed sanity check on selected_set')
            add_to_queue(self.q_out, messages.DISPLAY_ERROR,
                'Please select an artifact set from the dropdown.')
            self.started = False
            return False
        
        #Robot is not currently connected
        if not self.robot.connected():
            self.logger.error('failed sanity check on robot.connected()')
            
            #Try and connect
            self.connect()
            
            #If that failed, let the Gui know so it can tell the user
            if not self.robot.connected():
                self.logger.error("COMPLETELY FAILED ON robot.connected()")
                add_to_queue(self.q_out, messages.DISPLAY_ERROR,
                    'Unable to connect to the robot. Try pressing the reset button and then unplugging it and replugging it.')
                self.started = False
                return False
        
        #Otherwise, let the user know that the connection was successfull
        add_to_queue(self.q_out, messages.SET_STATUS_TEXT, 'Connected to the Gado')
        
        #Reset the robot to its initial location
        self.robot.reset()
        
        #If the scanner is not currently connected
        if not self.scanner.connected():
            self.logger.error('failed sanity check on scanner.connected(), retrying')
            
            #Delete the scanner object (if any)
            try: del self.scanner
            except:
                self.logger.exception("Error while connecting to scanner")
                pass
            
            #Reinstantiate the object with the user settings
            self.scanner = Scanner(**import_settings())
            
            #If the scanner is still not connected to the system
            if not self.scanner.connected():
                self.logger.error('failed sanity check on scanner.connected()')
                
                #Let the Gui thread know that the scanner could not be found
                self.started = False
                add_to_queue(self.q_out, messages.DISPLAY_ERROR,
                    'Unable to connect to the scanner. Try unplugging it and replugging it. You may need to restart this application or run the setup wizard again.')
                return False
        
        #Let the Gui thread know that the scanner was found so it can alert the user
        add_to_queue(self.q_out, messages.SET_STATUS_TEXT, 'Connected to the scanner')
        
        #Webcam is not currently connected
        if not self.camera.connected():
            
            #Attempt to connect to it
            self.camera.connect()
            
            #If that fails
            if not self.camera.connected():
                self.logger.error('failed sanity check on camera.connected()')
                
                #Let the Gui thread know that it is not connected so it can alert the user
                add_to_queue(self.q_out, messages.DISPLAY_ERROR,
                    'Unable to connect to the webcam. Try unplugging it and replugging it. You may need to restart this application or run the setup wizard again.')
                self.started = False
                return False
            
        #Let the Gui thread know that the webcam is connected
        add_to_queue(self.q_out, messages.SET_STATUS_TEXT, 'Connected to the webcam')
        
        #Move the robot's actuator up to its starting position
        self.robot._moveActuator(self.robot.actuator_up_value)
        
        #Allow some time for the movement to happen
        time.sleep(2)
        
        #Something strange happened, let the Gui thread know
        if self.started != id(_a):
            add_to_queue(self.q_out, messages.DISPLAY_ERROR, 'An unknown error has occurred. Try restarting this application')
            self.started = False
            return False
        
        #Sanity checks all passed, let the Gui thread know that the system is ready to proceed
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
        
        #Stop the robot
        if msg[0] == messages.STOP:
            add_to_queue(self.q_out, messages.SET_STATUS_TEXT, 'Robot stopped.')
            self.started = False
            self.robot.stop()
            raise Exception('STOP CALLED')
        
        #Reset the robot
        elif msg[0] == messages.RESET:
            self.robot.reset()
            add_to_queue(self.q_out, messages.SET_STATUS_TEXT, 'Robot reset')
            raise Exception('RESET CALLED')
        
        #This is the last artifact being scanned, stopped after it is finished
        elif msg[0] == messages.LAST_ARTIFACT:
            return False
        
        #Start the robot's procedure
        elif msg[0] == messages.START:
            add_to_queue(self.q_out, messages.DISPLAY_INFO, 'The robot is already running. If it is not, then please restart this application.')
        
        #Kill everything
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

        self.logger.debug("checking for messages")
        self._checkMessages()
        self.logger.info('attempting to save picture')
        
        # Sometimes it gets left behind, get rid of it
        try:
            t_webcam_image = self.s['webcam_image']
        except:
            self.logger.exception("Exception while starting the robot")
            pass
        try:
            t_scanner_image = self.s['scanned_image']
        except:
            self.logger.exception("Exception while starting the robot")
            pass
        
        try: os.remove(t_webcam_image)
        except:
            self.logger.exception("Exception while starting the robot")
            pass
        
        #Take picture of back of artifact
        self.camera.savePicture(t_webcam_image)
        self._checkMessages()
        
        self.logger.info("attempting to check for barcode")
        
        #Check to see if we have reached the end of the input pile
        completed = check_for_barcode(t_webcam_image, '')
        
        #While we still have artifacts in the in pile that need to be digitized
        while not completed:
            # New Artifact!
            self.logger.info("attempting to add an artifact")
            completed = self._checkMessages() & completed
            
            #Create a new artifact within the currently selected set
            artifact_info = new_artifact(self.dbi, self.selected_set)
            
            #Set the paths for the front and back images
            front_fn = artifact_info['front_path']
            back_fn = artifact_info['back_path']
            
            self.logger.debug('renaming webcam image to %s' % back_fn)
            
            #Move the temp webcam image to it's permanent location
            move(t_webcam_image, back_fn)
            
            #Pass the webcam's captured image back to the Gui thread so that it can be displayed
            add_to_queue(self.q_out, messages.SET_WEBCAM_PICTURE, back_fn)
            
            self.logger.info("attempting to go pick up an object")
            completed = self._checkMessages() & completed
            
            #Pick up a single artifact from the in pile
            self.robot.pickUpObject()
            time.sleep(5)
            
            self.logger.info("attempting to move object to scanner")
            completed = self._checkMessages() & completed
            
            #Using the scanner, capture an image of that artifact
            self.robot.scanObject()
            self.robot._vacuumOn(False)
            
            completed = self._checkMessages() & completed
            
            # Sometimes it gets left behind :(
            try: os.remove(t_scanner_image)
            except:
                self.logger.exception("Couldn't remove image file - this is usually not a problem")
            
            #Do the actual scanning of the artifact
            self.scanner.scanImage(t_scanner_image)
            
            self.logger.debug('renaming scanned images to %s' % front_fn)
            
            #Move scanned image to its permament location
            move(t_scanner_image, front_fn)
            
            #Pass the scanned image back to the Gui thread so that it can be displayed
            add_to_queue(self.q_out, messages.SET_SCANNER_PICTURE, front_fn)
            
            completed = self._checkMessages() & completed
            
            #Rotate the robot's arm to over the out pile
            self.robot.moveToOut()
            
            #Take a picture of the back of the next artifact and check to make sure it's not
            #the end of the current in pile
            self.camera.savePicture(t_webcam_image)
            completed = check_for_barcode(t_webcam_image, '')
        
        #Finished
        self.started = False
        self.logger.debug("Done with robot loop")
    
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


#Instantiate the logger
loggerObj = Logger(__name__)
logger = loggerObj.getLoggerInstance()
        
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
        logger.exception("Exception enumerating the serial ports")
        raise IterationError

    for i in itertools.count():
        try:
            val = _winreg.EnumValue(key, i)
            yield str(val[1])
        except EnvironmentError:
            logger.exception("Exception enumerating the serial ports")
            break

def _connect(robot, save_settings=True):
    '''
    Scan through ports attempting to connect to the robot.
    If save_settings is True, then save the port information.
    '''
    
    for port in enumerate_serial_ports():
        logger.debug('found port %s' % port)
    
    for port in enumerate_serial_ports():
        logger.debug("attempting port %s" % port)
        success = robot.connect(port)
        if success:
            if save_settings:
                export_settings(gado_port=port)
            return True
    return False