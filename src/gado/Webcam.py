from VideoCapture import Device
from gado.Logger import Logger

class Webcam():
    def __init__(self, webcam_name=None, webcam_id=None, **kargs):
        
        #Instantiate the logger
        loggerObj = Logger(__name__)
        self.logger = loggerObj.getLoggerInstance()
        
        self.device = None
        self.logger.debug('__init__ called with webcam_name=%s and webcam_id=%s' % (webcam_name, webcam_id))
        if webcam_name is not None:
            self.connect(device_name=webcam_name)
        elif webcam_id is not None:
            self.connect(device_number=webcam_id)
    
    def options(self, device_name=None, device_number=None):
        # I doubt people will have more than 5 webcams plugged in
        self.logger.debug('options() called with device_name %s and device_number %s' % (device_name, device_number))
        opts = []
        for i in range(2):
            try:
                self.logger.debug('options - attempting to connect to %s' % i)
                d = Device(devnum=i)
                if device_name is not None and device_name == d.getDisplayName():
                    del self.device
                    self.device = d
                elif device_number is not None and device_number == i:
                    del self.device
                    self.device = d
                opts.append((i, d.getDisplayName()))
                del d
            except:
                self.logger.exception("Exception while setting webcam options")
                pass
        self.logger.debug('options() returning %s' % opts)
        if self.connected():
            self.logger.debug('options - managed to connect to a device!')
        return opts
    
    def connect(self, device_name=None, device_number=None):
        self.logger.debug('connect() called with device_name %s and device_number %s' % (device_name, device_number))
        if device_name is not None:
            self.options(device_name=device_name)
        elif device_number is not None:
            self.options(device_number=device_number)
        else:
            self.logger.error('connect() called with NOTHING!')
            self.device = Device()
            self.logger.debug('success?')
    
    def disconnect(self):
        del self.device
        self.device = None 
    
    def savePicture(self, path, iterations=20, keep_all=False):
        if keep_all:
            i = path.rfind('.')
            img = '%s%%s%s' % (path[:i], path[i:])
        for i in range(iterations):
            if keep_all:
                self.device.saveSnapshot(img % i)
                if i == iterations - 1:
                    self.device.saveSnapshot(path)
            else:
                self.device.saveSnapshot(path)

    def connected(self):
        return (self.device != None)
    