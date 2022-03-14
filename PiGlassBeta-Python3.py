from evdev import InputDevice, categorize, ecodes
from subprocess import call
import RPi.GPIO as GPIO
from picamera import PiCamera
from picamera import Color
#import picamera
import time
import sys
import datetime
import cv2
import numpy as np
import subprocess
from subprocess import DEVNULL, STDOUT, check_call
import _thread
import os
import psutil
import vlc
from PIL import Image

# thug life meme mask image path
maskPath = "mask.png"

# cascade classifier object 
faceCascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')


#####def get_file_name_vid():  # new
#####    return datetime.datetime.now().strftime("Camera-%m-%d_%H.%M.%S.h264")
#global click, action, cut
click = vlc.MediaPlayer("file:///home/pi/PiGlassv2/click.mp3")
action = vlc.MediaPlayer("file:///home/pi/PiGlassv2/action.mp3")
cut = vlc.MediaPlayer("file:///home/pi/PiGlassv2/cut.mp3")
tl = vlc.MediaPlayer("file:///home/pi/PiGlassv2/TL.mp3")

height = 1080
width = 1920
alphaValue = 75
o = None
recording = 0
buttoncounter = 0
#camera = picamera.PiCamera()
camera = PiCamera()
global zoomcount
zoomcount=0
globalCounter = 0
#global key
key = ""
#global m
m=None
#global filename
filename = None

#recording = get_file_name_vid()
#camera.start_recording(recording)

def checkIfProcessRunning(processName):
    '''
    Check if there is any running process that contains the given name processName.
    '''
    #Iterate over the all the running process
    for proc in psutil.process_iter():
        try:
            # Check if process name contains the given name string.
            if processName.lower() in proc.name().lower():
                return True
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    return False;

def thuglife():
    TLfilename = get_file_name_TLpic()
    camera.capture(TLfilename, use_video_port=True)
    # read input image
    image = cv2.imread(TLfilename)
    # convert image to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # detect faces in grayscale image
    faces = faceCascade.detectMultiScale(gray, 1.15)

    # open input image as PIL image
    background = Image.open(TLfilename)

    # paste mask on each detected face in input image
    for (x,y,w,h) in faces:

        # just to show detected faces
        cv2.rectangle(image, (x,y), (x+w, y+h), (255, 0, 0), 2)
        #cv2.imshow('face detected', image)
        #cv2.waitKey(0)

        # open mask as PIL image
        mask = Image.open(maskPath)
        # resize mask according to detected face
        mask = mask.resize((w,h), Image.ANTIALIAS)

        # define offset for mask
        offset = (x,y)
        # paste mask on background
        background.paste(mask, offset, mask=mask)

    # paste final thug life meme
    background.save(TLfilename)

    photofile = "cp "+TLfilename+" /home/pi/Pictures/"
    print(filename)
    subprocess.Popen(photofile, shell=True)





#creates object 'gamepad' to store the data
#you can call it whatever you like
#global gamepad
gamepad = InputDevice('/dev/input/by-id/Gamepad')

#button code variables (change to suit your device)
aBtn = 305
bBtn = 304
xBtn = 307
yBtn = 306
#up = 'ABS_Y'
#down = 'ABS_Y'
#left = 'ABS_X'
#right = 'ABS_X'
start = 313
select = 312
lTrig = 308
rTrig = 309
#prints out device info at start
print(gamepad)


def initialize_camera():
    camera.resolution = (width, height)
#    camera.framerate = 15
#    picamera.annotate_size = 220 
    camera.annotate_text_size = 160
    camera.sharpness = 0
    camera.contrast = 0
    camera.brightness = 50
    camera.saturation = 0    
    camera.ISO = 0
    camera.video_stabilization = True
    camera.exposure_compensation = 0
    camera.exposure_mode = 'auto'
    camera.meter_mode = 'average'
    camera.awb_mode = 'auto'
    camera.image_effect = 'none'
    camera.color_effects = None
    camera.rotation = -90
    camera.hflip = False
    camera.vflip = False
    camera.start_preview()
#####    recording = get_file_name_vid()
#####    camera.start_recording(recording)
    print("Camera is configured and outputting video...")

if (width%32) > 0 or (height%16) > 0:
    print("Rounding down set resolution to match camera block size:")
    width = width-(width%32)
    height = height-(height%16)
    print("New resolution: " + str(width) + "x" + str(height))

ovl = np.zeros((height, width, 3), dtype=np.uint8)

