from evdev import InputDevice, categorize, ecodes
from subprocess import call
import RPi.GPIO as GPIO
from picamera import PiCamera
from picamera import Color
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
import csv
import random

with open('funnypics.csv', newline='') as f:
    reader = csv.reader(f)
    data = list(reader)
print(data)

csvList = data #[['thuglife', "Thugs", "/home/pi/PiGlassv2/mask.png", "center"], ["brainslug", "Slugs", "mask2.png","top-right"], ["brain blender", "Blenders", "mask4.png", "top"], ['dum sticker', "Dum", "/home/pi/PiGlassv2/maskdum.png", "center"]]
index = 0
# cascade classifier object 
faceCascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
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

def animatemenu():
    annotateString = '\n\n\n'+str(csvList[index][0])
    for x in range(6,160):
        time.sleep(.0025)
        camera.annotate_text_size = x
        camera.annotate_text = annotateString.upper()

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

def randomPic():
    global camera
    camera.annotate_text = None
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
    if(len(faces) == 0):
        camera.annotate_text = "\n\n\nNo "+csvList[index][1]+" Detected"
        return
    else:
        # paste mask on each detected face in input image
        for (x,y,w,h) in faces:
            randomMask = random.randint(0,len(csvList)-1)
            maskPath = csvList[randomMask][2]
            # just to show detected faces
            cv2.rectangle(image, (x,y), (x+w, y+h), (255, 0, 0), 2)
            # open mask as PIL image
            mask = Image.open(maskPath)
            # resize mask according to detected face
            mask = mask.resize((w,h), Image.ANTIALIAS)
            # define offset for mask
            posstr = csvList[randomMask][3]
            if(posstr == "center"):
                offset = (x,y)
            if(posstr == "center-left"):
                offset = (x-int(w/3),y)
            if(posstr == "center-right"):
                offset = (x+int(w/3),y)
            if(posstr == "top-right"):
                offset = (x+int(w/3),y-int(h/1.5))
            if(posstr == "top-left"):
                offset = (x-int(w/3),y-int(h/1.5))
            if(posstr == "top"):
                offset = (x,y-int(h))
            if(posstr == "bottom-right"):
                offset = (x+int(w/3),y+int(h/4))
            if(posstr == "bottom-left"):
                offset = (x-int(w/3),y+int(h/4))
            if(posstr == "bottom"):
                offset = (x,y+int(h/4))
            if(posstr == "above"):
                offset = (x,y-int(h/.85))
            if(posstr == "below"):
                offset = (x,y+int(h/.85))
            # paste mask on background
            print(str(background))
            print(str(mask))
            print(str(offset))
            background.paste(mask, offset, mask=mask)

        # paste final thug life meme
        background.save(TLfilename)
        img = cv2.imread(TLfilename, 1)
        imgS = cv2.resize(img, (640,480))
        cv2.namedWindow(csvList[randomMask][1], cv2.WND_PROP_FULLSCREEN)
        cv2.setWindowProperty(csvList[randomMask][1], cv2.WND_PROP_FULLSCREEN,cv2.WINDOW_FULLSCREEN)
        cv2.imshow(csvList[randomMask][1], imgS)
        camera.close()
        cv2.waitKey(4000)
        camera = PiCamera()
        initialize_camera()
        animatemenu()
        cv2.destroyWindow(csvList[randomMask][1])
#        camera.annotate_text = "\n\n\n"+str(len(faces))+" "+csvList[index][1]+$
        photofile = "cp "+TLfilename+" /home/pi/Pictures/"
        print(filename)
        subprocess.Popen(photofile, shell=True)



