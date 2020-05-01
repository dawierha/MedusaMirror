import cv2
import RPi.GPIO as GPIO
import time
import atexit
import threading
import numpy as np
from queue import Queue

MAX_ANGLE = 3600

def cleanup():
    GPIO.cleanup()

def calibrate():
    dirr = GPIO.LOW
    #print(GPIO.input(switch))
    GPIO.output(enable, GPIO.LOW)
    x=0
    while GPIO.input(switch):
        #print(f"Calibrating... {GPIO.input(switch)}")
        GPIO.output(direction, dirr)
        GPIO.output(step, GPIO.LOW)
        GPIO.output(step, GPIO.HIGH)
        time.sleep(0.008)
        print(f"steps{x}")
        x+=1

    x=0
    dirr=GPIO.HIGH
    while x<30:
        GPIO.output(direction, dirr)
        GPIO.output(step, GPIO.LOW)
        GPIO.output(step, GPIO.HIGH)
        time.sleep(0.008)
        x+=1


def motorThread(in_q, en_g):
    dirr = GPIO.LOW
    angle = 0
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

        if enab:
            GPIO.output(direction, dirr)
            GPIO.output(step, GPIO.LOW)
            GPIO.output(step, GPIO.HIGH)
            time.sleep(0.0008)

def camThread(out_q, en_q):
    # To capture video from webcam. 
    cap = cv2.VideoCapture(0)
    # To use a video file as input 
    # cap = cv2.VideoCapture('filename.mp4')

    width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)

    while True:
        #time.sleep(0.1)

        # Read the frame
        _, img = cap.read()
        # Convert to grayscale
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        # Detect the faces
        faces = face_cascade.detectMultiScale(gray, 1.1, 4)
        # Draw the rectangle around each face
        enable = False
        for (x, y, w, h) in faces:
            enable = True
            cv2.rectangle(img, (x, y), (x+w, y+h), (255, 0, 0), 2)
            center = (x+w/2, y+h/2)
            if center[0] <= width/2:
                print("Left half of image")
                out_q.put(GPIO.HIGH)
            else:
                print("Right half of image")
                out_q.put(GPIO.LOW)
        en_q.put(enable)

        # Display
        #cv2.imshow('img', img)
        # Stop if escape key is pressed
        k = cv2.waitKey(30) & 0xff
        if k==27:
            break




atexit.register(cleanup)

enable =7 	#White
step = 5  	#Yellow
direction = 3 	#Green
switch = 11

GPIO.setmode(GPIO.BOARD)
GPIO.setup(enable, GPIO.OUT)
GPIO.setup(step, GPIO.OUT)
GPIO.setup(direction, GPIO.OUT)
GPIO.setup(switch, GPIO.IN, pull_up_down=GPIO.PUD_UP)

GPIO.output(enable,GPIO.HIGH)
GPIO.input(switch)


GPIO.setwarnings(False)

#GPIO.add_event_detect(switch, GPIO.RISING)

# Load the cascade
face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
print("Loaded cascade")

calibrate()
print("Calibrated")
#Threading
dir_q = Queue()
en_q = Queue()
motor  = threading.Thread(target=motorThread, args=(dir_q,en_q,))
camera = threading.Thread(target=camThread, args=(dir_q,en_q,))
motor.start()
camera.start()

dir_q.join()
en_q.join()

while True:
    pass

GPIO.cleanup()
# Release the VideoCapture object
cap.release()