globalz = {
    'zoom_step'     : 0.03,
    'zoom_xy_min'   : 0.0,
    'zoom_x'       : 0.0,
    'zoom_y'       : 0.0,
    'zoom_xy_max'   : 0.4,
    'zoom_wh_min'   : 1.0,
    'zoom_wh'       : 1.0,
    'zoom_wh_max'   : 0.2,
}

def update_zoom():
    camera.zoom = (globalz['zoom_x'], globalz['zoom_y'], globalz['zoom_wh'], globalz['zoom_wh'])
    print("Camera at (x, y, w, h) = ", camera.zoom)

def set_min_zoom():
    globalz['zoom_x'] = globalz['zoom_xy_min']
    globalz['zoom_y'] = globalz['zoom_xy_min']
    globalz['zoom_wh'] = globalz['zoom_wh_min']

def set_max_zoom():
    globalz['zoom_x'] = globalz['zoom_xy_max']
    globalz['zoom_y'] = globalz['zoom_xy_max']
    globalz['zoom_wh'] = globalz['zoom_wh_max']

def zoom_out():
    global zoomcount
    if globalz['zoom_x'] - globalz['zoom_step'] < globalz['zoom_xy_min'] and globalz['zoom_y'] - globalz['zoom_step'] < globalz['zoom_xy_min']:
        print("At min zoom")
        #set_min_zoom()
    elif zoomcount >= 1:
        globalz['zoom_x'] -= globalz['zoom_step']
        globalz['zoom_y'] -= globalz['zoom_step']
        globalz['zoom_wh'] += (globalz['zoom_step'] * 2)
        zoomcount = zoomcount - 1
    update_zoom()

def zoom_in():
    global zoomcount
    if globalz['zoom_x'] + globalz['zoom_step'] > globalz['zoom_xy_max'] and globalz['zoom_y'] + globalz['zoom_step'] > globalz['zoom_xy_max']:
        print("At max zoom")
#        set_max_zoom()
    elif zoomcount < 10:
        zoomcount = zoomcount + 1
        globalz['zoom_x'] += globalz['zoom_step']
        globalz['zoom_y'] += globalz['zoom_step']
        globalz['zoom_wh'] -= (globalz['zoom_step'] * 2)
    update_zoom()

def pan_right():
    global zoomcount
    globalz['zoom_y'] += globalz['zoom_step']
    update_zoom()

def pan_left():
    global zoomcount
    globalz['zoom_y'] -= globalz['zoom_step']
    update_zoom()

def pan_up():
    global zoomcount
    globalz['zoom_x'] -= globalz['zoom_step']
    update_zoom()

def pan_down():
    global zoomcount
    globalz['zoom_x'] += globalz['zoom_step']
    update_zoom()


ovl = np.zeros((height, width, 3), dtype=np.uint8)

# initial config for gpio ports
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)

colors = {
        'white': (255,255,255),
        'red': (255,0,0),
        'green': (0,255,0),
        'blue': (0,0,255),
        'yellow': (255,255,0),
        }

def colormap(col):
    return colors.get(col, (255,255,255))

col = colormap('white')
font = cv2.FONT_HERSHEY_PLAIN

guivisible = 1
togsw = 1
guiOn = 1
gui = np.zeros((height, width, 3), dtype=np.uint8)
gui1 = 'PiGlassV2'
gui2 = 'Hold X: Take Picture'
gui3 = 'Hold A: Record Video'
gui4 = 'Bumpers: Zoom In/Out'
gui5 = 'Up/Down/Left/Right: Pan'

def upload_file(file_from, file_to):
    dbx = dropbox.Dropbox(token)
    f = open(file_from, 'rb')
    dbx.files_upload(f.read(), file_to)

def get_file_name_TLpic():  # new
    return datetime.datetime.now().strftime("TL-%Y-%m-%d_%H.%M.%S.jpg")

def get_file_name_pic():  # new
    return datetime.datetime.now().strftime("%Y-%m-%d_%H.%M.%S.jpg")

def get_file_name_vid():  # new
    return datetime.datetime.now().strftime("%Y-%m-%d_%H.%M.%S.h264")

def creategui(target):
    global gui5
    cv2.putText(target, gui1, (10,height-160), font, 10, col, 6)
    cv2.putText(target, gui2, (10,height-130), font, 3, col, 3)
    cv2.putText(target, gui3, (10,height-90), font, 3, col, 3)
    cv2.putText(target, gui4, (10,height-50), font, 3, col, 3)
    cv2.putText(target, gui5, (10,height-10), font, 3, col, 3)
    return

