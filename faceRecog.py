import cv2
import RPi.GPIO as GPIO
import time
import atexit
import threading
import numpy as np
import sys
import argparse
from picamera import PiCamera, mmal
from picamera.array import PiRGBArray
from picamera.mmalobj import to_rational
from queue import Queue


MAX_ANGLE = 3600
REWIND_ANGLE = 1000

def cleanup():
    GPIO.cleanup()

def calibrate():
    dirr = GPIO.LOW
    #print(GPIO.input(switch))
    GPIO.output(enable, GPIO.LOW)
    steps=0
    while GPIO.input(switch):
        #print(f"Calibrating... {GPIO.input(switch)}")
        GPIO.output(direction, dirr)
        GPIO.output(step, GPIO.LOW)
        GPIO.output(step, GPIO.HIGH)
        time.sleep(0.008)
        sys.stdout.write(f"\rSteps: {steps}")
        sys.stdout.flush()
        steps+=1

    steps=0
    dirr=GPIO.HIGH
    while steps < REWIND_ANGLE:
        GPIO.output(direction, dirr)
        GPIO.output(step, GPIO.LOW)
        GPIO.output(step, GPIO.HIGH)
        time.sleep(0.008)
        steps+=1

def cb_set_angle(channel):
    print("Entered callback")
    angle = 0


def motorThread(stop_event, in_q, en_g):
    GPIO.add_event_detect(switch, GPIO.FALLING, callback=cb_set_angle, bouncetime=600)
    dirr = GPIO.LOW
    enab = False
    GPIO.output(enable, GPIO.LOW)
    while True:
        if in_q.qsize() > 0:
            dirr = in_q.get()
        if en_q.qsize() > 0:
            enab = en_q.get()
        #if GPIO.event_detected(switch):
        #    print("endstop!!")
        #    angle = 0

        if enab and angle < 3600 and angle > 0:
            GPIO.output(direction, dirr)
            GPIO.output(step, GPIO.LOW)
            GPIO.output(step, GPIO.HIGH)
            time.sleep(0.0008)
        
        #Shuts the thread off
        if stop_event.is_set():
            break

def camThread(stop_event, out_q, en_q):
    #Sets up the camera
    with PiCamera() as camera:
        camera.resolution = (640, 480)
        camera.framerate = 5
        camera.exposure_mode = 'night'
        #Sets digital gain to 8.0
        mmal.mmal_port_parameter_set_rational(camera._camera.control._port, mmal.MMAL_PARAMETER_GROUP_CAMERA + 0x5A, to_rational(8.0))
        rawCapture = PiRGBArray(camera, size=(640, 480))
        

        width = camera.resolution[0]
        time_stamp_old = time.perf_counter() 
        for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
            #print(f"target fps: {camera.framerate}, dg: {camera.digital_gain}, exposure: {camera.exposure_mode}")
            # Read the frame
            img = frame.array

            # Convert to grayscale
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            
            # Detect the faces
            faces = face_cascade.detectMultiScale(gray, 1.1, 4)
            
            # Draw the rectangle around each face and detects decides if it wants to go left or right
            enable = False
            for (x, y, w, h) in faces:
                enable = True
                if args.show:
                    cv2.rectangle(img, (x, y), (x+w, y+h), (255, 0, 0), 2)
                center = (x+w/2, y+h/2)
                if center[0] <= width/2:
                    #print("Left half of image")
                    out_q.put(GPIO.HIGH)
                else:
                    #print("Right half of image")
                    out_q.put(GPIO.LOW)
            en_q.put(enable)
            
            # Display
            if args.show:
                cv2.imshow('img', img)
            # Stop if escape key is pressed
            k = cv2.waitKey(30) & 0xff
            if k==27:
                break
            
            # clear the stream in preparation for the next frame    
            rawCapture.truncate(0)
            rawCapture.seek(0)
            
            #Calculates and prints the FPS to std out
            if args.fps:
                time_stamp_new = time.perf_counter() 
                fps = 1/(time_stamp_new-time_stamp_old)
                sys.stdout.write("\rFPS: {0} ".format(round(fps, 1)))
                sys.stdout.flush()
                time_stamp_old = time_stamp_new

            #shuts the thread off
            if stop_event.is_set():
                break

#Arguemnts parsing
parser = argparse.ArgumentParser(description="Mirror Pi - The mirror that\'s avoiding you")
parser.add_argument("-s","--show", help="Shows the camera and face recognition output to the screen", action="store_true")
parser.add_argument("-c","--nocalibrate", help="Skips the calibration", action="store_true")
parser.add_argument("-f","--fps", help="Calculates and prints the FPS to std out", action="store_true")
args = parser.parse_args()

#This function is called when the program is forced to close
atexit.register(cleanup)

#Pin setup
direction = 3 	#Green
step = 5  	    #Yellow
enable =7 	    #White
switch = 11     #White

GPIO.setmode(GPIO.BOARD)
GPIO.setup(enable, GPIO.OUT)
GPIO.setup(step, GPIO.OUT)
GPIO.setup(direction, GPIO.OUT)
GPIO.setup(switch, GPIO.IN, pull_up_down=GPIO.PUD_UP)

GPIO.output(enable,GPIO.HIGH)
GPIO.input(switch)

GPIO.setwarnings(False)

# GPIO.add_event_detect(switch, GPIO.FALLING, callback=cb_set_angle, bouncetime=600)

# Load the cascade
face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
print("Loaded cascade")

#Calibrates the angle
if not args.nocalibrate:
    calibrate()
    print("Calibrated")
angle = REWIND_ANGLE

#Threading
dir_q = Queue()
en_q = Queue()
stop_event = threading.Event()
motor  = threading.Thread(target=motorThread, args=(stop_event, dir_q,en_q,))
camera = threading.Thread(target=camThread, args=(stop_event, dir_q,en_q,))
motor.start()
camera.start()

dir_q.join()
en_q.join()


try:
    while True:
        pass
except (KeyboardInterrupt, SystemExit):
    stop_event.set()
    print("\nExiting...")
    cleanup()




