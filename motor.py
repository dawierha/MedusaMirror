import RPi.GPIO as GPIO
import time
import argparse
import sys
import atexit

class Motor():
    def __init__(self, motor_id, direction_pin, step_pin, enable_pin, switch_pin, 
                 max_angle, rewind_angle, debug=False, calibrate=True):
        self.motor_id = motor_id
        self.direction_pin = direction_pin
        self.step_pin = step_pin
        self.enable_pin = enable_pin
        self.switch_pin = switch_pin
        self.max_angle = max_angle
        self.rewind_angle = rewind_angle
        self.angle = 0
        self.cc_dirr = GPIO.LOW     #Counter clockwise direction
        self.cw_dirr = GPIO.HIGH    #Clockwise direction
        self.debug = debug

        GPIO.setup(enable_pin, GPIO.OUT)
        GPIO.setup(step_pin, GPIO.OUT)
        GPIO.setup(direction_pin, GPIO.OUT)
        GPIO.setup(switch_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

        #Turns off motor
        GPIO.output(enable_pin, GPIO.HIGH)

        #Calibrates the motor
        if calibrate: self.calibrate()

        #Adds callback event for the switch
        GPIO.add_event_detect(switch_pin, GPIO.FALLING, callback=self.callback, bouncetime=600)
        
    def take_step(self, timeout):
        GPIO.output(self.step_pin, GPIO.LOW)
        GPIO.output(self.step_pin, GPIO.HIGH)
        time.sleep(timeout)

    def move_angle(self, direction, angle, timeout):
        target_angle = self.angle + (direction*2-1)*angle
        GPIO.output(self.direction_pin, direction)
        while direction*(self.angle <= target_angle) or (direction^1)*(self.angle >= target_angle):
            if self.angle >= self.max_angle or self.angle < 0 or GPIO.event_detected(self.switch_pin):
                if self.debug: print(f"\nMotor {self.motor_id}, Angle out of bounds. Angle: {self.angle}")
                if self.angle >= self.max_angle:
                    self.edge_handling(self.cc_dirr, int(self.max_angle/2), 0.0008)
                elif not GPIO.input(self.switch_pin):
                    self.angle = 0
                    self.edge_handling(self.cw_dirr, int(self.max_angle/2), 0.0008)
                sys.stdout.flush()
                break
            self.take_step(timeout)
            self.angle += direction*2-1
            if self.debug: sys.stdout.write(f"\rMotor {self.motor_id} Angle: {self.angle}")
            sys.stdout.flush()
        if self.debug: print("")
        sys.stdout.flush()

    def calibrate(self):
        if self.debug: print(f"Calibrating Motor {self.motor_id}")
        GPIO.output(self.enable_pin, GPIO.LOW)
        GPIO.output(self.direction_pin, self.cc_dirr)
        steps=0
        while GPIO.input(self.switch_pin):
            #print(f"Calibrating... {GPIO.input(switch)}")
            self.take_step(0.008)
            if self.debug: sys.stdout.write(f"\rMotor {self.motor_id} Steps: {steps}")
            sys.stdout.flush()
            steps+=1
        if self.debug: print("")
        self.angle=0
        self.move_angle(self.cw_dirr, self.rewind_angle, 0.008)
        if self.debug: print(f"Calibration done for motor {self.motor_id}")

    def callback(self, channel):
        if self.debug: print(f"Entered callback for motor {self.motor_id}")
        GPIO.output(self.enable_pin, GPIO.HIGH)

    def edge_handling(self, direction, target_angle, timeout):
        if self.debug: print(f"Entered Edgehandling with angle: {self.angle}")
        GPIO.output(self.enable_pin, GPIO.LOW)
        GPIO.output(self.direction_pin, direction)
        while direction*(self.angle <= target_angle) or (direction^1)*(self.angle >= target_angle):
            self.take_step(timeout)
            self.angle += direction*2-1
            if self.debug: sys.stdout.write(f"\rEdge Motor {self.motor_id} Angle: {self.angle}")
        if self.debug: print("")

def cleanup():
    GPIO.cleanup()

if __name__ == "__main__":
    #Arguemnts parsing
    parser = argparse.ArgumentParser(description="Motor controll")
    parser.add_argument("-m","--motor", help="Select which motor to be turned. Can be either 0, 1, 2. Default 1. 0 selects both motors", 
                        type=int, choices=[0, 1, 2], default=1)
    parser.add_argument("-d","--direction", help="Selects which direction to turn the motor. Can be eitehr 0 or 1. Default 0.", 
                        type=int, choices=[0, 1], default=0)
    parser.add_argument("-s","--steps", help="Specifies the number of steps the motor should take. Default 30.", type=int,
                        default=30)             
    args = parser.parse_args()
    print(f"Motor: {args.motor}, direction: {args.direction}, steps: {args.steps}")

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
    
    if args.motor == 1 or args.motor == 0:
        motor_1 = Motor(1, direction_1, step_1, enable_1, switch_1, 500, 250, debug=True)
        motor_1.move_angle(args.direction, args.steps, 0.016)
    if args.motor == 2 or args.motor == 0:
        motor_2 = Motor(2, direction_2, step_2, enable_2, switch_2, 1000, 150, debug=True)
        motor_2.move_angle(args.direction, args.steps, 0.016)
    while True:
        pass
