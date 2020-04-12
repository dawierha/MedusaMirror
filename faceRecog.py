import cv2
import RPi.GPIO as GPIO
import time
import atexit
import threading
import numpy as np
from queue import Queue

def cleanup():
    GPIO.cleanup()

def motorThread(in_q):
    dirr = GPIO.LOW 
    while True:
        #print('stepping motor')
        if in_q.qsize() > 0:
           dirr = in_q.get()
        #print(dirr)
        GPIO.output(direction, dirr)
        GPIO.output(step, GPIO.LOW)
        GPIO.output(step, GPIO.HIGH)
        time.sleep(0.0008)

def camThread(out_q):
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
        for (x, y, w, h) in faces:
            cv2.rectangle(img, (x, y), (x+w, y+h), (255, 0, 0), 2)
            center = (x+w/2, y+h/2)
            if center[0] <= width/2:
                print("Left half of image")
                out_q.put(GPIO.HIGH)
            else:
                print("Right half of image")
                out_q.put(GPIO.LOW)


        # Display
        cv2.imshow('img', img)
        # Stop if escape key is pressed
        k = cv2.waitKey(30) & 0xff
        if k==27:
            break




atexit.register(cleanup)

enable =7 	#White
step = 5  	#Yellow
direction = 3 	#Green

GPIO.setmode(GPIO.BOARD)
GPIO.setup(enable, GPIO.OUT)
GPIO.setup(step, GPIO.OUT)
GPIO.setup(direction, GPIO.OUT)
GPIO.output(enable, GPIO.LOW)

GPIO.setwarnings(False)

# Load the cascade
face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
print("Loaded cascade")

#Threading
q = Queue() 
motor  = threading.Thread(target=motorThread, args=(q, ))
camera = threading.Thread(target=camThread, args=(q,))
motor.start()
camera.start()

q.join()

while True:
    pass

GPIO.cleanup()
# Release the VideoCapture object
cap.release()