def patternswitch(target,guitoggle):
    global o, alphaValue
    toggleonoff()
    if guitoggle == 1:
            creategui(gui)
    o = camera.add_overlay(bytes(memoryview(target)), layer=3, alpha=alphaValue)
    return

def patternswitcherRecord(target,guitoggle):
    global o ###########, zoomcount, ycenter
    if guitoggle == 1:
        creategui(gui)

# function 
def togglepatternRecord():
    global togsw,o,curpat,col,ovl,gui,alphaValue,ycenter,zoomcount
    # if overlay is inactive, ignore button:
    if togsw == 0:
        print("Pattern button pressed, but ignored --- Crosshair not visible.")
    else:
        if guivisible == 0:
            ovl = np.zeros((height, width, 3), dtype=np.uint8)
            patternswitcherRecord(ovl,0)
        else:
            gui = np.zeros((height, width, 3), dtype=np.uint8)
            creategui(gui)
            patternswitcherRecord(gui,1)
    return

def togglepattern():
    global togsw,o,ovl,gui,alphaValue
    # if overlay is inactive, ignore button:
    if togsw == 0:
        print("Pattern button pressed, but ignored --- Crosshair not visible.")
    # if overlay is active, drop it, change pattern, then show it again
    else:
        if guivisible == 0:
            # reinitialize array:
            ovl = np.zeros((height, width, 3), dtype=np.uint8)
            patternswitch(ovl,0)
            if o != None:
                camera.remove_overlay(o)
            o = camera.add_overlay(bytes(memoryview(ovl)), layer=3, alpha=alphaValue)
        else:
            # reinitialize array
            gui = np.zeros((height, width, 3), dtype=np.uint8)
            creategui(gui)
            patternswitch(gui,1)
            if o != None:
                camera.remove_overlay(o)
            o = camera.add_overlay(bytes(memoryview(gui)), layer=3, alpha=alphaValue)
    return

def toggleonoff():
    global togsw,o,alphaValue
    if togsw == 1:
        print("Toggle Crosshair OFF")
        if o != None:
            camera.remove_overlay(o)
            togsw = 0
    else:
        print("Toggle Crosshair ON")
        if guivisible == 0:
            o = camera.add_overlay(bytes(memoryview(ovl)), layer=3, alpha=alphaValue)
        else:
            o = camera.add_overlay(bytes(memoryview(gui)), layer=3, alpha=alphaValue)
        togsw = 1
    return

# function 
def togglepatternZoomIn():
#################    #global togsw,o,curpat,col,ovl,gui,alphaValue,ycenter,zoomcount
    # if overlay is inactive, ignore button:
    if togsw == 0:
        print("Pattern button pressed, but ignored --- Crosshair not visible.")
        zoom_in()
    else:
        if guivisible == 0:
            zoom_in()
	    # reinitialize array:
            ovl = np.zeros((height, width, 3), dtype=np.uint8)
            patternswitcherZoomIn(ovl,0)
        else:
            # reinitialize array
            zoom_in()
            gui = np.zeros((height, width, 3), dtype=np.uint8)
            creategui(gui)
            patternswitcherZoomIn(gui,1)
    return

def togglepatternZoomOut():
    global togsw,o,curpat,col,ovl,gui,alphaValue
    # if overlay is inactive, ignore button:
    if togsw == 0:
        zoom_out()
    else:
        if guivisible == 0:
            zoom_out()
            # reinitialize array:
            ovl = np.zeros((height, width, 3), dtype=np.uint8)
            patternswitcherZoomOut(ovl,0)
###            o = camera.add_overlay(bytes(memoryview(ovl)), layer=3, alpha=alphaValue)
        else:
            zoom_out()
            # reinitialize array
            gui = np.zeros((height, width, 3), dtype=np.uint8)
            creategui(gui)
            patternswitcherZoomOut(gui,1)
###            o = camera.add_overlay(bytes(memoryview(gui)), layer=3, alpha=alphaValue)
    return

def patternswitcherZoomIn(target,guitoggle):
    global o, zoomcount, ycenter
    if guitoggle == 1:
        creategui(gui)
    if globalz['zoom_x'] == globalz['zoom_xy_max']:
        print("zoom at max")

def patternswitcherZoomOut(target,guitoggle):
    global o, zoomcount, ycenter
    # first remove existing overlay:
###    if o != None:
###        camera.remove_overlay(o)
    if guitoggle == 1:
        creategui(gui)
    if globalz['zoom_x'] == globalz['zoom_xy_min']:
        print("zoom at min")

