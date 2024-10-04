import RPi.GPIO as GPIO
import time
import curses  # To capture key presses

# Define GPIO pins
PUL_PIN = 22  #
DIR_PIN = 27  # Direction pin
ENA_PIN = 17  # Optional enable
SERVO_PIN = 10  # servo PWM control pin

# Motor parameters
STEP_DELAY = 0.0001  # Delay between steps
STEPS_PER_REV = 800
STEPS_PER_DEGREE = STEPS_PER_REV / 360

# Define step counts
step = int(5 * STEPS_PER_DEGREE)

# servo
SERVO_MIN_DUTY = 2.5  # Duty cycle for 0 degrees
SERVO_MAX_DUTY = 12.5  # Duty cycle for 180 degree

# Setup GPIO mode
GPIO.setmode(GPIO.BCM)
GPIO.setup(PUL_PIN, GPIO.OUT)
GPIO.setup(DIR_PIN, GPIO.OUT)
GPIO.setup(ENA_PIN, GPIO.OUT)
GPIO.setup(SERVO_PIN, GPIO.OUT)

# Setup PWM for the servo motor (50Hz is typical for servos)
servo_pwm = GPIO.PWM(SERVO_PIN, 50)
servo_pwm.start(0)  # Initialize with 0 duty cycle (servo off)


def set_servo_angle(angle):
    duty_cycle = SERVO_MIN_DUTY + (angle / 180) * (SERVO_MAX_DUTY - SERVO_MIN_DUTY)
    servo_pwm.ChangeDutyCycle(duty_cycle)
    time.sleep(2)  # Give some time for the servo to move
    GPIO.output(SERVO_PIN, GPIO.LOW)


# Function to rotate the motor
def rotate_motor(steps, direction):
    GPIO.output(DIR_PIN, direction)  # Set direction
    GPIO.output(ENA_PIN, GPIO.HIGH)  # Enable the driver

    for _ in range(steps):
        GPIO.output(PUL_PIN, GPIO.HIGH)
        time.sleep(STEP_DELAY)
        GPIO.output(PUL_PIN, GPIO.LOW)
        time.sleep(STEP_DELAY)
    # End for
    GPIO.output(ENA_PIN, GPIO.LOW)  # Disable the driver


# Function to step the motor once
def step_motor(direction):
    GPIO.output(DIR_PIN, direction)  # Set direction
    GPIO.output(ENA_PIN, GPIO.HIGH)  # Enable the driver

    # Pulse to make one step
    GPIO.output(PUL_PIN, GPIO.HIGH)
    time.sleep(STEP_DELAY)
    GPIO.output(PUL_PIN, GPIO.LOW)
    time.sleep(STEP_DELAY)


def main(stdscr):
    # Clear screen and set up
    stdscr.clear()
    curses.cbreak()
    stdscr.keypad(True)

    try:
        while True:
            key = stdscr.getch()

            if key == ord('r'):
                # Step right (one step at a time)
                # print("Stepping right...")
                rotate_motor(step, GPIO.HIGH)
            elif key == ord('l'):
                # Step left (one step at a time)
                # rint("Stepping left...")
                rotate_motor(step, GPIO.LOW)

            elif key == ord('q'):
                # Stop the motor
                print("Stopping...")
                GPIO.output(ENA_PIN, GPIO.LOW)
                break
            if key == ord('c'):
                set_servo_angle(180)  # Close the gripper (move to 180 degrees)
            elif key == ord('o'):
                set_servo_angle(0)  # Open the gripper (move to 0 degrees)


    except KeyboardInterrupt:
        print("Program interrupted")

    finally:
        print("Cleaning up GPIO...")
        GPIO.cleanup()


# Initialize curses wrapper
curses.wrapper(main)
