'''
Basic loop for scanning artifacts.

Please adjust the different values for the arm
 
'''
import ScannerControl.ScannerFunctionsTest as SF
import CameraControl.CameraFunctions as CF
import ComputerVision.BarcodeDetection as B

import Robot
import time
import serial

import os
import sane

#Setting up the robot
try:
    gado = Robot.Robot('/dev/ttyACM0')
except serial.serialutil.SerialException:
    print 'Robot not connected at /dev/ttyACM0'
    print 'Please check that is connected properly'
    exit()
    
time.sleep(5)
gado.connect()

#Our own scanner
scanner = SF.Scanner()

#Take a picture of the stack
camera = CF.Camera()

camera.captureBackImage('output.jpg')
#Robot, you go home
gado.goHome()

first_run = 1

#Main loop
while True:
    #0
    name = time.time()
    if first_run == 0:
        camera.captureBackImage("output.jpg")
    else:
        first_run = 0
    #Try to see if we find the QR code
    barcodes = B.findBarcodes("output.jpg")
    if barcodes:
        if barcodes[0] and barcodes[0] == "project gado":
            gado.sendRawActuatorWithBlocking(25)
            print "--------"
            print "DONE WITH STACK"
            print "--------"
            #Time to close everyhting we opened
            scanner.closeScanner()
            camera.closeCamera()
            exit()
    #1
    gado.sendRawArmTimeBlocking(20)
    start = time.time()
    print '1'

    #2
    gado.sendVacuum(120)
    print '2.1'
    gado.lowerAndLiftInternal()
    print '2.2'
    gado.sendRawActuatorWithBlocking(25)
    print '2.3'
    gado.sendRawActuatorWithBlocking(25)
    
    
    print '2.4'
    #3
    gado.sendRawArmTimeBlocking(120)
    print '3'
    #4
    gado.sendRawActuatorWithBlocking(184)
    print '4'
    
    #Save scanned image
    image = scanner.scanImage()
    image.save('ouput.tiff')

    #Some error problem maybe
    if not os.path.exists("output.jpg"):
        print "The camera failed to take an image"
        gado.sendRawActuatorWithBlocking(25)
        exit()
    #6
    print '6'
    gado.sendRawActuatorWithBlocking(70)
    
    #7
    print '7'
    gado.sendRawArmTimeBlocking(180)
    gado.sendVacuum(0)
    time.sleep(2)
    elapsed = time.time() - start
    elapsed = elapsed - 5
    print elapsed