def upload_file(file_from, file_to):
    dbx = dropbox.Dropbox(token)
    f = open(file_from, 'rb')
    dbx.files_upload(f.read(), file_to)


def main():
    global buttoncounter, zoomcount, guiOn, recording, gui5, gui, o, ovl, key, gamepad, action, click, cut, filename, tl
    prev_hold = None
    try:
        initialize_camera()
#        camera.annotate_text = datetime.datetime.now().strftime("%Y-%m-%d_%H.%M.%S")
        patternswitch(gui,1)
        guivisible = 1

	#loop and filter by event code and print the mapped label
        for event in gamepad.read_loop():
#        while True:
            if event.type == ecodes.EV_ABS: 
                camera.annotate_background = None
                absevent = categorize(event) 
                if ecodes.bytype[absevent.event.type][absevent.event.code] == 'ABS_X':
                    print(absevent.event.value)
                    if(absevent.event.value > 32512):
                       print("right")
                       pan_right()
                       camera.annotate_text = "\n\n\nRIGHT"
                    elif (absevent.event.value < 32512):
                       print("left")
                       pan_left()
                       camera.annotate_text = "\n\n\nLEFT"
                if ecodes.bytype[absevent.event.type][absevent.event.code] == 'ABS_Y':
                    print(absevent.event.value)
                    if(absevent.event.value > 32512):
                   #     togglepatternZoomOut()
                   #     camera.annotate_text = "\n"+str(zoomcount)+"/10\n\nZoom Out"
                        print("down")
                        pan_down()
                        camera.annotate_text = "\n\n\nDOWN"
#                        camera.annotate_text = "\n\n\nDOWN"
                    elif (absevent.event.value < 32512):
                   #     togglepatternZoomIn()
                   #     camera.annotate_text = "\n"+str(zoomcount)+"/10\n\nZoom In"
                        print("up")
                        pan_up()
                        camera.annotate_text = "\n\n\nUP"
#                        camera.annotate_text = "\n\n\nUP"
            #camera.annotate_text = datetime.datetime.now().strftime("%Y-%m-%d %H.%M.%S")
            #if KeyboardPoller.keypressed.isSet():  
            if event.type == ecodes.EV_KEY:
               # camera.annotate_text = datetime.datetime.now().strftime("%Y-%m-%d_%H.%M.%S")
                if event.value == 1:
                    camera.annotate_background = None

                    if event.code == yBtn:
                        camera.annotate_text = "\n\n\nHold to reset zoom"
                        print("Y")
                    elif event.code == bBtn:
                        camera.annotate_text = "\n\n\nThugLife"
                        print("ThugLife")
#                        time.sleep(2)
                    elif event.code == aBtn:
                        camera.annotate_text = "\n\n\nHold to record video"

#                        if recording == 0:
#                            set_min_zoom()
#                            if togsw == 0:
#                                toggleonoff()
#                            filename = get_file_name_vid()
#                            gui5 = "RECORDING"
#                            togglepatternRecord()
#                            toggleonoff()
#                            toggleonoff()
#                            set_min_zoom()
#                            camera.start_recording(filename)
#                            print('recording')
#                            recording = 1

                        print("A")
                    elif event.code == xBtn:
       	                camera.annotate_text = "\n\n\nHold to take Picture"
                        print("X")
#                    elif event.code == up:
#                        togglepatternZoomIn()
#                        camera.annotate_text = "\n"+str(zoomcount)+"\n\nZoom In"
#                        print("up")
#                    elif event.code == down:
#                        togglepatternZoomOut()
#                        camera.annotate_text = "\n"+str(zoomcount)+"\n\nZoom Out"
#                        print("down")
#                    elif event.code == left:
#                        camera.annotate_text = "\n\n\nLEFT"
#                        print("left")
#                    elif event.code == right:
#                        camera.annotate_text = "\n\n\nRIGHT"
#                        print("right")
                    elif event.code == start:
                        camera.annotate_text = "\n\n\nSTART"
                        print("start")
                    elif event.code == select:
                        camera.annotate_text = "\n\n\nHold to toggle overlay"
                        print("select")
                    elif event.code == lTrig:
                        camera.annotate_text = "\n\n\nZoom Out"
                        togglepatternZoomOut()
                        camera.annotate_text = "\n"+str(zoomcount)+"/10\n\nZoom Out"
                        print("left bumper")
                    elif event.code == rTrig:
                        camera.annotate_text = "\n"+str(zoomcount)+"/10\n\nZoom In"
                        togglepatternZoomIn()
                        print("right bumper")

                if event.value == 0:
                    camera.annotate_text = None
