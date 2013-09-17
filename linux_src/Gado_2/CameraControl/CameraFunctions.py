'''

A class for the webcam using the pygame library

@author: Agusti Pellicer (Aalto University)

'''

import pygame.camera as PyCamera
import pygame.image as PyGameImage
import Image

class Camera:
	def __init__(self,camera=0,resolution=(640,480)):
		""" Init the camera with a camera and a certain resolution """
		PyCamera.init()
		try:
			self.cam = PyCamera.Camera(PyCamera.list_cameras()[camera],resolution)
			self.resolution = resolution
		except Exception:
			print 'Problem initializing the camera!'

	def captureBackImage(self, filename):
		""" Capture an image using the default resolution """
		self.cam.start()
		img_surface = self.cam.get_image()
		pil_string_image = PyGameImage.tostring(img_surface, "RGBA",False)
		img = Image.fromstring("RGBA",self.resolution,pil_string_image)
		img.save(filename)
		self.cam.stop()

	def closeCamera(self):
		""" Closing the camera """
		PyCamera.quit()

if __name__ == '__main__':
	camera = Camera()
	camera.captureBackImage('outfile.jpg')
	camera.closeCamera()