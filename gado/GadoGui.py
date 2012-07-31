import sys
from Tkinter import *
import tkMessageBox
import Pmw
import os.path
import re
from gado.db import DBFactory
from gado.functions import *

class GadoGui(Frame):
    
    #Widgets
    global locationDropDown
    global locationWindow
    global locations
    global nameEntry
    
    global currentParent
    
    #Database object
    global db
    
    #Robot object
    global gado
    
    def __init__(self, master=None, db=None, gado=None):

        #Initialize the master frame
        Frame.__init__(self, master)
        
        #Store the database connection as a global
        self.db = db
        
        #Store the robot object as a global
        self.gado = gado
        
        #Create all menus for application
        self.createMenus(master)

        #Create a toplevel window to deal with location management
        self.locationWindow = Toplevel(self)
        
        self.createTopLevelWidgets()
        
        self.locationWindow.protocol("WM_DELETE_WINDOW", self.locationWindow.withdraw)
        self.locationWindow.withdraw()
        
        #Init current selected parent to None
        self.currentParent = None
        
        #Pack the widgets and create the GUI
        self.pack()
        self.createWidgets()
        
    #################################################################################
    #####                           MENU FUNCTIONS                              #####
    #################################################################################
    
    def createMenus(self, master=None):
        
        #Create the drop down menu
        self.menubar = Menu(master)
        
        #Create the file menu
        self.fileMenu = self.createFileMenu(self.menubar, master)
        
        #Create the Settings menu
        self.settingsMenu = self.createSettingsMenu(self.menubar, master)
        
        #Add both menus to the menubar
        self.menubar.add_cascade(label="File", menu=self.fileMenu)
        self.menubar.add_cascade(label="Settings", menu=self.settingsMenu)
        
        #Assign menubar
        master.config(menu=self.menubar)
        
    def createFileMenu(self, menubar=None, master=None):
        
        self.fileMenu = Menu(self.menubar, tearoff=0)
        self.fileMenu.add_command(label="Quit", command=master.quit)
        
        return self.fileMenu
    
    def createSettingsMenu(self, menubar=None, master=None):
        
        self.settingsMenu = Menu(self.menubar, tearoff=0)
        self.settingsMenu.add_command(label="Quit", command=master.quit)
        
        return self.settingsMenu
        
    #################################################################################
    #####                           WIDGET FUNCTIONS                            #####
    #################################################################################
    
    def createWidgets(self):
        
        #Create the location section
        self.createLocationWidgets()
        
        #Create the Control section
        self.createControlWidgets()
        
        #Create the status center
        self.createStatusWidgets()
        
    def createLocationWidgets(self):
        #Create label
        self.locationLabel = Label(self)
        self.locationLabel["text"] = "Location: "
        self.locationLabel.grid(row=0, column=0, sticky=W, padx=10, pady=5)
        
        #Create dropdown for location selection
        self.locationDropDown = Pmw.ComboBox(self)
        self.locationDropDown.grid(row=1, column=0, sticky=N+S+E+W, padx=10, pady=5, columnspan=2)
        
        #Add entries to that dropdown
        
        #At the moment, we don't have anything built to insert the most recent locations
        #We'll need to tie that into the database abstraction layer
        #For the time being we'll put in some temp data
        self.locationDropDown.insert(END, "Loc 1")
        self.locationDropDown.insert(END, "Loc 2")
        
        #Add the button to create a new location
        self.addLocationButton = Button(self)
        self.addLocationButton["text"] = "New Location"
        self.addLocationButton["command"] = self.addLocation
        self.addLocationButton.grid(row=1, column=2, sticky=N+S+E+W, padx=10, pady=5, columnspan=2)
        
    def createControlWidgets(self):
        #Create label
        self.controlLabel = Label(self)
        self.controlLabel["text"] = "Control: "
        self.controlLabel.grid(row=2, column=0, sticky=W, padx=10, pady=5)
        
        #Create start/stop/pause/restart buttons
        self.startButton = Button(self)
        self.startButton["text"] = "Start"
        self.startButton["command"] = self.startRobot
        self.startButton.grid(row=3, column=0, sticky=N+S+E+W, padx=10, pady=5)
        
        self.pauseButton = Button(self)
        self.pauseButton["text"] = "Pause"
        self.pauseButton["command"] = self.pauseRobot
        self.pauseButton.grid(row=3, column=1, sticky=N+S+E+W, padx=10, pady=5)
        
        self.stopButton = Button(self)
        self.stopButton["text"] = "Stop"
        self.stopButton["command"] = self.stopRobot
        self.stopButton.grid(row=3, column=2, sticky=N+S+E+W, padx=10, pady=5)
        
        self.resetButton = Button(self)
        self.resetButton["text"] = "Reset"
        self.resetButton["command"] = self.resetRobot
        self.resetButton.grid(row=3, column=3, sticky=N+S+E+W, padx=10, pady=5)
        
    def createStatusWidgets(self):
        #Create label
        self.statusLabel = Label(self)
        self.statusLabel["text"] = "Status: "
        self.statusLabel.grid(row=5, column=0, sticky=W, padx=10, pady=5)
        
        #Actual message box
        self.messageEntry = Entry(self)
        self.messageEntry.grid(row=6, column=0, columnspan=4, sticky=N+S+E+W, padx=10, pady=5)
    
    def createTopLevelWidgets(self):
        self.locationWindow.title("Manage Locations")
        
        #Create the location list box
        self.locations = Pmw.ScrolledListBox(self.locationWindow,
                                       items=(),
                                       labelpos='nw',
                                       label_text='Select a Parent: ',
                                       listbox_height=6,
                                       selectioncommand=self.setSelectedParent,
                                       usehullsize=1,
                                       hull_width = 200,
                                       hull_height = 200,)
        self.locations.grid(row=0, column=0, columnspan=2, sticky=N+S+E+W, padx=10, pady=5)
        
        #Create a label for the name entry
        self.nameLabel = Label(self.locationWindow)
        self.nameLabel["text"] = "Artifact Set Name: "
        self.nameLabel.grid(row=1, column=0, sticky=N+S+E+W, padx=10, pady=5)
        
        #Create the entry box for the name input
        self.nameEntry = Entry(self.locationWindow)
        self.nameEntry.grid(row=1, column=1, sticky=N+S+E+W, padx=10, pady=5)
        
        #Create the add button
        self.addButton = Button(self.locationWindow)
        self.addButton["text"] = "Add"
        self.addButton["command"] = self.insertNewLocation
        self.addButton.grid(row=2, column=0, sticky=N+S+E+W, padx=10, pady=5)
        
        #Create the delete button
        self.deleteButton = Button(self.locationWindow)
        self.deleteButton["text"] = "Delete"
        self.deleteButton["command"] = self.pauseRobot
        self.deleteButton.grid(row=2, column=1, sticky=N+S+E+W, padx=10, pady=5)
        
    #################################################################################
    #####                           LOCATION WINDOW FUNCTIONS                   #####
    #################################################################################    
    
    def setSelectedParent(self):
        #Remove any tabs that are being displayed
        self.currentParent = re.sub('   ', '', str(self.locations.getvalue()[0]))
        print "Have %s selected" % (self.currentParent)
            
    def calculateChildLevel(self, artifactSetId):
        sets = self.db(self.db.artifact_sets.id == artifactSetId).select()
        for s in sets:
            if(s['parent'] != None):
                return self.calculateChildLevel(s['parent']) + 1
            else:
                return 0
            
    def buildLocationList(self):
        #Clear current list
        self.locations.delete(0, 'end')
        
        #Need to get current artifact sets and insert them into the list box
        sets = self.db(self.db.artifact_sets.id > 0).select()
        for s in sets:
            #Calculate how deep in the tree this child
            numTabs = str(self.calculateChildLevel(s['id']))
            
            #Append the correct number of tabs
            for x in range(int(numTabs)):
                s['name'] = '   %s' % (s['name'])
                
            #Insert the formatted child
            self.locations.insert('end', '%s' % (s['name']))
            
    def addLocation(self):
        #Function call to add a new location through the DAL
        print "Adding new location..."
        
        #Build the list of current locations
        self.buildLocationList()
            
        #Bring the toplevel window into view
        self.locationWindow.deiconify()
    
    #This function will insert a new location into the database
    #IMPORTANT: at the moment we're assuming that all location names will be unique
    #This is probably a false assumption so we should figure out some way to deal with Ids instead
    def insertNewLocation(self):
        print "Going to insert new artifact_set\nCurrent parent: %s and insert: %s" % (self.currentParent, self.nameEntry.get())
        
        row = self.db(self.db.artifact_sets.name == self.currentParent).select().first()
        
        #Check to make sure we got a result
        if row is not None:
            #Insert the new child
            self.db.artifact_sets.insert(name=self.nameEntry.get(), parent=row['id'])
            self.db.commit()
            
            #Update listbox
            self.buildLocationList()
        
    #################################################################################
    #####                           FUNCTION WRAPPERS                           #####
    #################################################################################

    def startRobot(self):
        #Function call to start robot's operation
        print "Starting robot..."
        
        #self.gado.lowerAndLiftInternal()
        #self.gado.sendRawActuatorWithoutBlocking(200)
        self.gado.moveActuator(70)
        
    def pauseRobot(self):
        #Function call to pause robot's operation
        print "Pausing robot..."
        self.gado.moveArm(50)
        
    def stopRobot(self):
        #Function call to stop robot's operation
        print "Stopping robot..."
        
    def resetRobot(self):
        #Function call to reset the robot's operations
        print "Restarting robot..."
        
        #self.gado.goHome()
        