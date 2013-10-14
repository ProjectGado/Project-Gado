'''

A class for representing a scanner in Linux using the sane library

@author: Agusti Pellicer (Aalto University)

'''
import sane

class Scanner:

    def __init__(self,scanner=0,dpi=600,mode='Gray',depth=8):
        """ Scanner class with default parameters """
        sane.init()
        devices = sane.get_devices()
        try:
            device = devices[scanner]
        except IndexError:
            print 'No scanner found'
            self.scanner = False
            return
        
        #We just get the first one
        self.scanner = sane.open(device[0])
        #improve dpi
        self.scanner.resolution = dpi

        #there's other options to change 
        self.scanner.mode = mode
        self.scanner.depth = depth

    def scanImage(self):
        """ Scan the image (returns a PIL object) """
        img = self.scanner.scan()
        return img

    def printInfoScanner(self):
        """ Small utility to print the scanner options and parameters """
        for option in self.scanner.optlist:
            try:
                print self.scanner[option]
            except AttributeError as e:
                print 'Option not supported: ' + e.__str__()
                pass

    def closeScanner(self):
        """ We close the scanner """
        print self.scanner.close()
        print sane.exit()

if __name__ == '__main__':
    """ Small test for trying the different capabilities """
    scannerObject = Scanner()
    if not scannerObject.scanner:
        print 'Scanner not hooked up'
        exit()
    while True:
        print 'What do you want to do?'
        print '1. Scan'
        print '2. Scanner info'
        print '3. Exit'
        option = raw_input('Option:')
        try:
            if int(option) == 2:
                scannerObject.printInfoScanner()
            if int(option) == 3:
                scannerObject.closeScanner()
                exit()
            if int(option) == 1:
                img  = scannerObject.scanImage()
                img.save('test.tiff')
        except ValueError:
            print 'Please input a number'
            pass
