'''

A class for representing a scanner in Linux using the sane library

'''
import sane

class Scanner:

	def __init__(self):
		"""" We init the scanner properties """
		print 'Init sane'
		print sane.init()
		devices = sane.get_devices()
		print devices
		try:
			device = devices[0]
		except IndexError:
			print 'No scanner found'
			self.scanner = False
			return
		
		#We just get the first one
		self.scanner = sane.open(device[0])
		#improve dpi
		self.scanner.resolution = 600

		#there's other options to change 
		self.scanner.mode = 'Gray' # 'Gray' by default
		#scanner.depth = 16 # 8 by default

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

	def chooseScanner(self):
		""" Maybe we can just try to let the user choose the scanner """
		pass

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
				break
			if int(option) == 1:
				img  = scannerObject.scanImage()
				img.save('test.tiff')
		except ValueError:
			print 'Please input a number'
			pass