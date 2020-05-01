import RPi.GPIO as GPIO
import time
import atexit

def cleanup():
    GPIO.cleanup()

atexit.register(cleanup)

enable =7       #White
step = 5        #Yellow
direction = 3   #Green
switch = 11

GPIO.setmode(GPIO.BOARD)
GPIO.setup(enable, GPIO.OUT)
GPIO.setup(step, GPIO.OUT)
GPIO.setup(direction, GPIO.OUT)
GPIO.setup(switch, GPIO.IN)

GPIO.output(enable,GPIO.LOW)
GPIO.input(switch)

GPIO.setwarnings(False)


dirr = GPIO.HIGH
x=0
while x<30:
    GPIO.output(direction, dirr)
    GPIO.output(step, GPIO.LOW)
    GPIO.output(step, GPIO.HIGH)
    time.sleep(0.008)
    x+=1


GPIO.output(enable,GPIO.LOW)

while True:
    pass
