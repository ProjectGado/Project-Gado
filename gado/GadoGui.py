import sys
from Tkinter import *
import tkMessageBox
import ttk
#from gado.ProgressMeter import *
import Pmw
import time
import platform
from gado.Robot import Robot
from gado.functions import *

class GadoGui(Frame):
    
    #Widgets
    global artifactSetDropDown
    global artifactSetWindow
    global artifactSets
    global nameEntry
    global commPortDropDown
    global configDialog
    
    global currentParent
    
    #Robot object
    global gado
    
    #Enums for which aspect of the gado we're configuring
    INPUT_TRAY_LOCATION = 0
    OUTPUT_TRAY_LOCATION = 1
    SCANNER_LOCATION = 2
    SCANNER_HEIGHT = 3
    
    global currentConfParam
    
    #Time objects for setup MOVE IT ALL TO ITS OWN CLASS
    
    global _lastTime
    global _currentTime
    
    def _demo(meter, value):
        meter.set(value)
        if value < 1.0:
            value = value + 0.005
            meter.after(50, lambda: _demo(meter, value))
        else:
            meter.set(value, 'Demo successfully finished')
    
    def __init__(self, root, db_interface, gado_system):
        # Create the root frame
        self.root = root
        
        #Initialize the master frame
        Frame.__init__(self, self.root)
        
        # The Gado ecosystem manager
        self.gado_sys = gado_system
        
        #Init the time
        self._lastTime = 0
        self._currentTime = 0
        
        #Store the database connection as a global
        self.dbi = db_interface
        
        #Create all menus for application
        self.createMenus(self.root)

        #Create a toplevel window to deal with artifactSet management
        self.artifactSetWindow = Toplevel(self)
        
        self.createTopLevelWidgets()
        
        self.artifactSetWindow.protocol("WM_DELETE_WINDOW", self.artifactSetWindow.withdraw)
        self.artifactSetWindow.withdraw()
        
        #configure the layout of the gado setup
        self.configurationWindow = Toplevel(self)
        
        #create the config dialog toplevel object
        self.configDialog = Toplevel(self)
        
        self.configDialog.protocol("WM_DELETE_WINDOW", self.configDialog.withdraw)
        self.configDialog.withdraw()
        
        self.createConfigurationWindowWidgets()
        
        self.configurationWindow.protocol("WM_DELETE_WINDOW", self.configurationWindow.withdraw)
        self.configurationWindow.withdraw()
        
        #Init current selected parent to None
        self.currentParent = None
        
        #Set the current conf parameter to None
        self.currentConfParam = None
        
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
        self.settingsMenu.add_command(label="Configure Layout", command=self.configureLayout)
        
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
        ports = ['a', 'b']
        
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
        
    def createConfigurationWindowWidgets(self):
        #Set the title
        self.configurationWindow.title("Configure Your Setup")
        
        self.mylabel = Label(self.configurationWindow)
        self.mylabel["text"] = "Set the locations for your current setup"
        self.mylabel.grid(row=0, column=0, sticky=N+S+E+W, padx=10, pady=5)
        
        self.inputTrayButton = Button(self.configurationWindow)
        self.inputTrayButton["text"] = "Input Tray Location"
        self.inputTrayButton["command"] = lambda: self.launchConfigDialog(self.INPUT_TRAY_LOCATION)#self.configDialog.deiconify
        self.inputTrayButton.grid(row=1, column=0, sticky=N+S+E+W, padx=10, pady=5)
        
        self.scannerLocation = Button(self.configurationWindow)
        self.scannerLocation["text"] = "Scanner Location"
        self.scannerLocation["command"] = lambda: self.launchConfigDialog(self.SCANNER_LOCATION)#self.configDialog.deiconify
        self.scannerLocation.grid(row=2, column=0, sticky=N+S+E+W, padx=10, pady=5)
        
        self.outputTrayLocation = Button(self.configurationWindow)
        self.outputTrayLocation["text"] = "Output Tray Location"
        self.outputTrayLocation["command"] = lambda: self.launchConfigDialog(self.OUTPUT_TRAY_LOCATION)#self.configDialog.deiconify
        self.outputTrayLocation.grid(row=3, column=0, sticky=N+S+E+W, padx=10, pady=5)
        
        self.scannerHeight = Button(self.configurationWindow)
        self.scannerHeight["text"] = "Scanner Height"
        self.scannerHeight["command"] = lambda: self.launchConfigDialog(self.SCANNER_HEIGHT)#self.configDialog.deiconify
        self.scannerHeight.grid(row=4, column=0, sticky=N+S+E+W, padx=10, pady=5)
        
    #################################################################################
    #####                           LOCATION WINDOW FUNCTIONS                   #####
    #################################################################################    
    
    def setSelectedParent(self):
        #Remove any tabs that are being displayed
        
        idx = self.artifactSets.curselection()[0]
        self.currentParent = self.artifact_sets[int(idx)][0]
        print "Have %s selected" % (self.currentParent)
            
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
    #####                     CONFIGURATION LAYOUT  FUNCTIONS                   #####
    #################################################################################
    
    def launchConfigDialog(self, parameter):
        #Expose the configDialog window
        self.configDialog.deiconify()
        
        self.currentConfParam = parameter
        print "launched the instruction window wiht param: %s" % self.currentConfParam
    
    def keyboardCallback(self, event):
        
        #Check to see how long ago we recieved a keypress
        #We don't want to flood the robot with commands or it will hang/behave eratically
        
        self._currentTime = time.time()
        print "Time: " + str(self._currentTime)
        if self._currentTime - self._lastTime > 0.1:
            key = event.keycode
            
            if key == 37:
                #Left arrow press
                self.gado_sys.moveArmBackwards()
                
            elif key == 38:
                #Up arrow press
                self.gado_sys.moveActuatorDown()
                
            elif key == 39:
                #Right arrow press
                self.gado_sys.moveArmForward()
                
            elif key == 40:
                #Down arrow press
                self.gado_sys.moveActuatorUp()
            else:
                print "key: " + str(event.keycode)
            
            #Set _lastTime to the _currentTime
            self._lastTime = self._currentTime
        
    def configureLayout(self):
        
        self.createConfigurationWindowWidgets()
        #self.configurationWindow.bind("<Key>", self.keyboardCallback)
        self.configurationWindow.deiconify()
        
        #Create the toplevel window to tell the user what to do to configure the arm/actuator
        self.configDialog.title("Instructions")
        
        self.configDialog.bind("<Key>", self.keyboardCallback)
        
        #Label to tell user what's up
        self.configLabel = Label(self.configDialog)
        self.configLabel["text"] = "Using the arrow keys, move the arm of the robot to the desired location\n\nWhen finished hit Done"
        self.configLabel.grid(row=0, column=0, sticky=N+S+E+W, padx=10, pady=10)
        
        #Done button
        self.doneButton = Button(self.configDialog)
        self.doneButton["text"] = "Done"
        self.doneButton["command"] = self.saveConfig #  DOESN'T EXIST YET
        self.doneButton.grid(row=1, column=0, sticky=N+S+E+W, padx=10, pady=5)
        
        
    #################################################################################
    #####                           FUNCTION WRAPPERS                           #####
    #################################################################################
    
    #Save the particular value from the layout setup process
    def saveConfig(self):
        #Whenever we launch one of the configuration windows (input tray locaiton, scanner height, etc)
        #We also set the currentConfParam to whichever parameter it is we are tweaking
        #This way, we always know what the value we gathered is associated with
        if self.currentConfParam is not None:
            if self.currentConfParam == self.INPUT_TRAY_LOCATION:
                print "Saving input tray location as: %s" % self.gado_sys.getArmPosition()
                
                kwargs = {'arm_in_value' : self.gado_sys.getArmPosition()}
                
            elif self.currentConfParam == self.OUTPUT_TRAY_LOCATION:
                print "Saving output tray location as %s" % self.gado_sys.getArmPosition()
                
                kwargs = {'arm_out_value' : self.gado_sys.getArmPosition()}
                
            elif self.currentConfParam == self.SCANNER_LOCATION:
                print "Saving scanner location as %s" % self.gado_sys.getArmPosition()
                
                kwargs = {'arm_home_value' : self.gado_sys.getArmPosition()}
                
            elif self.currentConfParam == self.SCANNER_HEIGHT:
                print "Saving scanner height as %s" % self.gado_sys.getActuatorPosition()
                
                kwargs = {'actuator_home_value' : self.gado_sys.getActuatorPosition()}
                
            #Export whatever settings have changed
            export_settings(**kwargs)
            
            #Update the settings that are being used by the robot
            self.gado_sys.updateSettings()
        else:
            print "Something went wrong, have no idea which config parameter I'm working with..."
            
        #Get rid of the instructions window    
        self.configDialog.withdraw()
    
    #Query the current system for all available serial ports
    #Try to to connect to each port and "shake hands" with the robot
    #If it is in fact the robot, the handshake will match the expected value
    #in the settings file
    def autoConnectRobot(self):
        
        #Collect all ports available
        ports = self.listCommPorts()
        print "got ports: " + str(ports)
        #Test each one until we find the Gado (or we don't)
        for port in ports:
            #Try these settings
            self.serialConnection.baudrate = 115200#self.settings['baudrate']
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
        system_name = platform.system()
        if system_name == "Windows":
            # Scan for available ports.
            available = []
            for i in range(256):
                try:
                    s = serial.Serial(i)
                    available.append(i)
                    s.close()
                except serial.SerialException:
                    pass
            return available
        elif system_name == "Darwin":
            # Mac
            return glob.glob('/dev/tty*') + glob.glob('/dev/cu*')
        else:
            # Assume Linux or something else
            return glob.glob('/dev/ttyS*') + glob.glob('/dev/ttyUSB*')
    
    def connectToRobot(self):
        success = self.gado_sys.connect()
        if success:
            tkMessageBox.showinfo("Connection Status", "Successfully connected to Gado!")
        else:
            tkMessageBox.showerror("Connection Status", "Could not connect to Gado, please ensure it is on and plugged into the computer")
        return success
    
    def disconnectFromRobot(self):
        success = self.gado_sys.disconnect()
        if success:
            tkMessageBox.showinfo("Connection Status", "Closed connection to Gado!")
        else:
            tkMessageBox.showerror("Connection Status", "Error closing connection, was it connected?")
    
    def startRobot(self):
        #Function call to start robot's operation
        print "Starting robot..."
        
        #self.gado.lowerAndLiftInternal()
        #self.gado.sendRawActuatorWithoutBlocking(200)
        self.gado_sys.start()
        
    def pauseRobot(self):
        #Function call to pause robot's operation
        print "Pausing robot..."
        self.gado_sys.pause()
    
    def resumeRobot(self):
        self.gado_sys.resume()
    
    def stopRobot(self):
        #Function call to stop robot's operation
        print "Stopping robot..."
        self.gado_sys.stop()
        
    def resetRobot(self):
        #Function call to reset the robot's operations
        print "Restarting robot..."
        self.gado_sys.reset()