#import evdev
from evdev import InputDevice, categorize, ecodes
import alsaaudio
import random
from picamera import PiCamera
from picamera import Color
import time
import subprocess
import sys
import os
import vlc
import datetime

volume = vlc.MediaPlayer("file:///home/pi/PiGlassv2/volume.mp3")
#m = aaudio.Mixer() #change later to audio hat
m = alsaaudio.Mixer('Speaker')
#m = alsaaudio.Mixer('Headphones', cardindex=0)
current_volume = m.getvolume() # Get the current Volume
#m.setvolume(80) # Set the volume to 80%.

def get_file_name_vid():  # new
    return datetime.datetime.now().strftime("Menu-%m-%d_%H.%M.%S.h264")

camera = PiCamera()
camera.resolution = (1920, 1080)
camera.start_preview()
camera.rotation = -90
camera.annotate_text_size = 155
filename = get_file_name_vid()
camera.start_recording(filename)

#camera.annotate_text = "\n\n\nLauncher"
#creates object 'gamepad' to store the data
#you can call it whatever you like
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

prev_hold = None

#prints out device info at start
print(gamepad)

menulist = ["camera", "take video w/audio", "youtube stream", "emulationstation", "kodi", "steamlink", "disconnect controller"]
annotateString = ""
index = 0
showNextPrev = False
rainbow = False

#colorlist = ["red", "green", "blue", "orange", "yellow", "purple", "yellow", "white", "cyan"]
colorlist = ["red", "orange", "yellow", "green", "blue", "indigo", "violet"]

def animatemenu():
    annotateString = '\n\n\n'+str(menulist[index])
    #camera.annotate_background = Color('black')
    for x in range(6,160):
        time.sleep(.0025)
        if(rainbow):
            camera.annotate_background = Color(colorlist[x%6])
#            camera.annotate_background = Color(random.choice(colorlist)) #rainbow
#        else:
#            camera.annotate_background = Color('black')
        camera.annotate_text_size = x
        camera.annotate_text = annotateString.upper()
    if(rainbow):
        camera.annotate_background = Color(colorlist[index])
    else:
        camera.annotate_background = None

def runSelection():
    camera.stop_recording()
    if(menulist[index] == 'camera'):
        camera.close()
        os.system("python3 /home/pi/PiGlassv2/PiGlassBeta-Python3.py")
        print("camera")
        sys.exit(0)
    if(menulist[index] == 'youtube stream'):
        camera.close()
        subprocess.Popen(["sh", "/home/pi/PiGlassv2/syncedaudio.sh"], shell=False)
        print("stream")
        sys.exit(0)
    if(menulist[index] == 'take video w/audio'):
        camera.close()
        subprocess.Popen(["sh", "/home/pi/PiGlassv2/videosound.sh"], shell=False)
        print("video w/audio")
        sys.exit(0)
    if(menulist[index] == 'emulationstation'):
        subprocess.Popen(["sudo", "ttyecho", "-n", "/dev/tty1", "emulationstation"], shell=False)
        print("emulationstation")
        sys.exit(0)
    if(menulist[index] == 'kodi'):
        subprocess.Popen(["sudo", "-u", "pi", "kodi"], shell=False)
        sys.exit(0)
    if(menulist[index] == 'steamlink'):
        subprocess.Popen(["sudo", "-u", "pi", "steamlink"], shell=False)
        camera.close()
        sys.exit(0)
    if(menulist[index] == 'disconnect controller'):
        print("disconnect controller")
        subprocess.Popen(["bluetoothctl", "disconnect", "98:B6:E9:EA:16:6E"], shell=False)
        sys.exit(0)

def menuAnnotate():
#    camera.annotate_text_size = 160
    annotateString = ''
    if(index > 0):
#        if(index > 1):
#            annotateString += menulist[index - 2]
        #else:
        annotateString += "\n"
        annotateString += menulist[index - 1]
        annotateString += "\n\n"
    else:
        annotateString += "\n\n\n"
    annotateString += str(menulist[index]).upper()
    annotateString += "\n\n"

    if(index+1 < len(menulist)):
        annotateString += menulist[index+1]
    annotateString += "\n"
#    if(index+2 <= len(menulist)):
#        annotateString += menulist[index+2]
    annotateString += "\n"
    camera.annotate_text = annotateString


animatemenu()
###menuAnnotate()
#loop and filter by event code and print the mapped label
for event in gamepad.read_loop():
    if(showNextPrev):
        menuAnnotate()
    #camera.annotate_text = annotateString
    if event.type == ecodes.EV_ABS: 
