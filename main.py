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
from gado.gado_sys import GadoSystem
from gado.db import DBFactory, DBInterface
from Tkinter import Tk
import threading
from gado.Webcam import *

        
if __name__ == '__main__':
    print "Initializing Gado Robot Management Interface"
    
    #Test picture taking
    camera = Webcam()
    print "Connected to webcam: %s" % str(camera.connect())
    #camera.saveImage("superTest.jpg", camera.returnImage())
    
    # Import current gado settings
    settings = import_settings()
    
    # Get access to the DB
    db = DBFactory(**settings).get_db()
    
    
    '''
    a
      b
        c
        d
      e
        f
    g
      h
        i
    '''
    db(db.artifacts.id > 0).delete()
    db(db.artifact_sets.id > 0).delete()
    
    a_id = db.artifact_sets.insert(name='a', parent=None)
    b_id = db.artifact_sets.insert(name='b', parent=a_id)
    c_id = db.artifact_sets.insert(name='c', parent=b_id)
    d_id = db.artifact_sets.insert(name='d', parent=b_id)
    e_id = db.artifact_sets.insert(name='e', parent=a_id)
    f_id = db.artifact_sets.insert(name='f', parent=e_id)
    g_id = db.artifact_sets.insert(name='g', parent=None)
    h_id = db.artifact_sets.insert(name='h', parent=g_id)
    i_id = db.artifact_sets.insert(name='i', parent=h_id)
    
    db.artifacts.insert(artifact_set=c_id)
    db.artifacts.insert(artifact_set=d_id)
    db.artifacts.insert(artifact_set=i_id)
    db.artifacts.insert(artifact_set=f_id)
    
    
    db_interface = DBInterface(db)
    
    #Create instance of robot
    gado = Robot(**settings)
    
    #Create root of application
    tk = Tk()
    
    #Start up the Gado System for management
    gado_sys = GadoSystem(db_interface, gado, camera, tk)
    
    #Create the window which will display the autoconnect progress bar
    progressBar = ProgressBar(root=tk)
    
    # Create and launch the thread which will try to autoconnect to the Gado
    connectionThread = AutoConnectThread(gado_sys, progressBar)
    connectionThread.start()
    
    #Display the progress bar for the autoconnection process
    progressBar.mainloop()
    
    #Create the main gui object
    #gui = GadoGui(tk, db_interface, gado_sys)
    
    #We're done autoconnecting, so destroy the progress bar window
    progressBar.destroy()
    
    #Launch the main GUI
    #gui.mainloop()
    
    #When we exit, destroy the root of the application
    tk.destroy()
    