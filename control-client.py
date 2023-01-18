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
    select_input = data["value"]

@sio.event
def shift(sid, data):
    print('shift ', data)
    shift_input = data["value"]

@sio.event
def steer(sid):
    print('steer ', sid)

@sio.event
def disconnect(sid):
    print('disconnect ', sid)

def send_msg():
    shared.set('throttle', throttle_output)
    shared.set('select', select_output)
    shared.set('shift', shift_output)
    print('\rthrottle: ' + repr(throttle_output) + ' shift: ' + repr(shift_output) + ' select: ' + repr(select_output))
    time.sleep(0.100)

try:
    while True:
        char = screen.getch()
        if char == ord('x'):
#            os.system('sudo ifconfig can0 down')
            break
        elif char == ord('+'):  # faster
            if throttle_output < 100:
                throttle_output += 10
        elif char == ord('-'):  # slower
            if throttle_output > 0:
                throttle_output -= 10
        elif char == ord('q'):  # Forward
            shift_output = 1
        elif char == ord('y'):  # Reverse
            shift_output = 2
        elif char == ord('a'):  # Neutral
            shift_output = 0
        elif char == ord('s'):  # select
            select_output = 1
        else:
            select_output = 0
        send_msg()

finally:
    curses.nocbreak(); screen.keypad(0); curses.echo()
    curses.endwin()

