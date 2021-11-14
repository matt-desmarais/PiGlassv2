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

volume = vlc.MediaPlayer("file:///home/pi/PiGlassv2/volume.mp3")
#m = aaudio.Mixer() #change later to audio hat
m = alsaaudio.Mixer('Speaker')
#m = alsaaudio.Mixer('Headphones', cardindex=0)
current_volume = m.getvolume() # Get the current Volume
#m.setvolume(80) # Set the volume to 80%.

camera = PiCamera()
camera.resolution = (1920, 1080)
camera.start_preview()
camera.rotation = -90
camera.annotate_text_size = 160
#creates object 'gamepad' to store the data
#you can call it whatever you like
gamepad = InputDevice('/dev/input/event0')

#button code variables (change to suit your device)
aBtn = 17 # W key - does nothing
bBtn = 30 # A key - does nothing 
xBtn = 31 # S key - does nothing
yBtn = 32 # D key - does nothing
start = 54  #right shift key - toggle menu next/prev display
select = 28 #enter key - select current option
lTrig = 105 #left arrow - volume down
rTrig = 106 #right arrow - volume up
up = 103 #up arrow - cycle menu up
down = 108 #down arrow - cycle menu down

prev_hold = None

#prints out device info at start
print(gamepad)

menulist = ["camera", "youtube stream", "emulationstation", "kodi", "steamlink", "disconnect controller", "seven", "eight", "nine", "ten"]
annotateString = ""
index = 0
showNextPrev = False

colorlist = ["red", "green", "blue", "orange", "yellow", "purple", "yellow", "white", "cyan"]

def animatemenu():
    annotateString = '\n\n\n'+str(menulist[index])
    for x in range(6,160):
        time.sleep(.0025)
        #camera.annotate_background = Color(random.choice(colorlist)) rainbow
        camera.annotate_background = Color('black')
        camera.annotate_text_size = x
        camera.annotate_text = annotateString.upper()
    camera.annotate_background = None

def runSelection():
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
    if(menulist[index] == 'emulationstation'):
        subprocess.Popen(["sudo", "ttyecho", "-n", "/dev/tty1", "emulationstation"], shell=False)
        print("emulationstation")
        sys.exit(0)
    if(menulist[index] == 'kodi'):
        subprocess.Popen(["kodi"], shell=False)
        sys.exit(0)
    if(menulist[index] == 'steamlink'):
        subprocess.Popen(["sudo", "-u", "pi", "steamlink"], shell=False)
        camera.close()
        sys.exit(0)
    if(menulist[index] == 'disconnect controller'):
        print("disconnect controller")
        sys.exit(0)

def menuAnnotate():
    annotateString = ''
    if(index > 0):
        annotateString += "\n"
        annotateString += menulist[index - 1]
        annotateString += "\n\n"
    else:
        annotateString += "\n\n\n"
    annotateString += str(menulist[index]).upper()
    annotateString += "\n\n"

    if(index+1 < len(menulist)):
        annotateString += menulist[index+1]
    else:
        annotateString += "\n\n"
    camera.annotate_text = annotateString


animatemenu()
#loop and filter by event code and print the mapped label
for event in gamepad.read_loop():
    if(showNextPrev):
        menuAnnotate()
    if event.type == ecodes.EV_KEY:
        if event.value == 1:
            camera.annotate_background = None
            if event.code == yBtn:
                camera.annotate_text = "\n\n\nD"
                print("D")
            elif event.code == bBtn:
                camera.annotate_text = "\n\n\nA"
                print("A")
            elif event.code == aBtn:
                camera.annotate_text = "\n\n\nW"
                print("W")
            elif event.code == xBtn:
                camera.annotate_text = "\n\n\nS"
                print("S")
            elif event.code == start:
                print("start")
                showNextPrev = not showNextPrev
                print(showNextPrev)
                if(showNextPrev == False):
                    animatemenu()
            elif event.code == select:
                camera.annotate_text = "\n\n\nRunnning Selection"
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
            elif event.code == up:
                print("up")
                if(index > 0):
                    index -= 1
                    animatemenu()
            elif event.code == down:
                print("down")
                if(index < len(menulist)-1):
                    index += 1
                    animatemenu()

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
