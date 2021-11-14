# import the necessary packages
from picamera.array import PiRGBArray
from picamera import PiCamera
import time
import cv2
import numpy as np

# Load the cascade
#face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
#face_cascade = cv2.CascadeClassifier('haarcascade_fullbody.xml')

# initialize the HOG descriptor/person detector
hog = cv2.HOGDescriptor()
hog.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())

# To capture video from webcam. 
#cap = cv2.VideoCapture(0)
# To use a video file as input 
# cap = cv2.VideoCapture('filename.mp4')

#time.sleep(3)
# initialize the camera and grab a reference to the raw camera capture
camera = PiCamera()
camera.resolution = (640, 480)
camera.rotation = 180
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

# detect people in the image
    # returns the bounding boxes for the detected objects
    boxes, weights = hog.detectMultiScale(gray, winStride=(8,8) )

    boxes = np.array([[x, y, x + w, y + h] for (x, y, w, h) in boxes])

    for (xA, yA, xB, yB) in boxes:
        # display the detected boxes in the colour picture
        cv2.rectangle(gray, (xA, yA), (xB, yB), (0, 255, 0), 2)



    # Detect the faces
#    faces = face_cascade.detectMultiScale(gray, 1.1, 4)
    # Draw the rectangle around each face
#    for (x, y, w, h) in faces:
#        cv2.rectangle(img, (x, y), (x+w, y+h), (255, 0, 0), 2)

    cv2.namedWindow("Frame", cv2.WND_PROP_FULLSCREEN)
    cv2.setWindowProperty("Frame",cv2.WND_PROP_FULLSCREEN,cv2.WINDOW_FULLSCREEN)



    # show the frame
    cv2.imshow("Frame", img)
    key = cv2.waitKey(1) & 0xFF
    # clear the stream in preparation for the next frame
    rawCapture.truncate(0)
    # if the `q` key was pressed, break from the loop
    if key == ord("q"):
        break


