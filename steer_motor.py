import RPi.GPIO as GPIO
import time
import argparse
import sys
import atexit

def cleanup():
    GPIO.cleanup()

#Arguemnts parsing
parser = argparse.ArgumentParser(description="Motor controll")
parser.add_argument("-m","--motor", help="Select which motor to be turned. Can be either 0, 1, 2. Default 0. 2 selects both motors", 
                    type=int, choices=[0, 1, 2], default=0)
parser.add_argument("-d","--direction", help="Selects which direction to turn the motor. Can be eitehr 0 or 1. Default 0.", 
                    type=int, choices=[0, 1], default=0)
parser.add_argument("-s","--steps", help="Specifies the number of steps the motor should take. Default 30.", type=int,
                    default=30)
args = parser.parse_args()
print(f"Motor: {args.motor}, direction: {args.direction}, steps: {args.steps}")

atexit.register(cleanup)

enable_1 =7         #White
step_1 = 5          #Yellow
direction_1 = 3     #Green
switch_1 = 11       #White
direction_2 = 8	    #Green
step_2 = 10     	#Yellow
enable_2 = 12   	#White
switch_2 = 16   	#White

GPIO.setmode(GPIO.BOARD)
#First Motor
GPIO.setup(enable_1, GPIO.OUT)
GPIO.setup(step_1, GPIO.OUT)
GPIO.setup(direction_1, GPIO.OUT)
GPIO.setup(switch_1, GPIO.IN)

GPIO.output(enable_1,GPIO.LOW)
GPIO.input(switch_1)

#Second Motor
GPIO.setup(enable_2, GPIO.OUT)
GPIO.setup(step_2, GPIO.OUT)
GPIO.setup(direction_2, GPIO.OUT)
GPIO.setup(switch_2, GPIO.IN)

GPIO.output(enable_2,GPIO.LOW)
GPIO.input(switch_2)


GPIO.setwarnings(False)

steps=0
while steps<=args.steps:
    sys.stdout.write(f"\rSteps: {steps}")
    sys.stdout.flush()
    if args.motor == 0 or args.motor == 2:
        GPIO.output(direction_1, args.direction)
        GPIO.output(step_1, GPIO.LOW)
        GPIO.output(step_1, GPIO.HIGH)
    if args.motor == 1 or args.motor == 2:
        GPIO.output(direction_2, args.direction)
        GPIO.output(step_2, GPIO.LOW)
        GPIO.output(step_2, GPIO.HIGH)
    time.sleep(0.016)
    steps+=1

print("")

GPIO.output(enable_1, GPIO.LOW)
GPIO.output(enable_2, GPIO.LOW)

