import time
import curses
from pymemcache.client import base
import socketio
import eventlet


throttle_output = 0
select_output = 0
shift_output = 0

screen = curses.initscr()
curses.noecho()
curses.cbreak()
screen.keypad(True)
screen.nodelay(True)
screen.scrollok(False)

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
    if data["value"] > 0:
        shift_output = 1
    elif data["value"] < 0:
        shift_output = 2
    else:
        shift_output = 0
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
    print('steer ', sid)

@sio.event
def disconnect(sid):
    reset_control()
    print('disconnect ', sid)

@sio.event
def newUser(sid, data):
    reset_control()

@sio.event
def poke(sid, data):
    send_msg()

def reset_control():
    global throttle_output
    global select_output
    global shift_output
    throttle_output = 0
    select_output = 0
    shift_output = 0

def send_msg():
    shared.set('throttle', throttle_output)
    shared.set('select', select_output)
    shared.set('shift', shift_output)
    print('\rthrottle: ' + repr(throttle_output) + ' shift: ' + repr(shift_output) + ' select: ' + repr(select_output))


if __name__ == '__main__':
    eventlet.wsgi.server(eventlet.listen(('localhost', 3010)), app)

