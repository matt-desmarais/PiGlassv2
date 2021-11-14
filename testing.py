from picamera import PiCamera, Color
from time import sleep

camera = PiCamera()
camera.resolution = (2200, 1600)
camera.start_preview()
camera.annotate_background = Color('blue')
camera.annotate_foreground = Color('white')
camera.annotate_text_size = 160
camera.annotate_text = "\n\n\nHello world"

sleep(5)
camera.stop_preview()
