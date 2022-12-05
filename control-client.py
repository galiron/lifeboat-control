#!/usr/bin/env python3
import eventlet
import socketio
import os
import time
from numpy import interp

THROTTLE_INTERFACE = "can0"
THROTTLE_BITRATE = 500000
THROTTLE_INTERVAL = 0.015
THROTTLE_ID = "00000001"
THROTTLE_SELECTED = "7F"
THROTTLE_NOT_SELECTED = "7E"
THROTTLE_UNKNOWN_ONE = "033F"
THROTTLE_UNKNOWN_TWO = "010000"
THROTTLE_FORWARD_MAX = 891
THROTTLE_FORWARD_MIN = 556
THROTTLE_NEUTRAL = 444
THROTTLE_REVERSE_MIN = 334
THROTTLE_REVERSE_MAX = 128

throttle_input = 0      # input fuer Throttle, 0 bis 100

shift_input = 0         # input fuer Shift 0 = neutral, 1 = forward, 2 = reverse
shift_throttle_output = THROTTLE_NEUTRAL

select_input = 0        # input fuer Select 0 = not pressed, 1 = pressed
select_output = THROTTLE_NOT_SELECTED

# Gedankenstuetze CAN
# CAN msg ist entwickelt fuer NHK MEC KE4+ Single Motor
# msg = cansend can0 00000180#01BC033E7F010000 #cansend can0 00000180#0200000005000080

# Vorbereitung des Netzwerkinterfaces
os.system('sudo ip link set ' + THROTTLE_INTERFACE + ' type can bitrate ' + str(THROTTLE_BITRATE))
os.system('sudo ifconfig ' + THROTTLE_INTERFACE + ' up')

def send_msg():
    os.system('cansend can0 ' + THROTTLE_ID + '#' + f'{shift_throttle_output:0>4X}' + THROTTLE_UNKNOWN_ONE + select_output + THROTTLE_UNKNOWN_TWO) 
    print('\rShift&Throttle: ' + repr(shift_throttle_output) + ' Select: ' + repr(select_output))

sio = socketio.Server()
app = socketio.WSGIApp(sio, static_files={
    '/': {'content_type': 'text/html', 'filename': 'index.html'}
})

@sio.event
def connect(sid, environ):
    print('connect ', sid)

@sio.event
def hello_world(sid, data):
    print('hello_world ', data)

@sio.event
def throttle(sid, data):
    print('throttle ', data)
    throttle_input = data["value"]
    print('throttle ', throttle_input)

@sio.event
def select(sid, data):
    print('select ', data)
    select_input = data.value

@sio.event
def shift(sid, data):
    print('shift ', data)
    shift_input = data.value

@sio.event
def steer(sid):
    print('steer ', sid)

@sio.event
def disconnect(sid):
    print('disconnect ', sid)

if __name__ == '__main__':
    eventlet.wsgi.server(eventlet.listen(('127.0.0.1', 5000)), app)

    while True:
        if select_input == 1:
            select_output = THROTTLE_SELECTED
        elif select_input == 0:
            select_output = THROTTLE_NOT_SELECTED
        else:   # select_input außerhalb erlaubtem Bereich?
            select_output = THROTTLE_NOT_SELECTED   # not selected. auch throttle-neutral? tbd.

        if throttle_input >= 0 and throttle_input <= 100:   # throttle_input in erlaubtem Bereich?
            if shift_input == 0:        # NEUTRAL
                shift_throttle_output = THROTTLE_NEUTRAL
            elif shift_input == 1:      # FORWARD
                shift_throttle_output = int(interp(throttle_input,[0,100],[THROTTLE_FORWARD_MIN,THROTTLE_FORWARD_MAX]))
            elif shift_input == 2:      # REVERSE
                shift_throttle_output = int(interp(throttle_input,[0,100],[THROTTLE_REVERSE_MIN,THROTTLE_REVERSE_MAX]))
            else:                       # shift_input in erlaubtem Bereich?
                shift_throttle_output = THROTTLE_NEUTRAL    # Sonst NEUTRAL
        else:
            shift_throttle_output = THROTTLE_NEUTRAL    # Sonst NEUTRAL

        #send_msg()  # CAN Message senden

        time.sleep(THROTTLE_INTERVAL)   #warten um das Sendeintervall einzuhalten
        

