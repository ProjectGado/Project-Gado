from VideoCapture import Device

class Webcam(Device):
    def __init__(self, **kargs):
        try:
            Device.__init__(self)
            self._connected = True
        except:
            self._connected = False
        #self.setResolution(1600, 1200)
        #self.displayCapturePinProperties()
    
    def savePicture(self, path, iterations=15):
        for i in range(iterations):
            self.saveSnapshot(path)

    def connected(self):
        return self._connected