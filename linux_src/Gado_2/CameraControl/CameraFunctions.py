'''

A class for the webcam using pygame library

@author: Agusti Pellicer

'''

import pygame.camera as PyCamera
import pygame.image as PyGameImage
import Image

#import subprocess
import shlex


class Camera:
	def __init__(self):
		PyCamera.init()
		#Because we have two
		try:
			self.cam = PyCamera.Camera(PyCamera.list_cameras()[1],(1920,1080))
		except Exception:
			print 'Problem initializing the camera!'

	def captureBackImage(self, filename):

		#It's a surface let's use PIL
		self.cam.start()
		img_surface = self.cam.get_image()
		pil_string_image = PyGameImage.tostring(img_surface, "RGBA",False)
		img = Image.fromstring("RGBA",(1920,1080),pil_string_image)
		img.save(filename)
		self.cam.stop()

	def closeCamera(self):
		PyCamera.quit()

if __name__ == '__main__':
	camera = Camera()
	camera.captureBackImage('outfile.jpg')
	camera.closeCamera()