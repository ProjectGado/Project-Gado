from Tkinter import *
import ttk
import tkFont
from gado.functions import *
import time
from threading import Thread
import gado.messages as messages

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

class WizardQueueListener(Thread):
    def __init__(self, q_in, q_out, message, args, callback):
        self.q_in = q_in
        self.q_out = q_out
        self.message = message
        self.args = args
        self.callback = callback
        Thread.__init__(self)
    
    def run(self):
        add_to_queue(self.q_out, self.message, self.args)
        msg = fetch_from_queue(self.q_in)
        self.callback(msg)
        
class WizardLocationListener(Thread):
    def __init__(self, wizard, q_in):
        self.q_in = q_in
        self.wizard = wizard
        Thread.__init__(self)
    
    def run(self):
        while True:
            msg = fetch_from_queue(self.q_in)
            if msg[0] == messages.WIZARD_ABANDON_SHIP:
                return
            elif msg[1] == messages.RETURN:
                self.wizard.registerMovement(msg[1])

IN_PILE = 'Documents to be Scanned Pile'
OUT_PILE = 'Scanned Documents Pile'
SCANNER = 'Scanner'
SCANNER_HEIGHT = 'Scanner Height'

class Wizard():
    def __init__(self, root, q_in, q_out, q_gui):
        self.q_in = q_in # read by wizard
        self.q_out = q_out # goes to gado_sys
        self.q_gui = q_gui # goes to GadoGui
        self.root = root
        
        self._last_time = time.time()
        
        #Define our custom fonts
        labelFont = tkFont.Font(family = "Helvetica", size = 14)
        textFont = tkFont.Font(family="Helvetica", size = 11)
        self.labelFont = labelFont
        self.textFont = textFont
        
        #Set base size requirements
        window = Toplevel(root)
        window.minsize(WINDOW_WIDTH, WINDOW_HEIGHT)
        window.maxsize(WINDOW_WIDTH, WINDOW_HEIGHT)
        window.geometry("%dx%d+0+0" % (WINDOW_WIDTH, WINDOW_HEIGHT))
        self.window = window
        
        #List to hold all frames
        frameList = []
        self.frameList = frameList
        self.frame_idx = 0
        nextButtons = []
        self.nextButtons = nextButtons
        
        self.keyboardCallbacks = dict()
        
        
        frame, next_btn = self._frame_welcome()
        frameList.append(frame)
        nextButtons.append(next_btn)
        '''
        
        frame, next_btn = self._frame_requirements()
        frameList.append(frame)
        nextButtons.append(next_btn)
        
        frame, next_btn = self._frame_peripheral('scanner')
        frameList.append(frame)
        nextButtons.append(next_btn)
        frame, next_btn = self._frame_peripheral('webcam')
        frameList.append(frame)
        nextButtons.append(next_btn)
        '''
        
        frame, next_btn = self._frame_location(IN_PILE)
        frameList.append(frame)
        nextButtons.append(next_btn)
        self.keyboardCallbacks[len(frameList) - 1] = 'arm_in_value'
        
        '''
        frame, next_btn = self._frame_location(SCANNER)
        frameList.append(frame)
        nextButtons.append(next_btn)
        self.keyboardCallbacks[len(frameList) - 1] = 'arm_home_value'
        
        frame, next_btn = self._frame_location(SCANNER_HEIGHT)
        frameList.append(frame)
        nextButtons.append(next_btn)
        self.keyboardCallbacks[len(frameList) - 1] = 'actuator_home_value'
        
        frame, next_btn = self._frame_location(OUT_PILE)
        frameList.append(frame)
        nextButtons.append(next_btn)
        self.keyboardCallbacks[len(frameList) - 1] = 'arm_out_value'
        
        '''
        frame, next_btn = self._frame_done()
        frameList.append(frame)
        nextButtons.append(next_btn)
        
        self.currentFrame = frame
        self.frame_idx = -1
        self.locationThread = None
        #self.nextFrame()
        
        window.protocol("WM_DELETE_WINDOW", self.window.withdraw)
        window.withdraw()
        
        '''
        welcomeFrame = ttk.Frame(window, width = WINDOW_WIDTH, height = WINDOW_HEIGHT)
        welcomeFrame.grid(column = 0, row = 0, padx = 10, pady = 5, sticky = N+S+E+W)
        frameList.append(welcomeFrame)
        self.welcomeFrame = welcomeFrame
        
        
        #Create the requirments frame
        requirementsFrame = ttk.Frame(window, width = WINDOW_WIDTH, height = WINDOW_HEIGHT)
        requirementsFrame.grid(column = 0, row = 0, padx = 10, pady = 5, sticky = N+S+E+W)
        frameList.append(requirementsFrame)
        self.requirementsFrame = requirementsFrame
        
        #Create the scanner frame
        scannerFrame = ttk.Frame(window, width = WINDOW_WIDTH, height = WINDOW_HEIGHT)
        scannerFrame.grid(column = 0, row = 0, padx = 10, pady = 5, sticky = N+S+E+W)
        frameList.append(scannerFrame)
        self.scannerFrame = scannerFrame
        
        #Create the webcam frame
        webcamFrame = ttk.Frame(window, width = WINDOW_WIDTH, height = WINDOW_HEIGHT)
        webcamFrame.grid(column = 0, row = 0, padx = 10, pady = 5, sticky = N+S+E+W)
        frameList.append(webcamFrame)
        self.webcamFrame = webcamFrame
        
        #Create the location frame
        locationFrame = ttk.Frame(window, width = WINDOW_WIDTH, height = WINDOW_HEIGHT)
        locationFrame.grid(column = 0, row = 0, padx = 10, pady = 5, sticky = N+S+E+W)
        frameList.append(locationFrame)
        self.locationFrame = locationFrame
        
        #Create frame to test the actuator's ability to pick up document
        pickUpFrame = ttk.Frame(window, width = WINDOW_WIDTH, height = WINDOW_HEIGHT)
        pickUpFrame.grid(column = 0, row = 0, padx = 10, pady = 5, sticky = N+S+E+W)
        frameList.append(pickUpFrame)
        self.pickUpFrame = pickUpFrame
        
        '''
        #Create frame to test scanner
        #scannerTestFrame = ttk.Frame(root, width = WINDOW_WIDTH, height = WINDOW_HEIGHT)
        #scannerTestFrame.grid(column = 0, row = 0, padx = 10, pady = 5, sticky = N+S+E+W)
        #frameList.append(scannerTestFrame)
        '''
        
        #Finished frame
        doneFrame = ttk.Frame(window, width = WINDOW_WIDTH, height = WINDOW_HEIGHT)
        doneFrame.grid(column = 0, row = 0, padx = 10, pady = 5, sticky = N+S+E+W)
        frameList.append(doneFrame)
        self.doneFrame = doneFrame
        
        #Create all widgets for all frames
        self.createWelcomeWidgets()
        self.createRequirementsWidgets()
        self.createScannerWidgets()
        self.createWebcamWidgets()
        self.createLocationWidgets()
        self.createPickUpWidgets()
        #createScanTestWidgets()
        self.createDoneWidgets()
        
        #Forget all frames but the welcome one
        self.bringToFront(welcomeFrame)
        
        
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
        
        #window.title("Gado Configuration Wizard")
        
        #Start wizard
        #window.mainloop()
    
    def load(self):
        for frame in self.frameList:
            frame.grid_forget()
        self.frameList[0].grid(column = 0, row = 0, padx = 10, pady = 5, sticky = N+S+E+W)
        self.currentFrame = self.frameList[0]
        self.frame_idx = 0
        self.window.deiconify()
        #self.root.mainloop()
    
    ##############################################################################
    ###                             WIDGET FUNCTIONS                           ###
    ##############################################################################
    
    def emptyFrame(self, label_text, main_text):
        frame = ttk.Frame(self.window, width = WINDOW_WIDTH, height = WINDOW_HEIGHT)
        frame.grid(column=0, row=0, padx=10, pady=5, sticky=N+S+E+W)
        
        label = Label(frame, text=label_text, font=self.labelFont)
        label.grid(column=0, row=0, padx=10, pady=5, sticky=N+S+E+W, columnspan=2)
        
        text = Text(frame, height=TEXT_HEIGHT, width=TEXT_WIDTH, wrap=WORD, font=self.textFont)
        text.insert(END, main_text)
        text.config(state=DISABLED)
        text.grid(column=0, row=1, columnspan=2, padx=10, pady=20,sticky=N+S+E+W)
        
        return frame
    
    def nextButton(self, frame):
        button = Button(frame, text = "Next", command = self.nextFrame)
        return button
    
    def prevButton(self, frame):
        button = Button(frame, text = "Previous", command = self.prevFrame)
        return button
    
    def _frame_welcome(self):
        label = 'Welcome to the Gado Configuration Wizard!'
        text = '\n\nWe\'re going to try and connect the robot to your computer.\n\nPlease make sure it is plugged in...'
        frame = self.emptyFrame(label, text)
        
        #Nav buttons
        connect = Button(frame, text = "Connect", command = self.connectToGado)
        connect.grid(column = 0, row = 2, padx = 10, pady = 5, sticky = N+S+E+W)
        
        next_btn = self.nextButton(frame)
        next_btn.config(state=DISABLED)
        next_btn.grid(column = 1, row = 2, padx = 10, pady = 5, sticky = N+S+E+W)
        
        return (frame, next_btn)
    
    def _frame_requirements(self):
        label = 'Setup Requirements'
        text = "In order to proceed with the setup you will need to make sure that you have:\n\
                       \n\t1. The piece of paper containing the QR code (tells the robot to stop)\
                       \n\t2. A sample of the typical kind of artifact you will be scanning\
                       \n\t3. All pieces of equipment that came with the robot\
                       \n\t4. A Smile :)"
        frame = self.emptyFrame(label, text)
        
        #Nav Buttons
        reqNextButton = self.nextButton(frame)
        reqBackButton = self.prevButton(frame)
        
        reqNextButton.grid(column = 1, row = 2, padx = 10, pady = 5, sticky = N+S+E+W)
        reqBackButton.grid(column = 0, row = 2, padx = 10, pady = 5, sticky = N+S+E+W)
        
        return (frame, reqNextButton)
    
    def _frame_peripheral(self, p_type):
        # Two peripherals, webcam and scanner
        text = "\n\nWe're going to try to figure out which %s to use\
                \n\nMake sure that your %s is connected to your computer and that all necessary drivers are installed" % (p_type.lower(), p_type.lower())
        label = 'Connect to %s' % p_type.capitalize()
        frame = self.emptyFrame(label, text)
        
        if 'scanner' in p_type.lower():
            funct = self.connectToScanner
        elif 'webcam' in p_type.lower():
            funct = self.connectToWebcam
        
        connect = Button(frame, text = "Locate %s" % (p_type.capitalize()),
                         command = funct)
        connect.grid(column = 0, row = 2, padx = 10, pady = 5, sticky = N+S+E+W)
        
        nextButton = self.nextButton(frame)
        prevButton = self.prevButton(frame)
        
        nextButton.config(state=DISABLED)
        
        nextButton.grid(column = 1, row = 3, padx = 10, pady = 5, sticky = N+S+E+W)
        prevButton.grid(column = 0, row = 3, padx = 10, pady = 5, sticky = N+S+E+W)
        
        return (frame, nextButton)
    
    def _frame_location(self, location):
        label = 'Configure the Robot'
        if location == SCANNER_HEIGHT:
            text = '\n\nUsing the up and down arrow keys, please place the suction cup on the scanner. We recommend placing a piece of paper on top of the scanner as you lower the suction cup.'
        else:
            text = '\n\nUsing the right and left arrow keys, please move the robot\'s arm over the %s' % location
        frame = self.emptyFrame(label, text)
        
        self.window.bind("<Key>", self._keyboard_callback)
        
        nextButton = self.nextButton(frame)
        prevButton = self.prevButton(frame)
        nextButton.grid(column = 1, row = 3, padx = 10, pady = 5, sticky = N+S+E+W)
        prevButton.grid(column = 0, row = 3, padx = 10, pady = 5, sticky = N+S+E+W)
        
        return (frame, nextButton)
    
    def _frame_done(self):
        label = 'Finished!'
        text = "\n\nCongratulations! You have successfully configured the Gado!\n\nIn the future, if you would like to change the configuration, run this wizard again."
        frame = self.emptyFrame(label, text)
        
        doneQuitButton = Button(frame, text = "Done", command = self.nextFrame)
        doneBackButton = self.prevButton(frame)
        
        doneQuitButton.grid(column = 1, row = 2, padx = 10, pady = 5, sticky = N+S+E+W)
        doneBackButton.grid(column = 0, row = 2, padx = 10, pady = 5, sticky = N+S+E+W)
        
        return (frame, doneQuitButton)
    
    def nextFrame(self):
        print 'Wizard\tnextFrame() called'
        if self.locationThread:
            print 'Wizard\tnextFrame() killing locationThread'
            add_to_queue(self.q_in, messages.WIZARD_ABANDON_SHIP)
            self.locationThread = None
        print 'Wizard\tnextFrame() forgetting current frame'
        self.currentFrame.grid_forget()
        self.frame_idx += 1
        print 'Wizard\tnextFrame() next index: %s' % self.frame_idx
        if self.frame_idx >= len(self.frameList):
            print 'Wizard\tnextFrame() END OF THE ROAD'
            # We're done with all the frames
            self.window.destroy()
            return
        print 'Wizard\tnextFrame() is this a keyboard callback?'
        if self.frame_idx in self.keyboardCallbacks:
            print 'Wizard\tnextFrame() yes, this a keyboard callback frame'
            self.locationThread = WizardLocationListener(self, self.q_in)
            self.locationThread.start()
        nextFrame = self.frameList[self.frame_idx]
        print 'Wizard\tnextFrame() forcing nextFrame to be visible'
        nextFrame.grid(column = 0, row = 0, padx = 10, pady = 5, sticky = N+S+E+W)
        self.currentFrame = nextFrame
    
    def prevFrame(self):
        if self.locationThread:
            add_to_queue(self.q_in, messages.WIZARD_ABANDON_SHIP)
            self.locationThread = None
        self.currentFrame.grid_forget()
        self.frame_idx -= 1
        if self.frame_idx < 0: self.frame_idx = 0
        if self.frame_idx in self.keyboardCallbacks:
            self.locationThread = WizardLocationListener(self, self.q_in)
            self.locationThread.start()
        nextFrame = self.frameList[self.frame_idx]
        nextFrame.grid(column = 0, row = 0, padx = 10, pady = 5, sticky = N+S+E+W)
        self.currentFrame = nextFrame
    
    ###############################################################################
    ###                             TRANSITION FUNCTIONS                        ###
    ###############################################################################
    
    def quitWizard():
        add_to_queue(self.q_gui, messages.RELAUNCH_LISTENER)
        self.window.destroy()
        
    ##############################################################################
    ###                             LOCATION SETUP FUNCTIONS                   ###
    ##############################################################################
    
    #Initial function that starts off the layout config cascade
    def startLocationSetup(locationText, nextButton, backButton):
        firstConf = False
        
        #Clear the locationText widget
        locationText.delete(1.0, END)
        
        #Set the location frame as current frame
        self.currentFrame = locationFrame
        
        #Move to first step in layout configuration
        _defineArmInPile(locationText, nextButton, backButton)
    
    def _configuring_arm(self):
        return 'arm' in self.keyboardCallbacks[self.frame_idx]
    
    def _keyboard_callback(self, event):
        print 'Wizard\tKeyboard Event!'
        t = time.time()
        value = None
        settings_key = self.keyboardCallbacks[self.frame_idx]
        if t - self._last_time > 0.1:
            key = event.keycode
            self._last_time = t
            if self._configuring_arm():
                if key == 37:
                    #Left arrow press
                    #add_to_queue(self.q_out, messages.MOVE_LEFT)
                    value = self.robot.move_arm(clockwise=False)
                    print "Wizard\tarm move left to %s" % value
                    
                elif key == 39:
                    #add_to_queue(self.q_out, messages.MOVE_RIGHT)
                    value = self.robot.move_arm(clockwise=True)
                    #Right arrow press
                    print "Wizard\tarm move right to %s" % value
            else:
                if key == 38:
                    #add_to_queue(self.q_out, messages.MOVE_UP)
                    #Up arrow press
                    value = self.robot.move_actuator(up=True)
                    print "Wizard\tactuator move up to %s" % value
                elif key == 40:
                    #add_to_queue(self.q_out, messages.MOVE_DOWN)
                    #Down arrow press
                    value = self.robot.move_actuator(up=False)
                    print "Wizard\tactuator move down to %s" % value
            if value != None:
                print 'Wizard\tValue != None'
                s = {settings_key : value}
                print 'Wizard\tsettings:', s
                export_settings(**s)
    
    def registerMovement(self, value):
        key = self.keyboardCallbacks[self.frame_idx]
        settings[key] = value
        export_settings(**settings)
    
    ##############################################################################
    ###                             WRAPPER FUNCTIONS                          ###
    ##############################################################################
    
    def connectToGado(self):
        #We can move on from the connection frame (Hardcoded to true until we have real connectivity)
        t = WizardQueueListener(self.q_in, self.q_out, messages.ROBOT_CONNECT, None, self.robotConnectCallback)
        t.start()
    
    def robotConnectCallback(self, msg):
        if msg[0] == messages.RETURN:
            if msg[1]:
                self.nextButtons[self.frame_idx].config(state=NORMAL)
                t = WizardQueueListener(self.q_in, self.q_out, messages.GIVE_ME_A_ROBOT, None, self.robotCallback)
                t.start()
    
    def robotCallback(self, msg):
        print 'Wizard\tgot a robot callback'
        if msg[0] == messages.RETURN:
            if msg[1]:
                print 'Wizard\tassigned self.robot'
                self.robot = msg[1]
    
    def connectToScanner(self):
        t = WizardQueueListener(self.q_in, self.q_out, messages.SCANNER_CONNECT, None, self.connectedCallback)
        t.start()
    
    def connectToWebcam(self):
        t = WizardQueueListener(self.q_in, self.q_out, messages.WEBCAM_CONNECT, None, self.connectedCallback)
        t.start()
    
    def connectedCallback(self, msg):
        if msg[0] == messages.RETURN:
            if msg[1]:
                self.nextButtons[self.frame_idx].config(state=NORMAL)
                return
        add_to_queue(self.q_gui, messages.DISPLAY_ERROR, 'Unable to connect, please make sure everything is plugged in')
