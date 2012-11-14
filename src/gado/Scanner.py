from __future__ import division
import win32com.client
import os, sys, pythoncom
from gado.Logger import Logger

#Constants

WIA_IMG_FORMAT_PNG = "{B96B3CAF-0728-11D3-9D7B-0000F81EF32E}"
WIA_COMMAND_TAKE_PICTURE = "{AF933CAC-ACAD-11D2-A093-00C04F72DC3C}"
WIA_HORIZONTAL_RESOLUTION = "Horizontal Resolution"
WIA_VERTICAL_RESOLUTION = "Vertical Resolution"
WIA_HORIZONTAL_EXTENT = "Horizontal Extent"
WIA_VERTICAL_EXTENT = "Vertical Extent"
WIA_HORIZONTAL_BED_SIZE = "Horizontal Bed Size"
WIA_VERTICAL_BED_SIZE = "Vertical Bed Size"
DEVICE_MANAGER = "WIA.DeviceManager"
COMMON_DIALOG = "WIA.CommonDialog"
SCALE_FACTOR = 1000
DEFAULT_DPI = 150

class Scanner():
    
    def __init__(self, **kwargs):
        
        pythoncom.CoInitialize()
        
        #Instantiate the logger
        loggerObj = Logger(__name__)
        self.logger = loggerObj.getLoggerInstance()
        
        #Init all of the scanner objects
        self.deviceManager = win32com.client.Dispatch(DEVICE_MANAGER)
        self.wiaObject = win32com.client.Dispatch(COMMON_DIALOG)
        
        self.device = None
        self.scanDpi = DEFAULT_DPI
        self.scannerName = None
        
        #Try and push the settings from the conf file
        try:
            self.scanDpi = kwargs['image_back_dpi']
            self.scannerName = kwargs['scanner_name']
        except:
            self.logger.exception("Error while instantiating scanner with passed settings...\nScanner\tError: %s" % (sys.exc_info()[0]))
       
    #Take the last image scanned on the scanner and transfer it to the local computer
    #Save it as imageName in the specified dir (specify the file format as well, eg. png, jpg, bmp)
    def scanImage(self, imageName, overwrite=True):
        
        if overwrite:
            try: os.remove(imageName) # try deleting it
            except:
                self.logger.exception("Exception scanning image")
                pass # file didn't exist. oh well.
        
        #If the DPI hasn't yet been set, then set it
        if self.scanDpi is None:
            self.setDPI(DEFAULT_DPI)
            
        try:
            #Transfer the raw image data from the scanner to the local computer
            image = self.device.Items[self.device.Items.count].Transfer(WIA_IMG_FORMAT_PNG)
            
            #Chdir to specified dir (if exists) and save the file as the passed name
            #If file already exists, it will be overwritten
            
            image.SaveFile(imageName)
                
            return True
        except:
            self.logger.exception("Scanner\tError while transferring image from scanner to computer...\nScanner\tError: %s\n%s" % (sys.exc_info()[0], sys.exc_info()[1]))
    
        return False
    
    #Using the scannerName property in gado.conf, try and connect to the scanner
    #If this property does not exist in the conf file or if the scanner is not
    #present on the local machine return False. Otherwise, return True
    def connectToScanner(self):
        
        if self.deviceManager is not None:
            #Iterate through the deviceManager to find our particular scanner (or not)
            for dev in self.deviceManager.DeviceInfos:
                
                #Look through each device to see if it's correct
                for prop in dev.Properties:
                    
                    if prop.Name == "Name" and prop.Value == self.scannerName:
                        #Found our scanner, let's connect to it
                        self.device = dev.Connect()
                        
                        self.setDPI(self.scanDpi)
                        
                        return True
        else:
            self.logger.critical("Scanner\tNo device manager?!")
        return False
    
    def connected(self):
        return self.connectToScannerGui()
    
    #Use Windows Image Aquisition's API to automatically pick the scanner to use
    #If there are multiple scanners available then a GUI pops up allowing the user to select one
    #If the selected scanner can successfully be connected to, then it is saved in the gado.conf
    #file for future use
    def connectToScannerGui(self):
        
        try:
            self.device = self.wiaObject.ShowSelectDevice()
            self.logger.debug("Scanner\tHAVE DEVICE: %s" % (self.device))
            self.logger.debug('Scanner\tsetting scan dpi %s' % self.scanDpi)
            self.setDPI(self.scanDpi)
            
            return True
        
        except:
            self.logger.exception("Scanner\tFailed to select a device, you should make sure everything is connected...\nScanner\tError: %s" % (sys.exc_info()[0]))
            
            return False
        
    #Pass in a dpi value to explicitly set the scanner to
    #This value is also saved in the gado.conf file for future use
    def setDPI(self, dpiValue):
        
        try:
            #Find each item for the connected device
            for item in self.device.Items:
                
                #Find each property for each item
                for prop in item.Properties:
                    
                    #Change both the horizontal and vertical dpi
                    if prop.Name == WIA_HORIZONTAL_RESOLUTION or prop.Name == WIA_VERTICAL_RESOLUTION:
                        
                        #Changing dpi settings, see if we have a valid dpi property
                        if self.scanDpi is not None:
                            prop.Value = self.scanDpi
                            
                        else:
                            #Setting to default, 600 DPI
                            prop.Value = DEFAULT_DPI
                            
                    #Change the horizontal and vertical extents (size) so we get the entire surface
                    #of the scanner scanned instead of just a portion
                    if prop.Name == WIA_HORIZONTAL_EXTENT:
                        
                        horBedSize = self._getHorizontalBedSize()
                        
                        horizontalExtent = int((horBedSize / SCALE_FACTOR) * float(dpiValue))
                        
                        prop.Value = horizontalExtent
                        
                    if prop.Name == WIA_VERTICAL_EXTENT:
                        
                        vertBedSize = self._getVerticalBedSize()
                        
                        verticalExtent = int((vertBedSize / SCALE_FACTOR) * float(dpiValue))
                        
                        prop.Value = verticalExtent
        except:
            print "Error trying to set dpi to value: %s...\nError: %s" % (dpiValue, sys.exc_info()[0])
            
    #Get the horizontal bed size (Used to calculate extents regarding setting custom DPIs)
    def _getHorizontalBedSize(self):
        
        if self.device is not None:
            
            for prop in self.device.Properties:
                if prop.Name == WIA_HORIZONTAL_BED_SIZE:
                    return prop.Value
                
        return -1
    
    #Get the vertical bed size (Used to calculate extents regarding setting custom DPIs)
    def _getVerticalBedSize(self):
        
        if self.device is not None:
            
            for prop in self.device.Properties:
                if prop.Name == WIA_VERTICAL_BED_SIZE:
                    return prop.Value
                
        return -1