#import evdev
from evdev import InputDevice, categorize, ecodes
import alsaaudio
from picamera import PiCamera
from picamera import Color
import time
import subprocess
import sys
import os

#m = alsaaudio.Mixer() #change later to audio hat
m = alsaaudio.Mixer('Speaker')
#m = alsaaudio.Mixer('Headphones', cardindex=0)
current_volume = m.getvolume() # Get the current Volume
#m.setvolume(80) # Set the volume to 80%.

camera = PiCamera()
camera.resolution = (1920, 1080)
camera.start_preview()
camera.rotation = -90
camera.annotate_text_size = 160
camera.annotate_text = "\n\n\nLauncher"
#creates object 'gamepad' to store the data
#you can call it whatever you like
gamepad = InputDevice('/dev/input/event0')

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

prev_hold = None


#prints out device info at start
print(gamepad)

#loop and filter by event code and print the mapped label
for event in gamepad.read_loop():
    if event.type == ecodes.EV_ABS: 
        camera.annotate_background = None
        absevent = categorize(event) 
        if ecodes.bytype[absevent.event.type][absevent.event.code] == 'ABS_X':
            print(absevent.event.value)
            if(absevent.event.value > 32512):
                print("right")
                camera.annotate_text = "\n\n\nRIGHT"
            elif (absevent.event.value < 32512):
                print("left")
                camera.annotate_text = "\n\n\nLEFT"
        if ecodes.bytype[absevent.event.type][absevent.event.code] == 'ABS_Y':
            print(absevent.event.value)
            if(absevent.event.value == 32512):
                if (prev_hold < 32512):
                    subprocess.Popen(["sudo", "mpg123", "/home/pi/PiGlassv2/volume.mp3"], shell=False)
                    prev_hold = absevent.event.value
                if (prev_hold > 32512):
                    camera.annotate_text = "\n\n\nExiting"
#                    prev_hold = absevent.event.value
                    #subprocess.Popen(["ls"], shell=False)
                    sys.exit(0)
            if(absevent.event.value > 32512):
                print("down")
                camera.annotate_text = "\n\n\nDOWN"
                prev_hold = absevent.event.value
            elif (absevent.event.value < 32512):
                print("up")
                prev_hold = absevent.event.value
                camera.annotate_text = "\n\n\nTesting Volume"
#                subprocess.Popen(["sudo", "mpg123", "/home/pi/PiGlassv2/volume.mp3"], shell=False)
#                camera.annotate_text = "\n\n\nTesting Volume"



    if event.type == ecodes.EV_KEY:
        if event.value == 1:
            camera.annotate_background = None
            if event.code == yBtn:
                camera.annotate_text = "\n\n\nY: Steamlink"
#                stat = subprocess.call(["systemctl", "is-active", "bt_speaker"])
#                if(stat == 0):  # if 0 (active), print "Active"
#                     print("BT Active")
#                     camera.annotate_text = "\n\n\nBluetooth Headphones\nEnabled"
#                else:
#                     print("BT not active")
#                     camera.annotate_text = "\n\n\nBluetooth Headphones\nDisabled"
                print("Y")
            elif event.code == bBtn:
                camera.annotate_text = "\n\n\nB: Kodi"
                print("B")
            elif event.code == aBtn:
                camera.annotate_text = "\n\n\nA: EmulationStation"
                print("A")
            elif event.code == xBtn:
                camera.annotate_text = "\n\n\nX: Camera"
                print("X")
            elif event.code == start:
                camera.annotate_text = "\n\n\nYT Livestream"
                print("start")
            elif event.code == select:
                camera.annotate_text = "\n\n\nSELECT"
                print("select")
            elif event.code == lTrig:
                #camera.annotate_text = "\n\n\nHold for Volume down"
                print("left bumper")
                current_volume = m.getvolume()
                print(current_volume)
