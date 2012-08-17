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

class GuiThread(Thread):
    def __init__(self, tk, q, l):
        self.tk = tk
        self.q = q
        self.l = l
        print "GuiThread\tcreating the gui"
        self.gui = GadoGui(tk, q, l)
        Thread.__init__(self)
        
    def run(self):
        print "GuiThread\tloading GUI elements"
        self.gui.load()
        print "GuiThread\tcalling tk.mainloop"
        self.tk.mainloop()
        print "GuiThread\tcalling finished tk.mainloop"
        #self.gui.mainloop()
        exit()

class LogicThread(Thread):
    def __init__(self, q, l):
        self.q = q
        self.l = l
        print "LogicThread\tintializing GadoSystem"
        self.gado_sys = GadoSystem(q, l)
        print "LogicThread\tcompleted intializing GadoSystem"
        Thread.__init__(self)
    
    def run(self):
        print "LogicThread\tcalling main loop on gado_sys"
        self.gado_sys.mainloop()
        print "LogicThread\tfinished main loop on gado_sys"
        
if __name__ == '__main__':
    print "Initializing Gado Robot Management Interface"
    
    q = Queue()
    tk = Tk()
    l = Lock()
    l.acquire()
    
    t1 = GuiThread(tk, q, l)
    t2 = LogicThread(q, l)
    
    l.release()
    t1.start()
    l.acquire()
    t2.start()
    l.release()
    
    
    # It would be nice to check to see if the LogicThread ate it.
    