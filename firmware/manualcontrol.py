import RPi.GPIO as GPIO
import time
import curses  # To capture key presses

# Define GPIO pins
PUL_PIN = 22  # Pulse pin
DIR_PIN = 27  # Direction pin
ENA_PIN = 17  # Optional enable pin

# Motor parameters
STEP_DELAY = 0.000001  # Delay between steps

# Setup GPIO mode
GPIO.setmode(GPIO.BCM)
GPIO.setup(PUL_PIN, GPIO.OUT)
GPIO.setup(DIR_PIN, GPIO.OUT)
GPIO.setup(ENA_PIN, GPIO.OUT)

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

    print("Press 'r' to step right, 'l' to step left, 'q' to quit.")
   
    try:
        while True:
            key = stdscr.getch()

            if key == ord('r'):
                # Step right (one step at a time)
                #print("Stepping right...")
                step_motor(GPIO.HIGH)
            elif key == ord('l'):
                # Step left (one step at a time)
                #rint("Stepping left...")
                step_motor(GPIO.LOW)
            elif key == ord('q'):
                # Stop the motor
                print("Stopping...")
                GPIO.output(ENA_PIN, GPIO.LOW)
                break

    except KeyboardInterrupt:
        print("Program interrupted")

    finally:
        print("Cleaning up GPIO...")
        GPIO.cleanup()

# Initialize curses wrapper
curses.wrapper(main)