#        camera.annotate_background = None
        #if(showNextPrev):
        #    menuAnnotate()
        absevent = categorize(event) 
        if ecodes.bytype[absevent.event.type][absevent.event.code] == 'ABS_X':
            print(absevent.event.value)
            if(absevent.event.value > 32512):
                print("right")
                #camera.annotate_text = "\n\n\nRIGHT"
            elif (absevent.event.value < 32512):
                print("left")
                #camera.annotate_text = "\n\n\nLEFT"
        if ecodes.bytype[absevent.event.type][absevent.event.code] == 'ABS_Y':
            print(absevent.event.value)
#            if(absevent.event.value == 32512):
#                if (prev_hold < 32512):
#                    prev_hold = absevent.event.value
#                if (prev_hold > 32512):
#                    print("exit")
                    #camera.annotate_text = "\n\n\nExiting"
            if(absevent.event.value > 32512):
                #if(showNextPrev):
                #    menuAnnotate()
                print("down")
                if(index < len(menulist)-1):
                    index += 1
                    animatemenu()
                #camera.annotate_text = "\n\n\nDOWN"
                #prev_hold = absevent.event.value
            elif (absevent.event.value < 32512):
                #if(showNextPrev):
                #    menuAnnotate()
                print("up")
                if(index > 0):
                    index -= 1
                    animatemenu()
                #prev_hold = absevent.event.value
                #camera.annotate_text = "\n\n\nTesting Volume"



    if event.type == ecodes.EV_KEY:
        if event.value == 1:
            camera.annotate_background = None
            if event.code == yBtn:
                rainbow = not rainbow
                camera.annotate_text = "\n\n\nRainbow: "+str(rainbow)
                print("Y")
            elif event.code == bBtn:
                #camera.annotate_text = "\n\n\nB: Kodi"
                print("B")
            elif event.code == aBtn:
                #camera.annotate_text = "\n\n\nA: EmulationStation"
                print("A")
            elif event.code == xBtn:
                #camera.annotate_text = "\n\n\nX: Camera"
                print("X")
            elif event.code == start:
                #camera.annotate_text = "\n\n\nYT Livestream"
                print("start")
                showNextPrev = not showNextPrev
                print(showNextPrev)
                if(showNextPrev == False):
                    animatemenu()
            elif event.code == select:
                #camera.annotate_text = "\n\n\nSELECT"
                print("select")
                runSelection()
            elif event.code == lTrig:
                print("left bumper")
                current_volume = m.getvolume()
                print(current_volume)
                newVolume = int(current_volume[0])-1
                if(newVolume >= 75):
                    m.setvolume(newVolume)
                camera.annotate_text = "\nVol: "+str(current_volume)+"\n\nVolume Down"

            elif event.code == rTrig:
                print("right bumper")
                current_volume = m.getvolume()
                print(current_volume)
                newVolume = int(current_volume[0])+1
                if(newVolume <= 100):
                    m.setvolume(newVolume)
                camera.annotate_text = "\nVol: "+str(current_volume)+"\n\nVolume Up"

        if event.value == 0:
            prev_hold = None
            if event.code == start:
                print("start")
            if event.code == lTrig:
                print("left bumper")
                volume.play()
                volume = vlc.MediaPlayer("file:///home/pi/PiGlassv2/volume.mp3")
            if event.code == rTrig:
                print("right bumper")
                volume.play()
                volume = vlc.MediaPlayer("file:///home/pi/PiGlassv2/volume.mp3")

        if event.value == 2 and event.code != prev_hold:
#            camera.annotate_background = Color('green')
            if event.code == yBtn:
                print("Y")
            elif event.code == bBtn:
                print("B")
            elif event.code == aBtn:
                print("A")
            elif event.code == xBtn:
                print("X")
            elif event.code == start:
                print("start")
            elif event.code == select:
                print("select")
            elif event.code == lTrig:
                print("left bumper")
                current_volume = m.getvolume()
                print(current_volume)
                newVolume = int(current_volume[0])-1
                if(newVolume >= 75):
                    m.setvolume(newVolume)
                camera.annotate_text = "\nVol: "+str(current_volume)+"\n\nVolume Down"
            elif event.code == rTrig:
                print("right bumper")
                current_volume = m.getvolume()
                print(current_volume)
                newVolume = int(current_volume[0])+1
                if(newVolume <= 100):
                    m.setvolume(newVolume)
                camera.annotate_text = "\nVol: "+str(current_volume)+"\n\nVolume Up"
