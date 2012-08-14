from __future__ import division
import win32com.client
import os
import sys

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
DEFAULT_DPI = 600

class Scanner():
    
    def __init__(self, **kwargs):
        
        #Init all of the scanner objects
        self.deviceManager = win32com.client.Dispatch(DEVICE_MANAGER)
        self.wiaObject = win32com.client.Dispatch(COMMON_DIALOG)
        
        self.device = None
        self.scanDpi = DEFAULT_DPI
        self.scannerName = None
        
        #Try and push the settings from the conf file
        try:
            self.scanDpi = kwargs['scan_dpi']
            self.scannerName = kwargs['scanner_name']
        except:
            print "Error while instantiating scanner with passed settings...\nError: %s" % (sys.exc_info()[0])
        
            
    ######  IT SEEMS LIKE THIS FUNCTION DOESN'T ACTUALLY DO ANYTHING... MIGHT CONSIDER TAKING IT OUT #####        
            
    #Tell the scanner to scan a copy of whatever is currently on the scanner surface
    #This scan is stored on the scanner until transferImage is called, telling it where to save
    #on the local machine
    def scan(self, dirName, imageName):
        
        transferred = True
        
        try:
            for command in self.device.Commands:
                print "Command: %s" % command.Name
                if command.CommandID == WIA_COMMAND_TAKE_PICTURE:
                    print "here!"
                    self.device.ExecuteCommand(WIA_COMMAND_TAKE_PICTURE)
                    print "Told scanner to scan"
                    #Transfer the image
                    #transferred = self._transferImage(dirName, imageName)
                    
            return transferred
        
        except:
            print "Error trying to scan image...\nError: %s" % str(sys.exc_info())
            
            return False
    
    #Take the last image scanned on the scanner and transfer it to the local computer
    #Save it as imageName in the specified dir (specify the file format as well, eg. png, jpg, bmp)
    def scanImage(self, dirName, imageName):
        
        #If the DPI hasn't yet been set, then set it
        if self.scanDpi is None:
            self.setDPI(DEFAULT_DPI)
            
        try:
            #Transfer the raw image data from the scanner to the local computer
            image = self.device.Items[self.device.Items.count].Transfer(WIA_IMG_FORMAT_PNG)
            
            #Chdir to specified dir (if exists) and save the file as the passed name
            #If file already exists, it will be overwritten
            
            #see if dir exists
            if os.path.exists(dirName):
                #Dir exists, chdir and see if image exists
                os.chdir(dirName)
                
                if os.path.exists(imageName):
                    os.remove(imageName)
                
                #Actually save the image
                image.SaveFile(imageName)
                
                return True
            
            else:
                print "File path does not exist, please check again..."
                
        except:
            print "Error while transferring image from scanner to computer...\nError: %s\n%s" % (sys.exc_info()[0], sys.exc_info()[1])
    
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
                    
        return False
    
    #Use Windows Image Aquisition's API to automatically pick the scanner to use
    #If there are multiple scanners available then a GUI pops up allowing the user to select one
    #If the selected scanner can successfully be connected to, then it is saved in the gado.conf
    #file for future use
    def connectToScannerGui(self):
        
        try:
            self.device = self.wiaObject.ShowSelectDevice()
            
            self.setDPI(self.scanDpi)
            
            return True
        
        except:
            print "Failed to select a device, you should make sure everything is connected...\nError: %s" % (sys.exc_info()[0])
            
            return False
    
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
    
    #Enumerate through each item in the connected device's heirarchy and dump out all properties
    #that are found
    def dumpProperties(self):
        
        #Dump all information concerning connected WIA devices
        print "WIA Devices Information:\n\n"
        
        for info in self.deviceManager.DeviceInfos:
            #Each property for each device
            for prop in info.Properties:
                print "%s -> %s" % (prop.Name, prop.Value)
        
        print "\n\n"
        
        #Dump all commands for connected device (if it exists)
        if self.device is not None and len(self.device.Commands) > 1:
            print "Device Specific Commands:\n"
            
            for command in self.device.Commands:
                print "%s -> %s" % (command.CommandID, command.Description)
        
            print "\n\n"
            
        #Dump all device specific properties
        if self.device is not None:
            print "Device Specific Properties:\n"
            
            for prop in self.device.Properties:
                if prop.isReadOnly:
                    print "%s -> %s (Read Only)" % (prop.Name, prop.Value)
                else:
                    print "%s -> %s (Read/Write)" % (prop.Name, prop.Value)
                
            print "\n\n"
            
        #Dump all items and their properties
        if self.device is not None:
            print "Item Hierarchy and Properties:\n"
            
            for item in self.device.Items:
                for prop in item.Properties:
                    if prop.IsReadOnly:
                        print "%s -> %s (Read Only)" % (prop.Name, prop.Value)
                    else:
                        print "%s -> %s (Read/Write)" % (prop.Name, prop.Value)
                        
            print "\n\n"