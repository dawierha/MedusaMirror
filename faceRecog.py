import cv2
import RPi.GPIO as GPIO
import time
import atexit
import numpy as np
import sys
import argparse
from picamera import PiCamera, mmal
from picamera.array import PiRGBArray
from picamera.mmalobj import to_rational
from multiprocessing import Process, Queue, Event
import signal


MAX_ANGLE = 3600
REWIND_ANGLE_0 = 1000 #Rewind angle for motor 0
REWIND_ANGLE_1 = 150   #Rewind angle for motor 1


def cleanup():
    GPIO.cleanup()


def calibrate(direction, step, enable, switch, rewind_angle):
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
    while steps < rewind_angle:
        GPIO.output(direction, dirr)
        GPIO.output(step, GPIO.LOW)
        GPIO.output(step, GPIO.HIGH)
        time.sleep(0.008)
        steps+=1

def cb_set_angle(channel):
    if channel == switch_1:
        pass
    elif channel == switch_2:
        pass
    print(f"Entered callback for motor {channel}")
    angle = 0


def motorThread(stop_event, in_q, en_g):
    signal.signal(signal.SIGINT, signal.SIG_IGN)
    GPIO.add_event_detect(switch_2, GPIO.FALLING, callback=cb_set_angle, bouncetime=600)
    dirr = GPIO.LOW
    enab = False
    GPIO.output(enable_1, GPIO.LOW)
    while True:
        if in_q.qsize() > 0:
            dirr = in_q.get()
        if en_q.qsize() > 0:
            enab = en_q.get()
        #if GPIO.event_detected(switch):
        #    print("endstop!!")
        #    angle = 0

        if enab and angle < 3600 and angle > 0:
            GPIO.output(direction_1, dirr)
            GPIO.output(step_1, GPIO.LOW)
            GPIO.output(step_1, GPIO.HIGH)
            time.sleep(0.0008)
            angle = angle + dirr*2-1
            print(f"Angle: {angle}")
        
        #Shuts the thread off
        if stop_event.is_set():
            break


def camThread(stop_event, out_q, en_q):
    signal.signal(signal.SIGINT, signal.SIG_IGN)
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
direction_1 = 3 	#Green
step_1 = 5  	    #Yellow
enable_1 =7 	    #White
switch_1 = 11     #White
direction_2 = 8 	#Green
step_2 = 10  	    #Yellow
enable_2 = 12 	    #White
switch_2 = 16       #White

GPIO.setmode(GPIO.BOARD)
GPIO.setup(enable_1, GPIO.OUT)
GPIO.setup(step_1, GPIO.OUT)
GPIO.setup(direction_1, GPIO.OUT)
GPIO.setup(switch_1, GPIO.IN, pull_up_down=GPIO.PUD_UP)

GPIO.output(enable_1, GPIO.HIGH)
GPIO.input(switch_1)

GPIO.setup(enable_2, GPIO.OUT)
GPIO.setup(step_2, GPIO.OUT)
GPIO.setup(direction_2, GPIO.OUT)
GPIO.setup(switch_2, GPIO.IN, pull_up_down=GPIO.PUD_UP)

GPIO.output(enable_2, GPIO.HIGH)
GPIO.input(switch_2)

GPIO.setwarnings(False)

# Load the cascade
face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
print("Loaded cascade")

#Calibrates the angle
if not args.nocalibrate:
    calibrate(direction_1, step_1, enable_1, switch_1, REWIND_ANGLE_0)
    print("\nCalibrated motor 0")
    calibrate(direction_2, step_2, enable_2, switch_2, REWIND_ANGLE_1)
    print("\nCalibrated motor 1")
angle = REWIND_ANGLE_0

#Threading
dir_q = Queue()
en_q = Queue()
stop_event = Event()
motor  = Process(target=motorThread, args=(stop_event, dir_q, en_q,))
camera = Process(target=camThread, args=(stop_event, dir_q, en_q,))
motor.start()
camera.start()


try:
    while True:
        pass
except (KeyboardInterrupt, SystemExit):
    print("\nExiting...")
    stop_event.set()
    motor.join()
    camera.join()
    cleanup()




