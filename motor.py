import RPi.GPIO as GPIO
import time
import sys

class Motor():

    #cw_dirr is the clockwise direction for the motor
    def __init__(self, direction_pin, step_pin, enable_pin, switch_pin, max_angle, rewind_angle, cw_dirr=GPIO.HIGH):
        self.direction_pin = direction_pin
        self.step_pin = step_pin
        self.enable_pin = enable_pin
        self.switch_pin = switch_pin
        self.max_angle = max_angle
        self.rewind_angle = rewind_angle
        self.angle = 0
        self.cc_dirr = cw_dirr ^ 1 #Counter clockwise direction
        self.cw_dirr = cw_dirr

        GPIO.setup(enable_pin, GPIO.OUT)
        GPIO.setup(step_pin, GPIO.OUT)
        GPIO.setup(direction_pin, GPIO.OUT)
        GPIO.setup(switch_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

        #Turns off motor
        GPIO.output(enable_pin, GPIO.HIGH)
        
    def take_step(self, timeout):
        GPIO.output(self.step_pin, GPIO.LOW)
        GPIO.output(self.step_pin, GPIO.HIGH)
        time.sleep(timeout)

    def calibrate(self):
        GPIO.output(self.enable_pin, GPIO.LOW)
        GPIO.output(self.direction_pin, self.cc_dirr)
        steps=0
        while GPIO.input(self.switch_pin):
            #print(f"Calibrating... {GPIO.input(switch)}")
            self.take_step(0.008)
            sys.stdout.write(f"\rSteps: {steps}")
            sys.stdout.flush()
            steps+=1

        self.angle=0
        GPIO.output(self.direction_pin, self.cw_dirr)
        while self.angle < self.rewind_angle:
            self.take_step(0.008)
            self.angle+=1

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


if __name__ == "__main__":
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

    motor_0 = Motor(direction_1, step_1, enable_1, switch_1, 1800, 300)
    motor_0.calibrate()
    GPIO.cleanup()
