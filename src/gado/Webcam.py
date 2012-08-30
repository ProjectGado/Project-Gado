from VideoCapture import Device

class Webcam():
    def __init__(self, webcam_name=None, **kargs):
        self.device = None
        self.device_number = None
        if True:#webcam_name != None:
            try:
                print 'Webcam\tinside the try'
                self.device = Device()
                print 'Webcam\tconnected'
                self.device_number = 1
                #self.device_number = device_number
            except:
                print 'Webcam\texcept - shit went down'
    
    def options(self):
        # I doubt people will have more than 5 webcams plugged in
        opts = []
        for i in range(5):
            try:
                d = Device(i)
                del d
                opts.append(d.getDisplayName())
            except:
                break
        return opts
    
    def connect(self, device_number):
        try:
            self.device = Device(device_number)
            self.device_number = device_number
        except:
            pass
    
    def disconnect(self):
        del self.device
        self.device = None 
    
    def savePicture(self, path, iterations=15):
        for i in range(iterations):
            self.device.saveSnapshot(path)

    def connected(self):
        return self.device_number != None
    