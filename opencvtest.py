from picamera import PiCamera
from picamera.array import PiRGBArray
import time
import cv2


camera = PiCamera(framerate = 40)
time.sleep(2)
camera.resolution = (640,480)
rawCapture = PiRGBArray(camera, size=camera.resolution)
start = time.time()
for frame, i in zip(camera.capture_continuous(rawCapture, format="bgr", use_video_port=True), range(400)):
    image = frame.array
    rawCapture.truncate(0)
print("Time for {0} frames: {1} seconds".format(frames ,time.time()-start))


#cap = cv2.VideoCapture(0)
#cap.set(cv2.CAP_PROP_FRAME_WIDTH,640)
#cap.set(cv2.CAP_PROP_FRAME_HEIGHT,480)
#cap.set(cv2.CAP_PROP_FPS, 40)
#start = time.time()
#for i in range(400):
#    ret, img = cap.read()
#print("Time for {0} frames: {1} seconds".format(frames, time.time() - start))
