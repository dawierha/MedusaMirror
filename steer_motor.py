import RPi.GPIO as GPIO
import time
import argparse
import sys
import atexit

def cleanup():
    GPIO.cleanup()

#Arguemnts parsing
parser = argparse.ArgumentParser(description="Motor controll")
parser.add_argument("-m","--motor", help="Select which motor to be turned. Can be either 0, 1, 2. Default 0.", 
                    type=int, choices=[0, 1, 2], default=0)
parser.add_argument("-d","--direction", help="Selects which direction to turn the motor. Can be eitehr 0 or 1. Default 0.", 
                    type=int, choices=[0, 1], default=0)
parser.add_argument("-s","--steps", help="Specifies the number of steps the motor should take. Default 30.", type=int,
                    default=30)
args = parser.parse_args()
print(f"Motor: {args.motor}, direction: {args.direction}, steps: {args.steps}")

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


dirr = args.motor
steps=0
while steps<args.steps:
    sys.stdout.write(f"\rSteps: {steps}")
    sys.stdout.flush()
    GPIO.output(direction, dirr)
    GPIO.output(step, GPIO.LOW)
    GPIO.output(step, GPIO.HIGH)
    time.sleep(0.008)
    steps+=1

print("")

GPIO.output(enable,GPIO.LOW)

