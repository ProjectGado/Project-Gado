from Tkinter import *
import ttk
import tkFont
from gado.functions import *
import time

#Constants
WINDOW_HEIGHT = 300
WINDOW_WIDTH = 450

TEXT_HEIGHT = 10
TEXT_WIDTH = 50

#Globals
_lastTime = 0
currentFrame = None
configuringArm = False
firstConf = True

#vars for enabling changing of state in GUI
welcomeDone = False
scannerDone = False
webcamDone = False
locationDone = False
pickupDone = False

#Next buttons so we can globally control their state
welcomeNextButton = None
reqNextButton = None
scannerNextButton = None
webcamNextButton = None
locationNextButton = None
pickupNextButton = None

#variables that will get pushed into the conf file when all is said and done
settings = {'arm_home_value' : 0, 'arm_in_value' : 0, 'arm_out_value' : 0, 'baudrate' : 115200\
            ,'scan_dpi' : 600, 'scanner_name' : None, 'actuator_home_value' : 0,\
            'actuator_up_value' : 25, 'handshake' : 'Im a robot!', 'db_dicitonary' : 'databases'\
            ,'db_filename' : 'db.sqlite', 'image_path' : "images"}


##############################################################################
###                             WIDGET FUNCTIONS                           ###
##############################################################################

def createWelcomeWidgets():
    global welcomeNextButton
    
    welcomeLabel = Label(welcomeFrame, text = 'Welcome to the Gado Configuration Wizard!', font = labelFont)
    welcomeLabel.grid(column = 0, row = 0, padx = 10, pady = 5, sticky = N+S+E+W, columnspan = 2)
    
    #Text
    welcomeText = Text(welcomeFrame, height = TEXT_HEIGHT, width = TEXT_WIDTH, wrap = WORD, font = textFont)
    welcomeText.insert(END, "\n\nWe're going to try and connect the robot to your computer.\n\nPlease make sure it is plugged in...")
    
    welcomeText.config(state=DISABLED)
    welcomeText.grid(column = 0, row = 1, columnspan = 2, padx = 10, pady = 20, sticky = N+S+E+W)
    
    #Nav buttons
    connectButton = Button(welcomeFrame, text = "Connect", command = connectToGado)
    connectButton.grid(column = 0, row = 2, padx = 10, pady = 5, sticky = N+S+E+W)
    
    welcomeNextButton = Button(welcomeFrame, text = "Next", command = callRequirementsFrame)
    welcomeNextButton.config(state=DISABLED)
    
    welcomeNextButton.grid(column = 1, row = 2, padx = 10, pady = 5, sticky = N+S+E+W)

def createRequirementsWidgets():
    reqLabel = Label(requirementsFrame, text = 'Setup Requirements', font = labelFont)
    reqLabel.grid(column = 0, row = 0, padx = 10, pady = 5, sticky = N+S+E+W, columnspan = 2)
    
    #Text
    reqText = Text(requirementsFrame, height = TEXT_HEIGHT, width = TEXT_WIDTH, wrap = WORD, font = textFont)
    reqText.insert(END, "In order to proceed with the setup you will need to make sure that you have:\n\
                   \n\t1. The piece of paper containing the QR code (tells the robot to stop)\
                   \n\t2. A sample of the typical kind of artifact you will be scanning\
                   \n\t3. All pieces of equipment that came with the robot\
                   \n\t4. A Smile :)")
    reqText.config(state=DISABLED)
    reqText.grid(column = 0, row = 1, columnspan = 2, padx = 10, pady = 20, sticky = N+S+E+W)
    
    #Nav Buttons
    reqNextButton = Button(requirementsFrame, text = "Next", command = callScannerFrame)
    reqBackButton = Button(requirementsFrame, text = "Back", command = callWelcomeFrame)
    
    reqNextButton.grid(column = 1, row = 2, padx = 10, pady = 5, sticky = N+S+E+W)
    reqBackButton.grid(column = 0, row = 2, padx = 10, pady = 5, sticky = N+S+E+W)