def funnyPic():
    global camera, index
    maskPath = csvList[index][2]
    print(maskPath)
    camera.annotate_text = None
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
    if(len(faces) == 0):
        camera.annotate_text = "\n\n\nNo "+csvList[index][1]+" Detected"
        return
    else:
        # paste mask on each detected face in input image
        for (x,y,w,h) in faces:
            # just to show detected faces
            cv2.rectangle(image, (x,y), (x+w, y+h), (255, 0, 0), 2)
            # open mask as PIL image
            mask = Image.open(maskPath)
            # resize mask according to detected face
            mask = mask.resize((w,h), Image.ANTIALIAS)
            # define offset for mask
            posstr = csvList[index][3]
            if(posstr == "center"):
                offset = (x,y)
            if(posstr == "center-left"):
                offset = (x-int(w/3),y)
            if(posstr == "center-right"):
                offset = (x+int(w/3),y)
            if(posstr == "top-right"):
                offset = (x+int(w/3),y-int(h/1.5))
            if(posstr == "top-left"):
                offset = (x-int(w/3),y-int(h/1.5))
            if(posstr == "top"):
                offset = (x,y-int(h))
            if(posstr == "bottom-right"):
                offset = (x+int(w/3),y+int(h/4))
            if(posstr == "bottom-far-right"):
                offset = (x+int(w/2),y+int(h/6))
            if(posstr == "bottom-left"):
                offset = (x-int(w/3),y+int(h/4))
            if(posstr == "bottom"):
                offset = (x,y+int(h/4))
            if(posstr == "above"):
                offset = (x,y-int(h/.85))
            if(posstr == "below"):
                offset = (x,y+int(h/.85))
            # paste mask on background
            print(str(background))
            print(str(mask))
            print(str(offset))
            background.paste(mask, offset, mask=mask)

        # paste final meme
        background.save(TLfilename)
        img = cv2.imread(TLfilename, 1)
        imgS = cv2.resize(img, (640,480))
        cv2.namedWindow(csvList[index][1], cv2.WND_PROP_FULLSCREEN)
        cv2.setWindowProperty(csvList[index][1], cv2.WND_PROP_FULLSCREEN,cv2.WINDOW_FULLSCREEN)
        cv2.imshow(csvList[index][1], imgS)
        camera.close()
        cv2.waitKey(4000)
        camera = PiCamera()
        initialize_camera()
        animatemenu()
        cv2.destroyWindow(csvList[index][1])
#        camera.annotate_text = "\n\n\n"+str(len(faces))+" "+csvList[index][1]+" Found"
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
start = 313
select = 312
lTrig = 308
rTrig = 309
#prints out device info at start
print(gamepad)


def initialize_camera():
    camera.resolution = (width, height)
    camera.resolution = (width, height)
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
gui2 = 'Hold B: Take Funny Picture'
gui3 = 'Hold A: Take Random Pic'
gui4 = 'Bumpers: Zoom In/Out'
gui5 = 'Up/Down Select Overlay'

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
    global buttoncounter, zoomcount, guiOn, recording, gui5, gui, o, ovl, key, gamepad, action, click, cut, filename, tl, index
    prev_hold = None
    try:
        initialize_camera()
#        camera.annotate_text = datetime.datetime.now().strftime("%Y-%m-%d_%H.%M.%S")
        patternswitch(gui,1)
        guivisible = 1
        animatemenu()
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
                        print("down")
                        if(index < len(csvList)-1):
                            index += 1
                            animatemenu()
                        else:
                            index = 0
                            animatemenu()
                    elif (absevent.event.value < 32512):
                        print("up")
                        if(index > 0):
                            index -= 1
                            animatemenu()
                        else:
                            index = len(csvList)-1
                            animatemenu()
            #if KeyboardPoller.keypressed.isSet():  
            if event.type == ecodes.EV_KEY:
               # camera.annotate_text = datetime.datetime.now().strftime("%Y-%m-%d_%H.%M.%S")
                if event.value == 1:
                    camera.annotate_background = None

                    if event.code == yBtn:
                        camera.annotate_text = "\n\n\nHold to reset zoom"
                        print("Y")
                    elif event.code == bBtn:
                        camera.annotate_text = "\n\n\nHold for "+str(csvList[index][0])
                        print("ThugLife")
#                        time.sleep(2)
                    elif event.code == aBtn:
                        camera.annotate_text = "\n\n\nHold for random pic"
                        print("A")
                    elif event.code == xBtn:
       	                camera.annotate_text = "\n\n\nHold to take Picture"
                        print("X")
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
                    if event.code == yBtn:
                        if(prev_hold == yBtn):
                            camera.annotate_background = None
                            camera.annotate_text = "\n\n\nZoom reset"
                    if event.code == aBtn:
                        print("A button released")
                    prev_hold = None

                if event.value == 2 and event.code != prev_hold:
                    if event.code == bBtn:
                        print("ThugLife")
                        funnyPic()
                        prev_hold = event.code
                    elif event.code == yBtn:
                        print("Y")
                        set_min_zoom()
                        update_zoom()
                        zoomcount = 0
                        prev_hold = event.code

                    elif event.code == aBtn:
                        camera.annotate_text = None
                        print("A")
                        randomPic()
                        prev_hold = event.code
                    elif event.code == xBtn:
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