#                    prev_hold = None
                    if event.code == yBtn:
                        if(prev_hold == yBtn):
                            camera.annotate_background = None
                            camera.annotate_text = "\n\n\nZoom reset"
                    if event.code == aBtn:
                        if recording == 1:
#                            subprocess.Popen(["sudo", "mpg123", "/home/pi/PiGlassv2/cut.mp3"], shell=False)
                            cut.play()
                            cut = vlc.MediaPlayer("file:///home/pi/PiGlassv2/cut.mp3")
                            #set_min_zoom()
                            camera.stop_recording()

                            photofile = "cp "+filename+" /home/pi/Pictures/"
                            print(filename)
                            subprocess.Popen(photofile, shell=True)

                            recording = 0
                            time.sleep(1)
                            gui5 = "Up/Down/Left/Right: Pan"
                            togglepatternRecord()
                            toggleonoff()
                            toggleonoff()
                            print('done recording') 
                    prev_hold = None


                if event.value == 2 and event.code != prev_hold:
                    #prev_hold = event.code
#                    camera.annotate_background = Color('green')
                    if event.code == bBtn:
                        camera.annotate_text = None
                        print("ThugLife")
                        tl = vlc.MediaPlayer("file:///home/pi/PiGlassv2/TL.mp3")
                        tl.play()
                        thuglife()
                        camera.annotate_text = "\n\n\nThugLife Done"
                        prev_hold = event.code
                    elif event.code == yBtn:
                        print("Y")
                        set_min_zoom()
                        update_zoom()
                        zoomcount = 0
                        prev_hold = event.code

                    elif event.code == aBtn:
#                        subprocess.Popen(["mpg123", "/home/pi/PiGlassv2/action.mp3"], shell=False)
                        camera.annotate_text = None
                        if recording == 0:
#                            subprocess.Popen(["sudo", "mpg123", "/home/pi/PiGlassv2/action.mp3"], shell=False)
                            action.play()
                            action = vlc.MediaPlayer("file:///home/pi/PiGlassv2/action.mp3")
                            if togsw == 0:
                                toggleonoff()
                            filename = get_file_name_vid()
                            gui5 = "RECORDING"
                            togglepatternRecord()
                            toggleonoff()
                            toggleonoff()
#                            set_min_zoom()
                            camera.start_recording(filename)
                            print('recording')
                            recording = 1
                        print("A")
                        #sys.exit(0)
                    elif event.code == xBtn:
#                        subprocess.Popen(["sudo", "mpg123", "/home/pi/PiGlassv2/click.mp3"], shell=False)
                        click.play()
                        click = vlc.MediaPlayer("file:///home/pi/PiGlassv2/click.mp3")
                        print("X")
                        camera.annotate_text = None
                        filename = get_file_name_pic()
                        camera.capture(filename, use_video_port=True)
                        photofile = "cp "+filename+" /home/pi/Pictures/"
                        print(filename)
                        subprocess.Popen(photofile, shell=True)
                        camera.annotate_text = "\n\n\nTook photo"
                        prev_hold = event.code
                 #       while gamepad.read_one() != None:
                 #           pass
                 #       time.sleep(2)
                 #       gamepad = InputDevice('/dev/input/event0')

#                    elif event.code == up:
#                        togglepatternZoomIn()
#                        camera.annotate_text = "\n"+str(zoomcount)+"\n\nZooming In"
#                        print("up")
#                    elif event.code == down:
#                        togglepatternZoomOut()
#                        camera.annotate_text = "\n"+str(zoomcount)+"\n\nZooming Out"
#                        print("down")
#                    elif event.code == left:
#                        print("left")
#                    elif event.code == right:
#                        print("right")
                    elif event.code == start:
                        print("start")
                    elif event.code == select:
                        camera.annotate_background = None
                        camera.annotate_text = None
                        prev_hold = event.code
                        print("select")
                        toggleonoff()
                        time.sleep(1)
                    elif event.code == lTrig:
#                        camera.annotate_text = "\n\n\nZoom Out"
                        togglepatternZoomOut()
                        camera.annotate_text = "\n"+str(zoomcount)+"/10\n\nZoom Out"
                        print("left bumper")
                    elif event.code == rTrig:
                        camera.annotate_text = "\n"+str(zoomcount)+"/10\n\nZoom In"
                        togglepatternZoomIn()
                        print("right bumper")


                


    finally:
        camera.close()               # clean up camera
        GPIO.cleanup()               # clean up GPIO

if __name__ == "__main__":
    main()