def createScannerWidgets():
    global scannerNextButton
    
    scannerLabel = Label(scannerFrame, text = 'Locate Scanner', font = labelFont)
    scannerLabel.grid(column = 0, row = 0, padx = 10, pady = 5, sticky = N+S+E+W, columnspan = 2)
    
    #Text
    scannerText = Text(scannerFrame, height = TEXT_HEIGHT - 2, width = TEXT_WIDTH, wrap = WORD, font = textFont)
    scannerText.insert(END, "\n\nWe're going to try to figure out which scanner to use\
                       \n\nMake sure that your scanner is connected to your computer and that all necessary drivers are installed")
    scannerText.config(state=DISABLED)
    scannerText.grid(column = 0, row = 1, columnspan = 2, padx = 10, pady = 20, sticky = N+S+E+W)
    
    #Nav Buttons
    testScanButton = Button(scannerFrame, text = "Locate Scanner", command = locateScanner)
    testScanButton.grid(column = 0, row = 2, padx = 10, pady = 5, sticky = N+S+E+W)
    
    scannerNextButton = Button(scannerFrame, text = "Next", command = callWebcamFrame)
    scannerBackButton = Button(scannerFrame, text = "Back", command = callRequirementsFrame)
    
    scannerNextButton.config(state=DISABLED)
    
    scannerNextButton.grid(column = 1, row = 3, padx = 10, pady = 5, sticky = N+S+E+W)
    scannerBackButton.grid(column = 0, row = 3, padx = 10, pady = 5, sticky = N+S+E+W)
    
def createWebcamWidgets():
    global webcamNextButton
    
    webcamLabel = Label(webcamFrame, text = 'Webcam stuff', font = labelFont)
    webcamLabel.grid(column = 0, row = 0, padx = 10, pady = 5, sticky = N+S+E+W, columnspan = 2)
    
    #Text
    webcamText = Text(webcamFrame, height = TEXT_HEIGHT - 2, width = TEXT_WIDTH, wrap = WORD, font = textFont)
    webcamText.insert(END, "\n\nGoing to attempt to discover and connect to the webcam.\n\nWe'll then capture an image from the webcam to make sure it is working properly")
    webcamText.config(state=DISABLED)
    webcamText.grid(column = 0, row = 1, columnspan = 2, padx = 10, pady = 20, sticky = N+S+E+W)
    
    #Nav Buttons
    testWebcamButton = Button(webcamFrame, text = "Locate Webcam", command = locateWebcam)
    testWebcamButton.grid(column = 0, row = 2, padx = 10, pady = 5, sticky = N+S+E+W)
    
    webcamNextButton = Button(webcamFrame, text = "Next", command = callLocationFrame)
    webcamBackButton = Button(webcamFrame, text = "Back", command = callScannerFrame)
    
    webcamNextButton.config(state=DISABLED)
    
    webcamNextButton.grid(column = 1, row = 3, padx = 10, pady = 5, sticky = N+S+E+W)
    webcamBackButton.grid(column = 0, row = 3, padx = 10, pady = 5, sticky = N+S+E+W)
    
def createLocationWidgets():
    global locationNextButton
    
    locationLabel = Label(locationFrame, text = 'Layout Location Configuration', font = labelFont)
    locationLabel.grid(column = 0, row = 0, padx = 10, pady = 5, sticky = N+S+E+W, columnspan = 2)
    
    #Text
    locationText = Text(locationFrame, height = TEXT_HEIGHT, width = TEXT_WIDTH, wrap = WORD, font = textFont)
    locationText.insert(END, "The next four prompts will allow you to set up the layout of your Gado")
    locationText.config(state=DISABLED)
    locationText.grid(column = 0, row = 1, padx = 10, pady = 20, sticky = N+S+E+W, columnspan = 2)
    
    #We need to bind the frame for any keypress events (for the layout configuration steps)
    root.bind("<Key>", _keyboard_callback)
    
    global _lastTime
    _lastTime = 0
    
    #Nav Buttons
    
    #Unlike the other next buttons, this button changes the contents of this frame for each
    #step of the location configuration. After the final layout parameters have been set,
    #then this button will link to the next Frame
    locationNextButton = Button(locationFrame, text = "Next", command = lambda: startLocationSetup(locationText, locationNextButton, locationBackButton))
    locationBackButton = Button(locationFrame, text = "Back", command = callWebcamFrame)
    
    locationNextButton.grid(column = 1, row = 2, padx = 10, pady = 5, sticky = N+S+E+W)
    locationBackButton.grid(column = 0, row = 2, padx = 10, pady = 5, sticky = N+S+E+W)
    
