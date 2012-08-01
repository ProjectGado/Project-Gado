from gado.Robot import Robot
import thread
from threading import Thread

class WebcamThread(Thread):
    def __init__(self):
        pass
    
    def run(self):
        '''
        Takes a picture of the back of the image
        '''
        pass

class ScannerThread(Thread):
    def __init__(self, funct):
        self.funct
        pass
    
    def run(self):
        cmd = 'self.%s' % self.funct
        exec("cmd")
    
    def initialize(self):
        '''
        "Warms up" the scanner for scanning
        '''
        pass
        
    def transfer(self):
        '''
        Gets the image from the scanner to the machine
        '''
        pass

class RobotThread(Thread):
    def __init__(self, robot, action):
        self.robot = robot
        self.action = action
    
    def run():
        cmd = 'self.%s' % self.action
        exec(cmd)
        
    def reset():
        self.robot.reset()
    
    

class GadoSystem():
    def __init__(self, dbi, robot):
        self.robot = robot
        self.dbi = dbi
    
    def start(self):
        # Sanity check
        if not self.robot.connected():
            raise Exception("No robot connected")
        
        # Warmup!
        rthread = RobotThread('')
        self.robot.reset()
        self._initialize_scanner()
        
        #
        image = self._capture_webcam()
        while not (_check_barcode(image)):
            
            
            pass
        
        pass
    
    def connect(self, port=None):
        '''
        If port is none, then cycle through all available comm ports
        '''
        if not comm:
            #Query the comm ports available on the system
            rawPortList = str(subprocess.check_output(["python", "-m", "serial.tools.list_ports"]))
            ports = re.findall('(COM\d+)', rawPortList)
        
            for port in ports:
                success = robot.connect(port)
                if success:
                    return True
        else:
            success = self.robot.connect(port)
            return success
        return False
    
    def disconnect(self):
        pass
        return True
    
    def _capture_webcam(self):
        '''
        Captures a backside view of the next image in queue
        '''
        image = None
        return image
    
    def _check_barcode(self, image):
        '''
        Checks for a barcode within image
        '''
        return True
    
    def _initialize_scanner(self):
        pass
    
    def _scan_image(self):
        '''
        Instructs the scanner to scan the image
        This does not transfer the image to the computer yet
        '''
        pass
    
    def _transfer_image(self):
        pass
    