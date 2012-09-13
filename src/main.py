'''
The primary Gado program.

This provides a user interface for managing the robot
including creating new artifact sets and starting and
stopping scan jobs.

A few definitions:
 - an artifact is an image or document to be scanned by Gado
 - an image is a picture of either the front or the back of
   an artifact, taken by the scanner or the web cam
 - an artifact set is a collection of artifacts. when a bunch
   of artifacts are loaded into the 'in' tray, they are all
   considered to be a part of the same 'artifact set'
'''
from gado.GadoGui import GadoGui
from gado.gado_sys import GadoSystem
from gado.Logger import Logger
from Tkinter import *
from threading import Thread, Lock
from Queue import Queue
from gado.functions import fetch_from_queue
import gado.messages as messages
import PIL.Image
import ImageTk
import ttk
import sys
import time
import logging

#definitions
LOGGING_LEVEL = logging.DEBUG
    
# This thread is responsible for:
#   - Creating the Gui object (Everything the end user sees/interacts with)
#   - Passing in both queues to that object (so that the logic and gui threads can talk)
#   - Actually loading up and initializing the gui

class GuiThread(Thread):
    
    def __init__(self, q_in, q_out):
        #Instantiate logger object
        loggerObj = Logger(self.__class__.__name__)
        self.logger = loggerObj.getLoggerInstance()
        
        #Load in queues
        self.q_in = q_in
        self.q_out = q_out
        
        self.logger.info("GuiThread\tcreating the gui")
        self.gui = GadoGui(q_in, q_out)
        Thread.__init__(self)
        
    def run(self):
        self.logger.info("GuiThread\tloading GUI elements")
        self.gui.load()
        self.logger.debug("GuiThread\tcalling finished tk.mainloop")
        
        #Once the thread is done loading, exit
        sys.exit()

# This thread is responsible for:
#   - Creating the Gado System object (Main logic for software)
#   - Passing in communication queues to that object
#   - Loading and executing the logic (robot movements/connections and the like)

class LogicThread(Thread):
    
    def __init__(self, q_in, q_out, recovered=False):
        #Instantiate logger object
        loggerObj = Logger(self.__class__.__name__)
        self.logger = loggerObj.getLoggerInstance()
        
        #Load in the queues
        self.q_in = q_in
        self.q_out = q_out
        
        self.logger.info("LogicThread\tintializing GadoSystem")
        
        self.gado_sys = GadoSystem(q_in, q_out, recovered)
        self.logger.debug("LogicThread\tcompleted intializing GadoSystem")
        
        Thread.__init__(self)
    
    def run(self):
        self.logger.info("LogicThread\tcalling main loop on gado_sys")
        
        self.gado_sys.load()
        self.gado_sys.mainloop()
        
        self.logger.debug("LogicThread\tfinished main loop on gado_sys")
        
        
#Main program section
if __name__ == '__main__':
    
    #Instantiate logger object
    loggerObj = Logger(__name__)
    logger = loggerObj.getLoggerInstance()
    
    logger.info("Initializing Gado Robot Management Interface")
       
    #Initialize communications queues
    q_gui_to_sys = Queue()
    q_sys_to_gui = Queue()
    
    #Instantiate both the Gui and Logic threads
    t1 = GuiThread(q_sys_to_gui, q_gui_to_sys)
    t2 = LogicThread(q_gui_to_sys, q_sys_to_gui)
    
    #Start up both threads independently
    t1.start()
    t2.start()
    
    #Main program loop
    while True:
        #Wait for the logic thread to finish running
        t2.join()
        
        logger.debug('main\tThread 2 Joined')
        
        #If there is a message waiting from the Gui
        if not q_gui_to_sys.empty():
            msg = fetch_from_queue(q_gui_to_sys)
            
            #If that message is to kill the application
            if msg[0] == messages.MAIN_ABANDON_SHIP:
                sys.exit()
                
        logger.debug('main\tThread 2 Recovering')
        
        #Re-instantiate the logic thread and run it again
        t2 = LogicThread(q_gui_to_sys, q_sys_to_gui, True)
        t2.start()
    
    #Wait for the Gui thread to finish running
    t1.join()
    logger.debug('main\tThread 1 Joined')
    
    #Exit out of program
    sys.exit()