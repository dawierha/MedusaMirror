import cv2
import atexit
import numpy as np
import argparse
import RPi.GPIO as GPIO
import time
import sys
import signal
from picamera import PiCamera, mmal
from picamera.array import PiRGBArray
from picamera.mmalobj import to_rational
from multiprocessing import Process, Queue, Event
from motor import Motor

MAX_ANGLE_1 = 1500
MAX_ANGLE_2 = 900
REWIND_ANGLE_1 = 750 #Rewind angle for motor 1
REWIND_ANGLE_2 = 150   #Rewind angle for motor 2

def cleanup():
    GPIO.cleanup()

def motorThread(stop_event, calibrate_event, in_q, en_g):
    signal.signal(signal.SIGINT, signal.SIG_IGN)
    motor_1 = Motor(1, direction_1, step_1, enable_1, switch_1, MAX_ANGLE_1, REWIND_ANGLE_1, debug=debug)
    motor_2 = Motor(2, direction_2, step_2, enable_2, switch_2, MAX_ANGLE_2, REWIND_ANGLE_2, debug=debug)
    motor_1.calibrate()
    motor_2.calibrate()
    
    motor_1.add_event_detect()
    motor_2.add_event_detect()
    
    calibrate_event.set()   #Tells the camThread that the motors are ready
    direction = None
    enable = None
    while True:
        #Shuts the thread off
        if stop_event.is_set():
            break

        if in_q.qsize() > 0:
            direction = in_q.get()
        if en_q.qsize() > 0:
            enable = en_q.get()
        if enable:
            motor_1.move(direction, 0.0008)
        

def camThread(stop_event, calibrate_event, out_q, en_q):
    signal.signal(signal.SIGINT, signal.SIG_IGN)
    # Load the cascade
    face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
    if debug: print("\nLoaded cascade")    
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
        calibrate_event.wait() #Waits for the motor to finnish calibrating
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
                    if debug: print("Left half of image")
                    out_q.put(GPIO.HIGH)
                else:
                    if debug: print("Right half of image")
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

if __name__ == "__main__":
    #Arguemnts parsing
    parser = argparse.ArgumentParser(description="Mirror Pi - The mirror that\'s avoiding you")
    parser.add_argument("-s","--show", help="Shows the camera and face recognition output to the screen", action="store_true")
    parser.add_argument("-c","--nocalibrate", help="Skips the calibration of the motors", action="store_true")
    parser.add_argument("-f","--fps", help="Calculates and prints the FPS to std out", action="store_true")
    parser.add_argument("-d", "--debug", help="Prints debug statements to std out", action="count", default=0)
    args = parser.parse_args()

    #This function is called when the program is forced to close
    atexit.register(cleanup)

    #Pin setup
    direction_1 = 3 	#Green
    step_1 = 5  	    #Yellow
    enable_1 =7 	    #White
    switch_1 = 11       #White
    direction_2 = 8 	#Green
    step_2 = 10  	    #Yellow
    enable_2 = 12 	    #White
    switch_2 = 16       #White

    GPIO.setmode(GPIO.BOARD)
    GPIO.setwarnings(False)

    #Multiprocesses
    dir_q = Queue()
    en_q = Queue()
    stop_event = Event()
    calibrate_event = Event()
    debug = args.debug
    motor  = Process(target=motorThread, args=(stop_event, calibrate_event, dir_q, en_q,))
    camera = Process(target=camThread, args=(stop_event, calibrate_event, dir_q, en_q,))
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