# Database requests
WEIGHTED_ARTIFACT_SET_LIST = 0 # RETURN (list)
ARTIFACT_SET_LIST = 1 # RETURN (list)
ADD_ARTIFACT_SET_LIST = 2 # RETURN (id)
DELETE_ARTIFACT_SET_LIST = 3 # VOID

# General robot commands
START = 4   # shouldn't return
STOP = 5    # No return   
LAST_ARTIFACT = 6 # No return
RESET = 7   # No return

# Connection and pictures
ROBOT_CONNECT = 8 # Return (boolean)

SCANNER_LISTING = 9.1 # RETURN ([scanner_names])
SCANNER_PICTURE = 9 # RETURN (path)
SCANNER_CONNECT = 10 # RETURN (boolean)

WEBCAM_LISTING = 10.1 # RETURN ([webcam_names])
WEBCAM_PICTURE = 11 # RETURN (path)
WEBCAM_CONNECT = 12 # RETURN (boolean)

# Manual robot controls
MOVE_RIGHT = 13 # RETURN (degree)
MOVE_LEFT = 14 # RETURN (degree)
MOVE_UP = 15 # RETURN (stroke)
MOVE_DOWN = 16 # RETURN (stroke)

DROP = 17 # VOID
LIFT = 18 # VOID

# MISC
SET_SELECTED_ARTIFACT_SET = 21 # VOID
RELOAD_SETTINGS = 22 # VOID

# Other misc
LAUNCH_WIZARD = 23 # VOID
READY = 24 # VOID
MAIN_READY = 24.1

# Returning values
RETURN = 19 # returning useful stuff (like db info)
UPDATE = 20 # providing an interface update, "Gado is currently XXXXX"

# GUI Messages
SET_SCANNER_PICTURE = 25
SET_WEBCAM_PICTURE = 26
SET_STATUS_TEXT = 27
DISPLAY_ERROR = 28
DISPLAY_INFO = 29

# Tells everyone to call exit()
SYSTEM_ABANDON_SHIP = 30
MAIN_ABANDON_SHIP = 31
GUI_ABANDON_SHIP = 32
WIZARD_ABANDON_SHIP = 33
GIVE_ME_A_ROBOT = 34 # Returns a robot
GUI_LISTENER_DIE = 35
RELAUNCH_LISTENER = 36
REFRESH = 37