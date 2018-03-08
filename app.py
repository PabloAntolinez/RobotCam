#!/usr/bin/env python
import hcsr04 as ultra
import numpy as np
from flask import Flask, render_template, Response
import piconzero as pz
import time

# Raspberry Pi camera module (requires picamera package)
from camera_pi import Camera

angle = 91
light = 0

def down():
        global angle
        angle += 5
        angle = min(145,angle)
        pz.setOutput(0,angle)
def up():
        global angle
        angle -= 5
        angle = max(40,angle)
        pz.setOutput(0,angle)
def center():
        global angle
        angle = 90
        pz.setOutput(0,angle)
        
def toggleLight():
        global light
        light = (light+1)%4
        if (light == 0):
                pz.setAllPixels(0,0,0)
        elif (light == 1) :
                pz.setAllPixels(255,255,255)
        elif (light == 2) :
                pz.setAllPixels(0,255,0)
        elif (light == 3) :
                pz.setAllPixels(255,0,0)
				
pz.init()
pz.setOutputConfig(0,2)
pz.setOutputConfig(5,3)
pz.setBrightness(100)
pz.setOutput(0,angle)
ultra.init()

app = Flask(__name__)

@app.route('/')
def index():
    """Video streaming home page."""
    return render_template('index.html')


def gen(camera):
    """Video streaming generator function."""
    while True:
		frame = camera.get_frame()
		yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')


@app.route('/video_feed')
def video_feed():
    """Video streaming route. Put this in the src attribute of an img tag."""
    return Response(gen(Camera()),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

#recieve which pin to change from the button press on index.html
#each button returns a number that triggers a command in this function
#
#Uses methods from motors.py to send commands to the GPIO to operate the motors
@app.route('/robot/<state>', methods=['POST'])
def update_robot(state=None):
	if state == "Forward" :
		pz.forward(100)
	elif state == "Reverse" :
		pz.reverse(100)
	elif state == "Left" :
		pz.spinLeft(50)
	elif state == "Right" :
		pz.spinRight(50)
	elif state == "Stop" :
		pz.stop()
	elif state == "Up":
		up()
	elif state == "Down":
		down()
	elif state == "Light":
		toggleLight()
	elif state == "Center":
		center()
	else :
		print (" no command ")
	return('',204)

if __name__ == '__main__':
    for i in range(4):
		pz.setAllPixels(255,255,255)
		time.sleep(0.05)
		pz.setAllPixels(0,0,0)
		time.sleep(0.05)
    app.run(host='0.0.0.0', port = 8000, threaded=True)


