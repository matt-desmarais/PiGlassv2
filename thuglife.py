# import the necessary packages
from picamera.array import PiRGBArray
from picamera import PiCamera
import time
import cv2
from PIL import Image
import numpy as np

# thug life meme mask image path
maskPath = "mask.png"
# haarcascade path
cascPath = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')

# Open mask as PIL image
mask = Image.open(maskPath)

def thug_mask(image):
	"""
	function to add thug life mask to input image
	"""

	# convert input image to grayscale
	gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

	# detect faces in grayscale image
	faces = cascPath.detectMultiScale(gray, 1.15)

	# convert cv2 imageto PIL image
	background = Image.fromarray(image)

	for (x,y,w,h) in faces:
		# resize mask
		resized_mask = mask.resize((w,h), Image.ANTIALIAS)
		# define offset for mask
		offset = (x,y)
		# pask mask on background
		background.paste(resized_mask, offset, mask=resized_mask)

	# return background as cv2 image
	return np.asarray(background)

# initialize the camera and grab a reference to the raw camera capture
camera = PiCamera()
camera.resolution = (640, 480)
camera.rotation = -90
camera.framerate = 32
rawCapture = PiRGBArray(camera, size=(640, 480))
time.sleep(.25)

# capture frames from the camera
for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
    # grab the raw NumPy array representing the image, then initialize the timestamp
    # and occupied/unoccupied text
    img = frame.array

    # Convert to grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Detect the faces
    faces = cascPath.detectMultiScale(gray, 1.1, 4)

    cv2.namedWindow("Frame", cv2.WND_PROP_FULLSCREEN)
    cv2.setWindowProperty("Frame",cv2.WND_PROP_FULLSCREEN,cv2.WINDOW_FULLSCREEN)

    # show the frame
    cv2.imshow("Frame", thug_mask(img))
    key = cv2.waitKey(1) & 0xFF
    # clear the stream in preparation for the next frame
    rawCapture.truncate(0)
    # if the `q` key was pressed, break from the loop
    if key == ord("q"):
        break


