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
from gado.GadoGui import *
from Tkinter import *
from gado.Robot import *

if __name__ == '__main__':
    print "Gado Robot Management Interface"
    # This is where we run Gado from!
    
    #Import current gado settings
    settings = import_settings()
    
    #Get access to the DB
    db = DBFactory(**settings).get_db()
    
    #Place db in globals
    globals()['db'] = db
    
    #Create instance of robot
    gado = None#Robot('COM7')
    
    root = Tk()
    root.title("Gado Robot Management Interface")
    
    gui = GadoGui(master=root, db=db, gado=gado)
    gui.mainloop()
    
    root.destroy()