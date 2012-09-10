import sys
from Tkinter import *
import tkMessageBox
import Image, ImageTk
import ttk
import Pmw
import time
import platform
from gado.Robot import Robot
from gado.functions import *
from gado.gui.ManageSets import ManageSets
from gado.gui.ConfigurationWindow import ConfigurationWindow
import gado.messages as messages
from threading import Thread
from Queue import Queue
from gado.gui.Wizard import Wizard
from gado.gui.AdvancedSettings import AdvancedSettings

import datetime

class GuiListener(Thread):
    '''
    Pulls the queue of messages aimed at the GUI
    
    Once it has pulled a message, it determines the appropriate
    action for handling the information.
    '''
    def __init__(self, q, gui_q, gui):
        self.gui_q = gui_q
        self.q = q
        self.gui = gui
        Thread.__init__(self)
    
    def run(self):
        while True:
            msg = fetch_from_queue(self.q)
            print 'GuiListener\tFetched message %s' % str(msg)
            if msg[0] == messages.SET_SCANNER_PICTURE:
                self.gui.changeScannedImage(msg[1])
            elif msg[0] == messages.SET_WEBCAM_PICTURE:
                self.gui.changeWebcamImage(msg[1])
            elif msg[0] == messages.SET_STATUS_TEXT:
                self.gui.changeStatusText(msg[1])
            elif msg[0] == messages.DISPLAY_ERROR:
                add_to_queue(self.gui_q, messages.DISPLAY_ERROR, msg[1])
            elif msg[0] == messages.DISPLAY_INFO:
                add_to_queue(self.gui_q, messages.DISPLAY_INFO, msg[1])
            elif msg[0] == messages.GUI_ABANDON_SHIP:
                self.gui.root.destroy()
                sys.exit()
            elif msg[0] == messages.GUI_LISTENER_DIE:
                return
            else:
                add_to_queue(self.q, msg[0], (msg[1] if len(msg) > 1 else None))