def createPickUpWidgets():
    global pickupNextButton
    
    pickupLabel = Label(pickUpFrame, text = 'Test document pick up', font = labelFont)
    pickupLabel.grid(column = 0, row = 0, padx = 10, pady = 5, sticky = N+S+E+W, columnspan = 2)
    
    #Text
    pickupText = Text(pickUpFrame, height = TEXT_HEIGHT - 2, width = TEXT_WIDTH, wrap = WORD, font = textFont)
    pickupText.insert(END, "\n\nAttempting to pickup an object.\n\nPlease place your test document in the in-pile")
    pickupText.config(state=DISABLED)
    pickupText.grid(column = 0, row = 1, padx = 10, pady = 20, sticky = N+S+E+W, columnspan = 2)
    
    #Nav Buttons
    testPickupButton = Button(pickUpFrame, text = "Pick up Document", command = testPickUp)
    testPickupButton.grid(column = 0, row = 2, padx = 10, pady = 5, sticky = N+S+E+W)
    
    pickupNextButton = Button(pickUpFrame, text = "Next", command = callDoneFrame)
    pickupBackButton = Button(pickUpFrame, text = "Back", command = callLocationFrame)
    
    pickupNextButton.config(state=DISABLED)
    
    pickupNextButton.grid(column = 1, row = 3, padx = 10, pady = 5, sticky = N+S+E+W)
    pickupBackButton.grid(column = 0, row = 3, padx = 10, pady = 5, sticky = N+S+E+W)
    
'''    
def createScanTestWidgets():
    scanTestLabel = Label(scannerTestFrame, text = 'Test Scanner', font = labelFont)
    scanTestLabel.grid(column = 0, row = 0, padx = 10, pady = 5, sticky = N+S+E+W)
    
    #Nav Buttons
    scanTestNextButton = Button(scannerTestFrame, text = "Next", command = callDoneFrame)
    scanTestBackButton = Button(scannerTestFrame, text = "Back", command = callPickupFrame)
    
    scanTestNextButton.grid(column = 1, row = 1, padx = 10, pady = 5, sticky = N+S+E+W)
    scanTestBackButton.grid(column = 0, row = 1, padx = 10, pady = 5, sticky = N+S+E+W)
'''

def createDoneWidgets():
    doneLabel = Label(doneFrame, text = 'Finished!', font = labelFont)
    doneLabel.grid(column = 0, row = 0, padx = 10, pady = 5, sticky = N+S+E+W, columnspan = 2)
    
    #Text
    doneText = Text(doneFrame, height = TEXT_HEIGHT, width = TEXT_WIDTH, wrap = WORD, font = textFont)
    doneText.insert(END, "\n\nCongratulations! You have successfully configured the Gado!\n\nIn the future, if you would like to change the configuration, run this wizard again.")
    doneText.config(state=DISABLED)
    doneText.grid(column = 0, row = 1, columnspan = 2, padx = 10, pady = 20, sticky = N+S+E+W)
    
    #Nav Buttons
    doneQuitButton = Button(doneFrame, text = "Done", command = quitWizard)
    doneBackButton = Button(doneFrame, text = "Back", command = callPickupFrame)
    
    doneQuitButton.grid(column = 1, row = 2, padx = 10, pady = 5, sticky = N+S+E+W)
    doneBackButton.grid(column = 0, row = 2, padx = 10, pady = 5, sticky = N+S+E+W)
    
###############################################################################
###                             TRANSITION FUNCTIONS                        ###
###############################################################################

#These functions facilitate the movement between different frames of the wizard

def callWelcomeFrame():
    bringToFront(welcomeFrame)
    
def callRequirementsFrame():
    bringToFront(requirementsFrame)
    
def callScannerFrame():
    bringToFront(scannerFrame)
    
def callWebcamFrame():
    bringToFront(webcamFrame)
    
def callLocationFrame():
    bringToFront(locationFrame)
    
    
def callPickupFrame():
    bringToFront(pickUpFrame)
    
'''
def callScanTestFrame():
    bringToFront(scannerTestFrame)
    
'''   
    
def callDoneFrame():
    bringToFront(doneFrame)
    
#Forget all frames except for the passed in frame
def bringToFront(frame):
    global settings
    
    for f in frameList:
    #Hide all frames but the one that was passed in
        if f is not frame:
            #Forget this frame
            f.grid_forget()
            
    #Bring the passed in frame to the front
    frame.grid(column = 0, row = 0, padx = 10, pady = 5, sticky = N+S+E+W)
    
    #Make this the current frame
    global currentFrame
    currentFrame = frame
    
    #Push settings to conf file
    export_settings(**settings)
    
def quitWizard():
    root.destroy()
    
##############################################################################
###                             LOCATION SETUP FUNCTIONS                   ###
##############################################################################

#Initial function that starts off the layout config cascade
def startLocationSetup(locationText, nextButton, backButton):
    global firstConf
    firstConf = False
    
    #Clear the locationText widget
    locationText.delete(1.0, END)
    
    #Set the location frame as current frame
    global currentFrame
    currentFrame = locationFrame
    
    #Move to first step in layout configuration
    _defineArmInPile(locationText, nextButton, backButton)

