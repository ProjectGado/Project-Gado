from VideoCapture import Device

class Webcam(Device):
    def savePicture(self, path, iterations=15):
        for i in range(iterations):
            self.saveSnapshot(path)
