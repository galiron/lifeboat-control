from pymemcache.client import base
import asyncio
import time
from threading import Thread

import socketio
import eventlet


throttle_output = 0
steering_output = 0
select_output = 0
shift_output = 0


shared = base.Client('127.0.0.1:11211')

sio = socketio.Server()
app = socketio.WSGIApp(sio, static_files={
    '/': {'content_type': 'text/html', 'filename': 'index.html'}
})

@sio.event
def connect(sid, environ):
    reset_control()
    print('connect ', sid)

@sio.event
def throttle(sid, data):
    print('throttle ', data["value"])
    global shift_output
    global throttle_output
    global select_output
    select_output = 1
    if data["value"] > 0:
        shift_output = 1    # forward
    elif data["value"] < 0:
        shift_output = 2    # reverse
    else:
        shift_output = 0    # neutral
    throttle_output = data["value"]
    print(throttle_output)

@sio.event
def select(sid, data):
    print('select ', data)
    global select_output
    select_output = data["value"]

@sio.event
def shift(sid, data):
    print('shift ', data)
    global shift_output
    shift_output = data["value"]

@sio.event
def steer(sid, data):
    print('steer ', data)
    global steering_output
    steering_output = data["value"]

@sio.event
def disconnect(sid):
    reset_control()
    print('disconnect ', sid)

@sio.event
def newUser(sid, data):
    reset_control()

def reset_control():
    global throttle_output
    global select_output
    global shift_output
    global steering_output
    steering_output = 0
    throttle_output = 0
    select_output = 0
    shift_output = 0

def send_msg():
    while True:
        global throttle_output
        global select_output
        global shift_output
        global steering_output
        shared.set('throttle', throttle_output)
        shared.set('select', select_output)
        shared.set('shift', shift_output)
        print('\rthrottle: ' + repr(throttle_output) + ' shift: ' + repr(shift_output) + ' select: ' + repr(select_output))
        time.sleep(0.1)

def start_sockets():
    eventlet.wsgi.server(eventlet.listen(('localhost', 3000)), app)


if __name__ == '__main__':
    Thread(target=send_msg, args=()).start()
    Thread(target=start_sockets, args=()).start()