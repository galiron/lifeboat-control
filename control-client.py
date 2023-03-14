import os
import can
import time
import sys,tty,termios
import curses
from pymemcache.client import base
import socketio


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
    print('throttle ', data)
    if data["value"] > 0:
        shift_output = 1
    elif data["value"] < 0:
        shift_output = 2
    else:
        shift_output = 0
    throttle_output =  data["value"]

@sio.event
def select(sid, data):
    print('select ', data)
    select_output = data["value"]

@sio.event
def shift(sid, data):
    print('shift ', data)
    shift_output = data["value"]

@sio.event
def steer(sid):
    print('steer ', sid)

@sio.event
def disconnect(sid):
    reset_control()
    print('disconnect ', sid)

@sio.event
def newUser(sid):
    reset_control()

def reset_control():
    throttle_output = 0
    select_output = 0
    shift_output = 0

def send_msg():
    shared.set('throttle', throttle_output)
    shared.set('select', select_output)
    shared.set('shift', shift_output)
    print('\rthrottle: ' + repr(throttle_output) + ' shift: ' + repr(shift_output) + ' select: ' + repr(select_output))
    time.sleep(0.100)

try:
    while True:
        send_msg()

finally:
    curses.nocbreak(); screen.keypad(0); curses.echo()
    curses.endwin()