class GadoGui(Frame):
    '''
    This is the primary GUI class
    '''
    
    def __init__(self, q_in, q_out):
        # Load in the system-to-gui queue and the gui-to-system queue
        self.q_in = q_in
        self.q_out = q_out
        
        #Start the Gui's personal queue
        self.gui_q = Queue()
        self.t1 = GuiListener(q_in, self.gui_q, self)
        
        #Instantiate the root frame of the Gui
        self.root = Tk()
        
        #Set the title
        self.root.title("Gado Control Software")
        
        #Whenever the red x on the window is clicked, destroy the entire Gui
        self.root.protocol('WM_DELETE_WINDOW', self.destroy)
        
        #Initialize the master frame
        Frame.__init__(self, self.root)
    
    def load(self):
        '''
        Loads in all elements of the Gui
        
        This includes all windows, menus and widgets
        '''
        
        #Load up all possible windows
        self.manage_sets = ManageSets(self.root, self.q_in, self.q_out, self.gui_q)
        self.selected_set = None
        self.config_window = ConfigurationWindow(self.root, self.q_in, self.q_out, self.gui_q)
        self.wizard = Wizard(self.root, self.q_in, self.q_out, self.gui_q)
        self.advanced_settings = AdvancedSettings(self.root, self.q_in, self.q_out, self.gui_q)
        
        #Create all menus for application
        self._createMenus(self.root)
        
        #Pack the widgets and create the GUI
        self.pack()
        self.createWidgets()
        
        msg = fetch_from_queue(self.q_in)
        self.tkloop()
        
        #Start up the Gui Listener
        self.t1.start()
        
        #Set the root's icon for the title bar
        self.root.wm_iconbitmap("resources/gado.ico")
        
        #Start up the main Gui loop
        self.root.mainloop()
        
    #################################################################################
    #####                           MENU FUNCTIONS                              #####
    #################################################################################
    
    def _createMenus(self, master=None):
        '''
        Creates all of the menus in the application in addition to
        all of the entries within those menus
        '''
        
        #Create the drop down menu
        self.menubar = Menu(master)
        
        #Create the file menu
        self.fileMenu = self._createFileMenu(self.menubar, master)
        
        #Create the Settings menu
        self.settingsMenu = self._createSettingsMenu(self.menubar, master)
        
        #Add both menus to the menubar
        self.menubar.add_cascade(label="File", menu=self.fileMenu)
        self.menubar.add_cascade(label="Settings", menu=self.settingsMenu)
        
        #Assign menubar
        master.config(menu=self.menubar)
    
    def changeStatusText(self, text):
        '''
        Changes the status text box's current text
        '''
        
        self.messageEntry.config(state=NORMAL)
        self.messageEntry.delete(0, 'end')
        self.messageEntry.insert('end', text)
        self.messageEntry.config(state=DISABLED)
    
    def _createFileMenu(self, menubar=None, master=None):
        '''
        Creating the file menu and it's individual entries
        '''
        
        self.fileMenu = Menu(self.menubar, tearoff=0)
        self.fileMenu.add_command(label="Quit", command=self.destroy)
        
        return self.fileMenu
    
    def _createSettingsMenu(self, menubar=None, master=None):
        '''
        Create the settings menu and it's individual entries
        '''
        
        self.settingsMenu = Menu(self.menubar, tearoff=0)
        self.settingsMenu.add_command(label="Configure Layout", command=self.show_configuration_window)
        self.settingsMenu.add_command(label="Launch Wizard", command=self.show_wizard)
        self.settingsMenu.add_command(label="Advanced Settings", command = self.advanced_settings.show)
        
        return self.settingsMenu
   
    def show_advanced_settings(self):
        '''
        Bring the advanced settings menu to the front of the Gui
        '''
        
        self.advanced_settings.show()
   
    def tkloop(self):
        '''
        Loop for internal Gui actions
        '''
        
        try:
            while True:
                msg = self.gui_q.get_nowait()
                print 'GadoGui\tmsg:', msg
                
                if msg[0] == messages.DISPLAY_ERROR:
                    tkMessageBox.showerror("Error", msg[1])
                elif msg[0] == messages.DISPLAY_INFO:
                    tkMessageBox.showinfo("Info", msg[1])
                elif msg[0] == messages.LAUNCH_WIZARD:
                    add_to_queue(self.q_in, messages.GUI_LISTENER_DIE)
                    self.wizard.load()
                elif msg[0] == messages.RELAUNCH_LISTENER:
                    self.t1 = GuiListener(self.q_in, self.gui_q, self)
                    self.t1.start()
                elif msg[0] == messages.SET_WEBCAM_PICTURE:
                    self.changeWebcamImage(msg[1])
                elif msg[0] == messages.SET_SCANNER_PICTURE:
                    self.changeScannedImage(msg[1])
                elif msg[0] == messages.REFRESH:
                    self._refresh()
        except:
            pass
        
        self.root.after(100, self.tkloop)
        
    #################################################################################
    #####                           WIDGET FUNCTIONS                            #####
    #################################################################################
    
    def createWidgets(self):
        
        #Create the artifactSet section
        self._createArtifactSetWidgets()
        
        #Create the Control section
        self._createControlWidgets()
        
        #Create the status center
        self._createStatusWidgets()
        
        #Create the image display widgets
        self._createImageDisplayWidgets()
    
    def _createArtifactSetWidgets(self):
        #Create label
        artifactSetLabel = Label(self)
        artifactSetLabel["text"] = "Artifact Set: "
        artifactSetLabel.grid(row=0, column=0, sticky=W, padx=10, pady=5, columnspan=2)
        
        #Create dropdown for selecting an artifact set
        set_dropdown = Pmw.ComboBox(self, selectioncommand=self.set_selected_set)
        set_dropdown.grid(row=1, column=0, sticky=N+S+E+W, padx=10, pady=5, columnspan=1)
        self.set_dropdown = set_dropdown
        self._populate_set_dropdown()
        
        # Add the button to create a new artifact set
        new_set_button = Button(self)
        new_set_button["text"] = "New Artifact Set"
        new_set_button["command"] = self.show_manage_sets
        new_set_button.grid(row=1, column=1, sticky=N+S+E+W, padx=10, pady=5, columnspan=1)
    
    def show_manage_sets(self):
        add_to_queue(self.q_in, messages.GUI_LISTENER_DIE)
        self.manage_sets.show()
    
    def show_configuration_window(self):
        add_to_queue(self.q_in, messages.GUI_LISTENER_DIE)
        self.config_window.show()
        
    def show_wizard(self):
        add_to_queue(self.q_in, messages.GUI_LISTENER_DIE)
        self.wizard.load()
    
    def set_selected_set(self, a):
        idx = self.set_dropdown.curselection()[0]
        self.selected_set = self.weighted_sets[int(idx)][0]
        if not self.selected_set:
            tkMessageBox.showerror("Invalid Set Selection", "Please select a valid set, or create a new one.")
        else:
            add_to_queue(self.q_out, messages.SET_SELECTED_ARTIFACT_SET, self.selected_set)
    
    def _createControlWidgets(self):
        #Create label
        self.controlLabel = Label(self)
        self.controlLabel["text"] = "Control: "
        self.controlLabel.grid(row=0, column=2, sticky=W, padx=10, pady=5)
        
        #Create start/stop/pause/restart buttons
        self.startButton = Button(self)
        self.startButton["text"] = "Start"
        self.startButton["command"] = self.startRobot
        self.startButton.grid(row=1, column=2, sticky=N+S+E+W, padx=10, pady=5)
        
        self.pauseButton = Button(self)
        self.pauseButton["text"] = "Pause"
        self.pauseButton["command"] = self.pauseRobot
        self.pauseButton.grid(row=1, column=3, sticky=N+S+E+W, padx=10, pady=5)
        
        self.stopButton = Button(self)
        self.stopButton["text"] = "Stop"
        self.stopButton["command"] = self.stopRobot
        self.stopButton.grid(row=1, column=4, sticky=N+S+E+W, padx=10, pady=5)
        
        self.resetButton = Button(self)
        self.resetButton["text"] = "Reset"
        self.resetButton["command"] = self.resetRobot
        self.resetButton.grid(row=1, column=5, sticky=N+S+E+W, padx=10, pady=5)
        
    def _createStatusWidgets(self):
        #Create label
        self.statusLabel = Label(self)
        self.statusLabel["text"] = "Status: "
        self.statusLabel.grid(row=4, column=0, sticky=W, padx=10, pady=5)
        
        #Actual message box
        self.messageEntry = Entry(self)
        self.messageEntry.grid(row=5, column=0, columnspan=6, sticky=N+S+E+W, padx=10, pady=5)
        
    def _createImageDisplayWidgets(self):
        '''
        These widgets display both the scanned and photographed images captured
        by the Gado system
        '''
        
        #Scanner label
        self.scannerLabel = Label(self)
        self.scannerLabel["text"] = "Scanner Image:"
        self.scannerLabel.grid(row=2, column=0, sticky=W, padx=10, pady=5)
        
        #Webcam Label
        self.webCamLabel = Label(self)
        self.webCamLabel["text"] = "Webcam Image:"
        self.webCamLabel.grid(row=2, column=2, sticky=W, padx=10, pady=5)
        
        #Open up the default image as a placeholder for the scanned/photographed images
        image = Image.open("resources/test.jpg")
        image.thumbnail((500, 500), Image.ANTIALIAS)
        
        image2 = Image.open("resources/test.jpg")
        image2.thumbnail((500,500), Image.ANTIALIAS)
        
        #Set to the default
        self.frontImage = ImageTk.PhotoImage(image)
        self.backImage = ImageTk.PhotoImage(image2)
        
        #Embed photos and display in Gui
        self.frontImageLabel = Label(self, image=self.frontImage)
        self.frontImageLabel.photo = self.frontImage
        self.frontImageLabel.grid(row=3, column=0, sticky=N+S+E+W, padx=10, pady=5, columnspan=2)
        
        self.backImageLabel = Label(self, image=self.backImage)
        self.backImageLabel.photo = self.backImage
        self.backImageLabel.grid(row=3, column=2, sticky=N+S+E+W, padx=10, pady=5, columnspan=4)
    
    def destroy(self):
        '''
        Kills the GUI dead. This method must be called.
        '''
        add_to_queue(self.q_out, messages.MAIN_ABANDON_SHIP)
        add_to_queue(self.q_in, messages.GUI_LISTENER_DIE)
        sys.exit()
        
    #################################################################################
    #####                           FUNCTION WRAPPERS                           #####
    #################################################################################
    
    def _refresh(self):
        #Delete allentries in the artifact set list
        self.set_dropdown.delete(0, 'end')
        
        #Repopulate that list with the most current entries
        self._populate_set_dropdown()
    
    def _populate_set_dropdown(self):
        '''
        Populates the artifact set dropdown with the most current list of artifact sets
        '''
        
        add_to_queue(self.q_out, messages.WEIGHTED_ARTIFACT_SET_LIST)
        msg = fetch_from_queue(self.q_in, messages.WEIGHTED_ARTIFACT_SET_LIST)
        self.weighted_sets = msg[1]
        for id, indented_name in self.weighted_sets:
            self.set_dropdown.insert('end', indented_name)
    
    def startRobot(self):
        # Function call to start robot's operation
        add_to_queue(self.q_out, messages.START)
        
    def pauseRobot(self):
        # Function call to pause robot's operation
        add_to_queue(self.q_out, messages.LAST_ARTIFACT)
    
    def stopRobot(self):
        #Function call to stop robot's operation
        add_to_queue(self.q_out, messages.STOP)
        
    def resetRobot(self):
        #Function call to reset the robot's operations
        add_to_queue(self.q_out, messages.RESET)
        
    #Image transferring functions
    
    def changeScannedImage(self, imagePath):
        #Open image from passed path and resize it (preserving ratio) to fit in GUI
        try:
            image = Image.open(imagePath)
            image.thumbnail((500, 500), Image.ANTIALIAS)
            
            self.frontImage = ImageTk.PhotoImage(image)
            
            self.frontImageLabel = Label(self, image=self.frontImage)
            self.frontImageLabel.photo = self.frontImage
            self.frontImageLabel.grid(row=3, column=0, sticky=N+S+E+W, padx=10, pady=5, columnspan=2)
            
        except:
            print "Error updating scanner image in gui thread..."
        
    def changeWebcamImage(self, imagePath):
        try:
            image = Image.open(imagePath)
            image.thumbnail((500,500), Image.ANTIALIAS)
            
            self.backImage = ImageTk.PhotoImage(image)
            
            self.backImageLabel = Label(self, image=self.backImage)
            self.backImageLabel.photo = self.backImage
            self.backImageLabel.grid(row=3, column=2, sticky=N+S+E+W, padx=10, pady=5, columnspan=2)
        except:
            print "Error updating webcam image in gui thread..."