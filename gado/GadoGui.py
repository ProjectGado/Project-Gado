import sys
from Tkinter import *
import tkMessageBox

class GadoGui(Frame):
    
    #Widgets
    global locationDropDown
    
    def __init__(self, master=None):
        
        #Initialize the frame
        Frame.__init__(self, master)
        
        #Create all menus for application
        self.createMenus(master)

        #Pack the widgets and create the GUI
        self.pack()
        self.createWidgets()
        
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
        
    def createWidgets(self):
        
        #Create the location section
        self.locationLabel = Label(self)
        self.locationLabel["text"] = "Location: "
        self.locationLabel.grid(row=0, column=0, sticky=W, padx=10, pady=5)
        
    def createFileMenu(self, menubar=None, master=None):
        
        self.fileMenu = Menu(self.menubar, tearoff=0)
        self.fileMenu.add_command(label="Quit", command=master.quit)
        
        return self.fileMenu
    
    def createSettingsMenu(self, menubar=None, master=None):
        
        self.settingsMenu = Menu(self.menubar, tearoff=0)
        self.settingsMenu.add_command(label="Quit", command=master.quit)
        
        return self.settingsMenu