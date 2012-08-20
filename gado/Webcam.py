from VideoCapture import Device

class Webcam(Device):
    def __init__(self, **kargs):
        print 'Webcam\t__init__ called'
        try:
            Device.__init__(self)
            self._connected = True
            print 'Webcam\tConnected to webcam'
        except:
            print 'Webcam\tFailed to connect to webcam'
            self._connected = False
        #self.setResolution(1600, 1200)
        #self.displayCapturePinProperties()
        print 'Webcam\treturning from __init__'
    
    def savePicture(self, path, iterations=15):
        for i in range(iterations):
            self.saveSnapshot(path)

    def connected(self):
        return self._connected