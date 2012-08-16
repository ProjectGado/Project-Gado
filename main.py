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
from gado.Scanner import Scanner
from Tkinter import Tk
import threading
from gado.Webcam import *

def create_dummy_artifact_sets(db, clear=True):
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
    
    if clear:
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
        
if __name__ == '__main__':
    print "Initializing Gado Robot Management Interface"
    
    # Import current gado settings
    settings = import_settings()
    
    # Get access to the DB
    db = DBFactory(**settings).get_db()
    db_interface = DBInterface(db)
    
    create_dummy_artifact_sets(db)
    
    #Create instance of robot
    gado = Robot(**settings)
    
    #Create instance of the Scanner object
    scanner = Scanner(**settings)
    #Perhaps move this connection stuff elsewhere...
    success = scanner.connectToScannerGui()
    #scanner.setDPI("600")
    #scanner.scanImage("C:\Users\Robert\Downloads", "scannedImage.png")
    #print "Scanner found: %s" % success
    
    #Create root of application
    tk = Tk()
    
    #Start up the Gado System for management
    gado_sys = GadoSystem(db_interface, gado, tk, scanner)
    
    #When we exit, destroy the root of the application
    tk.destroy()
    