#                camera.annotate_text = "\nVol: "+str(current_volume)+"\n\nVolume Down"
                newVolume = int(current_volume[0])-1
                if(newVolume >= 75):
                    m.setvolume(newVolume)
                camera.annotate_text = "\nVol: "+str(current_volume)+"\n\nVolume Down"

            elif event.code == rTrig:
                #camera.annotate_text = "\n\n\nHold for Volume up"
                print("right bumper")
                current_volume = m.getvolume()
                print(current_volume)
#                camera.annotate_text = "\nVol: "+str(current_volume)+"\n\nVolume Up"
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
            if event.code == rTrig:
                print("right bumper")



        if event.value == 2 and event.code != prev_hold:
            camera.annotate_background = Color('green')
            if event.code == yBtn:
                subprocess.Popen(["sudo", "-u", "pi", "steamlink"], shell=False)
#
                camera.close()
#                subprocess.Popen(["export", "DISPLAY=:0"], shell=False)
                #os.system("python3 /home/pi/PiGlassv2/facedetect.py")
#                subprocess.Popen(["sudo", "ttyecho", "-n", "/dev/tty1", "python3", "/home/pi/PiGlassv2/facedetect.py"], shell=False)
                sys.exit(0)

#                prev_hold = event.code
#                stat = subprocess.call(["systemctl", "is-active", "--quiet", "bt_speaker"])
#                if(stat == 0):  # if 0 (active), print "Active"
#                    print("BT Active")
#                    subprocess.Popen(["systemctl", "stop", "/opt/bt-speaker/bt_speaker.service"], shell=False)
#                    subprocess.Popen(["/usr/bin/sudo", "systemctl", "start", "bt_speaker.service"], shell=False)
#                    camera.annotate_text = "\n\n\nBluetooth Headphones\nEnabled"
#                else:
#                    print("BT not active")
#                    #subprocess.Popen(["/usr/bin/sudo", "systemctl", "stop", "bt_speaker.service"], shell=False)
#                    subprocess.Popen(["systemctl", "start", "/opt/bt-speaker/bt_speaker.service"], shell=False)
#                    camera.annotate_text = "\n\n\nBluetooth Headphones\nDisabled"
                print("Y")
            elif event.code == bBtn:
                subprocess.Popen(["kodi"], shell=False)
                sys.exit(0)
                print("B")
            elif event.code == aBtn:
                subprocess.Popen(["sudo", "ttyecho", "-n", "/dev/tty1", "emulationstation"], shell=False)
                print("A")
                sys.exit(0)
            elif event.code == xBtn:
#                subprocess.Popen(["/usr/bin/python3", "/home/pi/PiGlassv2/PiGlassBeta-Python3.py"], shell=False)
                camera.close()
                os.system("python3 /home/pi/PiGlassv2/PiGlassBeta-Python3.py")
                print("X")
                sys.exit(0)
            elif event.code == start:
                prev_hold = event.code
                camera.close()
                subprocess.Popen(["sh", "/home/pi/PiGlassv2/syncedaudio.sh"], shell=False)
                print("start")
                sys.exit(0)
            elif event.code == select:
                print("select")
            elif event.code == lTrig:
                print("left bumper")
                current_volume = m.getvolume()
                print(current_volume)
#                camera.annotate_text = "\nVol: "+str(current_volume)+"\n\nVolume Down"
                newVolume = int(current_volume[0])-1
                if(newVolume >= 75):
                    m.setvolume(newVolume)
                camera.annotate_text = "\nVol: "+str(current_volume)+"\n\nVolume Down"
            elif event.code == rTrig:
                print("right bumper")
                current_volume = m.getvolume()
                print(current_volume)
#                camera.annotate_text = "\nVol: "+str(current_volume)+"\n\nVolume Up"
                newVolume = int(current_volume[0])+1
                if(newVolume <= 100):
                    m.setvolume(newVolume)
                camera.annotate_text = "\nVol: "+str(current_volume)+"\n\nVolume Up"

