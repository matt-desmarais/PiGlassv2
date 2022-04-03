import RPi.GPIO as GPIO # Import Raspberry Pi GPIO library
import subprocess
global counter
import time
import vlc
counter = 0
global launch, kill
launch = vlc.MediaPlayer("file:///home/pi/PiGlassv2/launch.mp3")
kill = vlc.MediaPlayer("file:///home/pi/PiGlassv2/kill.mp3")
import psutil
import toml

data = toml.load("piglasscmds.toml")


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

def button_callback(channel):
    global counter, launch, kill
    counter += 1
    print("counter: "+str(counter))
    print("Mod: "+str(counter%2))
    if(counter%2 == 1):
        print("Launcher")
        #subprocess.Popen(["sudo", "mpg123", "/home/pi/PiGlassv2/launcher.mp3"], shell=False)
        launch.play()
        launch = vlc.MediaPlayer("file:///home/pi/PiGlassv2/launch.mp3")
#        time.sleep(2)
        subprocess.Popen(["python3", "/home/pi/PiGlassv2/tomlmenu.py"], shell=False)
    elif(counter%2 == 0):
#        if checkIfProcessRunning('kodi'): # or checkIfProcessRunning('retroarch'):
#            print('kodi is running')
#            subprocess.Popen(["sudo", "systemctl", "restart", "lightdm.service"], shell=False) 
#        else:
#            print('No kodi process was running')
#        if checkIfProcessRunning('retroarch'): # or checkIfProcessRunning('retroarch$
#            print('es is running')
#            subprocess.Popen(["sudo", "systemctl", "restart", "lightdm.service"], shell=False) 
#        else:
#            print('No kodi process was running')
#        subprocess.Popen(["sudo", "systemctl", "restart", "lightdm.service"], shell=False) 
        print("Killed")
        #subprocess.Popen(["sudo", "mpg123", "/home/pi/PiGlassv2/killing.mp3"], shell=False)
        kill.play()
        kill = vlc.MediaPlayer("file:///home/pi/PiGlassv2/kill.mp3")
#        killall = ['sudo', 'killall']
        for index in range(0, len(data.keys())-1):
            killall = ['sudo', 'killall']
            index_key = list(data.keys())[index]
            index_val = list(data.values())[index]
            index_prc = list(data.values())[index]['process']
            print(index_prc)
            if('python3' not in index_prc):
                killall += (list(index_prc.split(" ")))
                subprocess.Popen(killall, shell=False)
#            print(killall)
        time.sleep(3)
#        print(killall)
#        subprocess.Popen(str(killall), shell=False)
        subprocess.Popen(["sudo", "systemctl", "stop", "lightdm.service"], shell=False) 
        time.sleep(1)
        subprocess.Popen(['sudo', 'killall', 'python3'], shell=False)
#        subprocess.Popen(['sudo', 'killall', "raspivid", "ffmpeg", "steamlink", 'kodi.bin_v7', 'retroarch', 'emulationstatio', 'python3'], shell=False)
    print("Button was pushed!")

GPIO.setwarnings(False) # Ignore warning for now
GPIO.setmode(GPIO.BCM) # Use physical pin numbering
GPIO.setup(17, GPIO.IN, pull_up_down=GPIO.PUD_DOWN) # Set pin 10 to be an input pin and set initial value to be pulled low (off)

GPIO.add_event_detect(17,GPIO.RISING,callback=button_callback, bouncetime=3000) # Setup event on pin 10 rising edge

#message = input("Press enter to quit\n\n") # Run until someone presses enter

#subprocess.Popen(["sudo", "-u", "pi", "qjoypad"], shell=False) 

while True:
    time.sleep(.5)


GPIO.cleanup() # Clean up
