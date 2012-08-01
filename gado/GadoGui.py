import sys
from Tkinter import *
import tkMessageBox
import Pmw
import os.path
import serial
import re
import subprocess
from gado.Robot import Robot
from gado.functions import *

class GadoGui(Frame):
    
    #Widgets
    global artifactSetDropDown
    global artifactSetWindow
    global artifactSets
    global nameEntry
    global commPortDropDown
    
    global currentParent
    
    #Robot object
    global gado
    global settings
    
    #Serial object
    global serialConnection
    
    def __init__(self, db=None, db_interface=None, gado=None, root=None, settings=None):
        # Create the root frame
        if not root:
            self.root = Tk()
            self.root.title("Gado Robot Management Interface")
        else:
            self.root = root
        
        #Initialize the master frame
        Frame.__init__(self, self.root)
        
        #Store the settings (if any)
        self.settings = settings
        
        #Init the serial object
        self.serialConnection = serial.Serial()
        
        #Try to autoconnect to the robot
        self.autoConnectRobot()
        
        #Store the database connection as a global
        self.db = db
        self.dbi = db_interface
        
        #Store the robot object as a global
        #self.gado = gado
        
        #Create all menus for application
        self.createMenus(self.root)

        #Create a toplevel window to deal with artifactSet management
        self.artifactSetWindow = Toplevel(self)
        
        self.createTopLevelWidgets()
        
        self.artifactSetWindow.protocol("WM_DELETE_WINDOW", self.artifactSetWindow.withdraw)
        self.artifactSetWindow.withdraw()
        
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
        #Create the connection control widgets
        self.createConnectionControlWidgets()
        
        #Create the artifactSet section
        self.createArtifactSetWidgets()
        
        #Create the Control section
        self.createControlWidgets()
        
        #Create the status center
        self.createStatusWidgets()
        
    def createConnectionControlWidgets(self):
        #Create the label
        self.connectionLabel = Label(self)
        self.connectionLabel["text"] = "Connection Control: "
        self.connectionLabel.grid(row=0, column=0, sticky=N+S+E+W, padx=10, pady=5)
        
        #Comm port selection lab3l
        self.commSelectLabel = Label(self)
        self.commSelectLabel["text"] = "Select a Comm Port: "
        self.commSelectLabel.grid(row=1, column=0, sticky=N+S+E+W, padx=10, pady=5, columnspan=2)
        
        #Comm port selection dropdown
        self.commPortDropDown = Pmw.ComboBox(self)
        self.commPortDropDown.grid(row=1, column=2, sticky=N+S+E+W, padx=10, pady=5, columnspan=2)
        
        #Add in the actual available comm ports
        ports = self.listCommPorts()
        
        for port in ports:
            self.commPortDropDown.insert(END, port)
            
        #Create the buttons to connect and disconnect the robot
        self.connectButton = Button(self)
        self.connectButton["text"] = "Connect to Robot"
        self.connectButton["command"] = self.connectToRobot
        self.connectButton.grid(row=2, column=0, sticky=N+S+E+W, padx=10, pady=5, columnspan=2)
        
        self.disconnectButton = Button(self)
        self.disconnectButton["text"] = "Disconnect from Robot"
        self.disconnectButton["command"] = self.disconnectFromRobot
        self.disconnectButton.grid(row=2, column=2, sticky=N+S+E+W, padx=10, pady=5, columnspan=2)
        
    def createArtifactSetWidgets(self):
        #Create label
        self.artifactSetLabel = Label(self)
        self.artifactSetLabel["text"] = "ArtifactSet: "
        self.artifactSetLabel.grid(row=3, column=0, sticky=W, padx=10, pady=5)
        
        #Create dropdown for artifactSet selection
        self.artifactSetDropDown = Pmw.ComboBox(self)
        self.artifactSetDropDown.grid(row=4, column=0, sticky=N+S+E+W, padx=10, pady=5, columnspan=2)
        
        #Add entries to that dropdown
        
        #At the moment, we don't have anything built to insert the most recent artifactSets
        #We'll need to tie that into the database abstraction layer
        #For the time being we'll put in some temp data
        self.artifactSetDropDown.insert(END, "Loc 1")
        self.artifactSetDropDown.insert(END, "Loc 2")
        
        #Add the button to create a new artifactSet
        self.addArtifactSetButton = Button(self)
        self.addArtifactSetButton["text"] = "New Artifact Set"
        self.addArtifactSetButton["command"] = self.addArtifactSet
        self.addArtifactSetButton.grid(row=4, column=2, sticky=N+S+E+W, padx=10, pady=5, columnspan=2)
        
    def createControlWidgets(self):
        #Create label
        self.controlLabel = Label(self)
        self.controlLabel["text"] = "Control: "
        self.controlLabel.grid(row=5, column=0, sticky=W, padx=10, pady=5)
        
        #Create start/stop/pause/restart buttons
        self.startButton = Button(self)
        self.startButton["text"] = "Start"
        self.startButton["command"] = self.startRobot
        self.startButton.grid(row=6, column=0, sticky=N+S+E+W, padx=10, pady=5)
        
        self.pauseButton = Button(self)
        self.pauseButton["text"] = "Pause"
        self.pauseButton["command"] = self.pauseRobot
        self.pauseButton.grid(row=6, column=1, sticky=N+S+E+W, padx=10, pady=5)
        
        self.stopButton = Button(self)
        self.stopButton["text"] = "Stop"
        self.stopButton["command"] = self.stopRobot
        self.stopButton.grid(row=6, column=2, sticky=N+S+E+W, padx=10, pady=5)
        
        self.resetButton = Button(self)
        self.resetButton["text"] = "Reset"
        self.resetButton["command"] = self.resetRobot
        self.resetButton.grid(row=6, column=3, sticky=N+S+E+W, padx=10, pady=5)
        
    def createStatusWidgets(self):
        #Create label
        self.statusLabel = Label(self)
        self.statusLabel["text"] = "Status: "
        self.statusLabel.grid(row=8, column=0, sticky=W, padx=10, pady=5)
        
        #Actual message box
        self.messageEntry = Entry(self)
        self.messageEntry.grid(row=9, column=0, columnspan=4, sticky=N+S+E+W, padx=10, pady=5)
    
    def createTopLevelWidgets(self):
        self.artifactSetWindow.title("Manage Artifact Sets")
        
        #Create the artifactSet list box
        self.artifactSets = Pmw.ScrolledListBox(self.artifactSetWindow,
                                       items=(),
                                       labelpos='nw',
                                       label_text='Select a Parent: ',
                                       listbox_height=6,
                                       selectioncommand=self.setSelectedParent,
                                       usehullsize=1,
                                       hull_width = 200,
                                       hull_height = 200,)
        self.artifactSets.grid(row=0, column=0, columnspan=2, sticky=N+S+E+W, padx=10, pady=5)
        
        #Create a label for the name entry
        self.nameLabel = Label(self.artifactSetWindow)
        self.nameLabel["text"] = "Artifact Set Name: "
        self.nameLabel.grid(row=1, column=0, sticky=N+S+E+W, padx=10, pady=5)
        
        #Create the entry box for the name input
        self.nameEntry = Entry(self.artifactSetWindow)
        self.nameEntry.grid(row=1, column=1, sticky=N+S+E+W, padx=10, pady=5)
        
        #Create the add button
        self.addButton = Button(self.artifactSetWindow)
        self.addButton["text"] = "Add"
        self.addButton["command"] = self.insertNewArtifactSet
        self.addButton.grid(row=2, column=0, sticky=N+S+E+W, padx=10, pady=5)
        
        #Create the delete button
        self.deleteButton = Button(self.artifactSetWindow)
        self.deleteButton["text"] = "Delete"
        self.deleteButton["command"] = self.pauseRobot
        self.deleteButton.grid(row=2, column=1, sticky=N+S+E+W, padx=10, pady=5)
        
    #################################################################################
    #####                           LOCATION WINDOW FUNCTIONS                   #####
    #################################################################################    
    
    def setSelectedParent(self):
        #Remove any tabs that are being displayed
        
        idx = self.artifactSets.curselection()[0]
        self.currentParent = self.artifact_sets[int(idx)][0]
        print "Have %s selected" % (self.currentParent)
            
    def calculateChildLevel(self, artifactSetId):
        sets = self.db(self.db.artifact_sets.id == artifactSetId).select()
        for s in sets:
            if(s['parent'] != None):
                return self.calculateChildLevel(s['parent']) + 1
            else:
                return 0
            
    def buildArtifactSetList(self):
        #Clear current list
        self.artifactSets.delete(0, 'end')
        
        #Need to get current artifact sets and insert them into the list box
        self.artifact_sets = self.dbi.artifact_set_list()
        for id, indented_name in self.artifact_sets:
            self.artifactSets.insert('end', indented_name)
            
    def addArtifactSet(self):
        #Function call to add a new artifactSet through the DAL
        print "Adding new artifactSet..."
        
        #Build the list of current artifactSets
        self.buildArtifactSetList()
            
        #Bring the toplevel window into view
        self.artifactSetWindow.deiconify()
    
    #This function will insert a new artifactSet into the database
    #IMPORTANT: at the moment we're assuming that all artifactSet names will be unique
    #This is probably a false assumption so we should figure out some way to deal with Ids instead
    def insertNewArtifactSet(self):
        print "Going to insert new artifact_set\nCurrent parent: %s and insert: %s" % (self.currentParent, self.nameEntry.get())
        self.dbi.add_artifact_set(self.nameEntry.get(), self.currentParent)
        self.buildArtifactSetList()
        
    #################################################################################
    #####                           FUNCTION WRAPPERS                           #####
    #################################################################################

    #Query the current system for all available serial ports
    #Try to to connect to each port and "shake hands" with the robot
    #If it is in fact the robot, the handshake will match the expected value
    #in the settings file
    def autoConnectRobot(self):
        
        #Collect all ports available
        ports = self.listCommPorts()
        
        #Test each one until we find the Gado (or we don't)
        for port in ports:
            #Try these settings
            self.serialConnection.baudrate = self.settings['baudrate']
            self.serialConnection.port = port
            
            #Try and connect to this serial port
            try:
                self.serialConnection.open()
                
                #create a connection to the robot so we can try to shake hands
                gado = Robot(self.serialConnection, self.settings)
                
                if self.serialConnection.isOpen() and gado.handshake() == self.settings['handshake']:
                    print "Found the gado! at port: %s with handshake: %s" % (port, gado.handshake())
            except:
                print "No luck with port: %s" % (port)
            
    def listCommPorts(self):
        
        #Query the comm ports available on the system
        rawPortList = str(subprocess.check_output(["python", "-m", "serial.tools.list_ports"]))
        ports = re.findall('(COM\d+)', rawPortList)
        
        #Return a list of those ports
        return ports
    
    def connectToRobot(self):
        #Check to see if a comm port is selected
        if self.commPortDropDown.get() != None:
            
            #Apply settings
            self.serialConnection.baudrate = self.settings['baudrate']
            self.serialConnection.port = self.commPortDropDown.get()
            
            #Open the connection
            try:
                self.serialConnection.open()
            except:
                tkMessageBox.showerror("Connection Status", "Failed with message: %s" % (sys.exc_info()[1]))
                return False
            
            #check to make sure it was a success
            if self.serialConnection.isOpen():
                
                #Connect to actual robot
                self.gado = Robot(self.serialConnection, self.settings)
                tkMessageBox.showinfo("Connection Status", "Successfully connected to Gado!")
                
                return True
        else:
            tkMessageBox.showerror("Connection Status", "Could not connect to comm port: %s" % (self.commPortDropDown.get()))
            return False
    
    def disconnectFromRobot(self):
        #Check to see if port is already open
        if self.serialConnection.isOpen():
            self.serialConnection.close()
            
            tkMessageBox.showinfo("Connection Status", "Closed connection to Gado!")
        else:
            tkMessageBox.showerror("Connection Status", "No open connection found!")
    
    def startRobot(self):
        #Function call to start robot's operation
        print "Starting robot..."
        
        #self.gado.lowerAndLiftInternal()
        #self.gado.sendRawActuatorWithoutBlocking(200)
        self.gado.start()
        
    def pauseRobot(self):
        #Function call to pause robot's operation
        print "Pausing robot..."
        self.gado.pause()
        
    def stopRobot(self):
        #Function call to stop robot's operation
        print "Stopping robot..."
        self.gado.stop()
        
    def resetRobot(self):
        #Function call to reset the robot's operations
        print "Restarting robot..."
        self.gado.reset()