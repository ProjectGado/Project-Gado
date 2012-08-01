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
from gado.functions import import_settings
from gado.GadoGui import GadoGui
from gado.Robot import Robot
from gado.db import DBFactory, DBInterface
from Tkinter import Tk

if __name__ == '__main__':
    print "Initializing Gado Robot Management Interface"
    
    # Import current gado settings
    settings = import_settings()
    
    # Get access to the DB
    db = DBFactory(**settings).get_db()
    db_interface = DBInterface(db)
    
    #Create instance of robot
    #gado = Robot('COM7')
    
    # Get the window stuff up and running
    tk = Tk()
    gui = GadoGui(db=db, db_interface=db_interface, settings = settings, root = tk)
    gui.mainloop()
    
    tk.destroy()