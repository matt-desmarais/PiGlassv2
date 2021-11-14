
from evdev import InputDevice, categorize, ecodes, KeyEvent 

gamepad = InputDevice('/dev/input/event5') 
last = {
    "ABS_X": 128,
    "ABS_Y": 128
}
for event in gamepad.read_loop(): 
    if event.type == ecodes.EV_ABS: 
        absevent = categorize(event) 
        print("type: "+str(absevent.event.type))
        print("type: "+str(absevent.event.code))
        if ecodes.bytype[absevent.event.type][absevent.event.code] == 'ABS_X':
            print(absevent.event.value)
            if(absevent.event.value > 32512):
                print("right")
            elif (absevent.event.value < 32512):
                print("left")


        if ecodes.bytype[absevent.event.type][absevent.event.code] == 'ABS_Y':
            print(absevent.event.value)
            if(absevent.event.value > 32512):
                print("down")
            elif (absevent.event.value < 32512):
                print("up")



#        if ecodes.bytype[absevent.event.type][absevent.event.code] == 'ABS_Y': 
#            last["ABS_Y"] = absevent.event.value

#        if last["ABS_X"] > 128: 
#            print('left') 
#            print(last["ABS_X"]) 
#        elif last["ABS_X"] < 127: 
#            print('right') 
#            print(last["ABS_X"] )

#        if last["ABS_Y"] > 128 : 
#            print('forward' )
#            print(last["ABS_Y"] )
#        elif last["ABS_Y"] < 127: 
#            print('reverse' )
#            print(last["ABS_Y"])
