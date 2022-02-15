#!/user/bin/env python
#

import os
import json
import time 
import datetime
import picamera
from gpiozero import MotionSensor

#
# Start up
#
time.sleep(2)
print ("Ready...")

#
# Get Janus config settings from janus_config.json file
# and be sure the json file is in the same folder as this
#
with open('janus_config.json') as json_file:
    config = json.load(json_file)

#
# Setup GPIO config
#
PIR_sensor = MotionSensor(config['configuration']['GPIO_input'])

#
# Set
#
def get_file_name():
    return config['configuration']['imagefile_path'] + config['configuration']['name'] + datetime.datetime.now().strftime("%Y-%m-%d_%H:%M:%S" + '.jpg')

#
# Function to run when motion is detected
#
def MotionDetected():
    print("Motion detected")

    with picamera.PiCamera(resolution=("720p"), framerate=30) as camera:
        camera.capture(get_file_name())

try:
    while True:
        if PIR_sensor.motion_detected:
            print ("Motion!")
            MotionDetected()
            time.sleep(0.1)

except KeyboardInterrupt:
    print ("Quiting...")
