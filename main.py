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
from Tkinter import Tk
from threading import Thread, Lock
from Queue import Queue
from gado.functions import fetch_from_queue
import gado.messages as messages
import sys

class GuiThread(Thread):
    def __init__(self, q_in, q_out):
        self.q_in = q_in
        self.q_out = q_out
        print "GuiThread\tcreating the gui"
        self.gui = GadoGui(q_in, q_out)
        Thread.__init__(self)
        
    def run(self):
        print "GuiThread\tloading GUI elements"
        self.gui.load()
        print "GuiThread\tcalling finished tk.mainloop"
        #self.gui.mainloop()
        sys.exit()

class LogicThread(Thread):
    def __init__(self, q_in, q_out, recovered=False):
        self.q_in = q_in
        self.q_out = q_out
        print "LogicThread\tintializing GadoSystem"
        self.gado_sys = GadoSystem(q_in, q_out, recovered)
        print "LogicThread\tcompleted intializing GadoSystem"
        Thread.__init__(self)
    
    def run(self):
        print "LogicThread\tcalling main loop on gado_sys"
        self.gado_sys.mainloop()
        print "LogicThread\tfinished main loop on gado_sys"
        
if __name__ == '__main__':
    print "Initializing Gado Robot Management Interface"
    
    q_gui_to_sys = Queue()
    q_sys_to_gui = Queue()
    
    t1 = GuiThread(q_sys_to_gui, q_gui_to_sys)
    t2 = LogicThread(q_gui_to_sys, q_sys_to_gui)
    
    t1.start()
    t2.start()
    
    while True:
        t2.join()
        print 'main\tThread 2 Joined'
        if not q_gui_to_sys.empty():
            msg = fetch_from_queue(q_gui_to_sys)
            if msg[0] == messages.MAIN_ABANDON_SHIP:
                sys.exit()
        print 'main\tThread 2 Recovering'
        t2 = LogicThread(q_gui_to_sys, q_sys_to_gui, True)
        t2.start()
    
    t1.join()
    print 'main\tThread 1 Joined'
    sys.exit()
    #print 'main\tfetching MAIN_ABANDON_SHIP'
    #msg = fetch_from_queue(q, messages.MAIN_ABANDON_SHIP)
    #print 'main\tfetched MAIN_ABANDON_SHIP'
    #exit()
    # It would be nice to check to see if the LogicThread ate it.
    