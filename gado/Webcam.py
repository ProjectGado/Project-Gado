import cv

class Webcam():
    
    def __init__(self):
        
        self.capture = None
    
    #Create a capute object from the system's firt webcam
    #In the future, this function should be expanded to check
    #each webcam the system has present
    
    def connect(self):
        #Open capture
        try:
            self.capture = cv.CaptureFromCAM(0)
            
            return True
        
        except:    
            print "Can't connect to the webcam, make sure it's connected..."
            
            return False
    
    #Return a frame grabbed from the webcam    
    def returnImage(self):
        image = cv.QueryFrame(self.capture)
        
        return image
    
    #Takes in a image path and an image object
    #Saves that object to that path on the system
    def saveImage(self, path, image):
        
        try:
            cv.SaveImage(path, image)
            
            return True
        
        except:
            print "Problem saving image: %s to path: %s" % (image, path)
            
            return False