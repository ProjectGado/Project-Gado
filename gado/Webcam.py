from VideoCapture import Device

class Webcam():
    def __init__(self, webcam_name=None, webcam_id=None, **kargs):
        self.device = None
        print 'Webcam\t__init__ called with webcam_name=%s and webcam_id=%s' % (webcam_name, webcam_id)
        if webcam_name is not None:
            self.connect(device_name=webcam_name)
        elif webcam_id is not None:
            self.connect(device_number=webcam_id)
    
    def options(self, device_name=None, device_number=None):
        # I doubt people will have more than 5 webcams plugged in
        print 'Webcam\toptions() called'
        opts = []
        for i in range(2):
            try:
                print 'Webcam\toptions - attempting to connect to %s' % i
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
                raise
        print 'Webcam\toptions() returning %s' % opts
        return opts
    
    def connect(self, device_name=None, device_number=None):
        if device_name is not None:
            self.options(device_name=device_name)
        elif device_number is not None:
            self.options(device_number=device_number)
        else:
            self.device = Device()
    
    def disconnect(self):
        del self.device
        self.device = None 
    
    def savePicture(self, path, iterations=15):
        for i in range(iterations):
            self.device.saveSnapshot(path)

    def connected(self):
        return (self.device != None)
    