def _configuringArm():
    global configuringArm
    return configuringArm

def _keyboard_callback(event):
    
    if currentFrame is locationFrame and firstConf is False:
        global _lastTime
        
        # Delay between robot commands for consistent behavior
        t = time.time()
        
        if t - _lastTime > 0.1:
            key = event.keycode
            if _configuringArm():
                if key == 37:
                    #Left arrow press
                    print "Arm move left"
                
                elif key == 39:
                    #Right arrow press
                    print "Arm move right"
            else:
                if key == 38:
                    #Up arrow press
                    print "Actuator move up"
                elif key == 40:
                    #Down arrow press
                    print "Actuator move down"
            
            _lastTime = t

def _defineArmInPile(locationText, nextButton, backButton):
    locationText.config(state=NORMAL)
    
    #Clear the locationText widget
    locationText.delete(1.0, END)
    
    locationText.insert(END, "\n\nConfigure the In-Pile's Location\n\nUsing the right and left arrow keys, move the arm to the desired location")

    locationText.config(state=DISABLED)

    global configuringArm
    configuringArm = True
    
    #Change the mapping for the next button to the next stage of the layout configuration
    nextButton.configure(command = lambda: _defineArmScanner(locationText, nextButton, backButton))

    #Change the mapping of the back button to the previous stage of the layout configuration
    backButton.configure(command = lambda: callWebcamFrame())
    
def _defineArmScanner(locationText, nextButton, backButton):
    locationText.config(state=NORMAL)
    
    #Clear the locationText widget
    locationText.delete(1.0, END)
    
    locationText.insert(END, "\n\nConfigure the Scanner's Location\n\nUsing the right and left arrow keys, move the arm to the desired location")

    locationText.config(state=DISABLED)
    
    global configuringArm
    configuringArm = True
    
    #Change the mapping for the next button to the next stage of the layout configuration
    nextButton.configure(command = lambda: _defineArmOutPile(locationText, nextButton, backButton))

    #Change the mapping of the back button to the previous stage of the layout configuration
    backButton.configure(command = lambda: _defineArmInPile(locationText, nextButton, backButton))
    
def _defineArmOutPile(locationText, nextButton, backButton):
    locationText.config(state=NORMAL)
    
    #Clear the locationText widget
    locationText.delete(1.0, END)
    
    locationText.insert(END, "\n\nConfigure the Out-Pile's Location\n\nUsing the right and left arrow keys, move the arm to the desired location")

    locationText.config(state=DISABLED)

    global configuringArm
    configuringArm = True

    #Change the mapping for the next button to the next stage of the layout configuration
    nextButton.configure(command = lambda: _defineActuatorDown(locationText, nextButton, backButton))

    #Change the mapping of the back button to the previous stage of the layout configuration
    backButton.configure(command = lambda: _defineArmScanner(locationText, nextButton, backButton))
    
def _defineActuatorDown(locationText, nextButton, backButton):
    locationText.config(state=NORMAL)
    
    #Clear the locationText widget
    locationText.delete(1.0, END)
    
    locationText.insert(END, "\n\nConfigure the height of the Scanner\n\nUsing the up and down arrow keys, move the suction cup to the surface of the Scanner")

    locationText.config(state=DISABLED)
    
    global configuringArm
    configuringArm = False
    
    #Change the mapping for the next button to the next stage of the layout configuration
    nextButton.configure(command = lambda: _defineActuatorUp(locationText, nextButton, backButton))

    #Change the mapping of the back button to the previous stage of the layout configuration
    backButton.configure(command = lambda: _defineArmOutPile(locationText, nextButton, backButton))

def _defineActuatorUp(locationText, nextButton, backButton):
    locationText.config(state=NORMAL)
    
    #Clear the locationText widget
    locationText.delete(1.0, END)
    
    locationText.insert(END, "\n\nConfigure the regular height of the actuator\n\nUsing the up and down arrow keys, move the Actuator to a height which can clear the scanner by at least 1\"")

    locationText.config(state=DISABLED)
    
    global configuringArm
    configuringArm = False
    
    #Change the mapping for the next button to the next stage of the layout configuration
    nextButton.configure(command = lambda: callPickupFrame())
    
    #Change the mapping of the back button to the previous stage of the layout configuration
    backButton.configure(command = lambda: _defineActuatorDown(locationText, nextButton, backButton))
    
##############################################################################
###                             WRAPPER FUNCTIONS                          ###
##############################################################################

def connectToGado():
    #We can move on from the connection frame (Hardcoded to true until we have real connectivity)
    global welcomeDone
    welcomeDone = True
    
    #Change state of next button to enabled
    global welcomeNextButton
    welcomeNextButton.config(state=NORMAL)
    
def locateScanner():
    global scannerDone
    scannerDone = True
    
    global scannerNextButton
    scannerNextButton.config(state=NORMAL)
    
def locateWebcam():
    global webcamDone
    webcamDone = True
    
    global webcamNextButton
    webcamNextButton.config(state=NORMAL)

def testPickUp():
    global pickupDone
    pickupDone = True
    
    global pickupNextButton
    pickupNextButton.config(state=NORMAL)
    
###############################################################################
###                             MAIN PROGRAM                                ###
###############################################################################

#Create the root of the wizard
root = Tk()

#Define our custom fonts
labelFont = tkFont.Font(family = "Helvetica", size = 14)
textFont = tkFont.Font(family="Helvetica", size = 11)

#Set base size requirements
root.minsize(WINDOW_WIDTH, WINDOW_HEIGHT)
root.maxsize(WINDOW_WIDTH, WINDOW_HEIGHT)
root.geometry("%dx%d+0+0" % (WINDOW_WIDTH, WINDOW_HEIGHT))

#List to hold all frame
frameList = []

#Create the welcome frame
welcomeFrame = ttk.Frame(root, width = WINDOW_WIDTH, height = WINDOW_HEIGHT)
welcomeFrame.grid(column = 0, row = 0, padx = 10, pady = 5, sticky = N+S+E+W)
frameList.append(welcomeFrame)

#Create the requirments frame
requirementsFrame = ttk.Frame(root, width = WINDOW_WIDTH, height = WINDOW_HEIGHT)
requirementsFrame.grid(column = 0, row = 0, padx = 10, pady = 5, sticky = N+S+E+W)
frameList.append(requirementsFrame)

#Create the scanner frame
scannerFrame = ttk.Frame(root, width = WINDOW_WIDTH, height = WINDOW_HEIGHT)
scannerFrame.grid(column = 0, row = 0, padx = 10, pady = 5, sticky = N+S+E+W)
frameList.append(scannerFrame)

#Create the webcam frame
webcamFrame = ttk.Frame(root, width = WINDOW_WIDTH, height = WINDOW_HEIGHT)
webcamFrame.grid(column = 0, row = 0, padx = 10, pady = 5, sticky = N+S+E+W)
frameList.append(webcamFrame)

#Create the location frame
locationFrame = ttk.Frame(root, width = WINDOW_WIDTH, height = WINDOW_HEIGHT)
locationFrame.grid(column = 0, row = 0, padx = 10, pady = 5, sticky = N+S+E+W)
frameList.append(locationFrame)

#Create frame to test the actuator's ability to pick up document
pickUpFrame = ttk.Frame(root, width = WINDOW_WIDTH, height = WINDOW_HEIGHT)
pickUpFrame.grid(column = 0, row = 0, padx = 10, pady = 5, sticky = N+S+E+W)
frameList.append(pickUpFrame)

'''
#Create frame to test scanner
scannerTestFrame = ttk.Frame(root, width = WINDOW_WIDTH, height = WINDOW_HEIGHT)
scannerTestFrame.grid(column = 0, row = 0, padx = 10, pady = 5, sticky = N+S+E+W)
frameList.append(scannerTestFrame)
'''

#Finished frame
doneFrame = ttk.Frame(root, width = WINDOW_WIDTH, height = WINDOW_HEIGHT)
doneFrame.grid(column = 0, row = 0, padx = 10, pady = 5, sticky = N+S+E+W)
frameList.append(doneFrame)

#Create all widgets for all frames
createWelcomeWidgets()
createRequirementsWidgets()
createScannerWidgets()
createWebcamWidgets()
createLocationWidgets()
createPickUpWidgets()
#createScanTestWidgets()
createDoneWidgets()

#Forget all frames but the welcome one
bringToFront(welcomeFrame)

'''
#We need to toggle the state of the next button for the welcomeFrame depending on welcomeDone
if welcomeDone:
    welcomeNextButton.config(state=NORMAL)
else:
    welcomeNextButton.config(state=DISABLED)
'''
#Create all gado specific objects/variables
#gado = Robot(None, None, None, None, DEFAULT_BAUD_RATE, None)

#Init the gado system with most vars as none (We don't need them at this point, would just be more overhead)
#gado_sys = GadoSystem(None, gado, root, None)

root.title("Gado Configuration Wizard")

#Start wizard
root.mainloop()