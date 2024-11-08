import pigpio
import time


#SERVO_GPIO = 18  # Servo for the third joint
GRIPPER_SERVO_GPIO = 19  # Servo for the gripper

# GPIO pins for first stepper
PUL_PIN_1 = 22
DIR_PIN_1 = 27
ENA_PIN_1 = 17
gear_ratio1 = 90/20 # =4.5

# GPIO pins for second stepper
PUL_PIN_2 = 23
DIR_PIN_2 = 24
ENA_PIN_2 = 25
gear_ratio2 = 4.5

# GPIO pins for third stepper
#examples
PUL_PIN_3 = 2
DIR_PIN_3 = 3
ENA_PIN_3 = 4
gear_ratio3 = 90/25

# Constants
delay = 0.00001
microsteps_per_revolution = 6400  # Microsteps per full revolution


gripper_position = 0

# Initialize pigpio
pi = pigpio.pi()  # Connect to pigpio daemon
if not pi.connected:
    exit()

def initialize_position():
    """
    Set initial positions: open the gripper and set the main servo motor to 90 degrees.
    """
    
    
    global gripper_position
    gripper_position = 0
    open_gripper()          # Open the gripper
    
    pi.write(ENA_PIN_1, 1)  # Turn on stepper motor 1
    pi.write(ENA_PIN_2, 1)  # Turn on stepper motor 2
    pi.write(ENA_PIN_3, 1)  # Turn on stepper motor 3
    
def clear_gpio():
    pi.set_servo_pulsewidth(GRIPPER_SERVO_GPIO, 0)  # Turn off the gripper servo
    pi.write(ENA_PIN_1, 0)  # Turn off stepper motor 1
    pi.write(ENA_PIN_2, 0)  # Turn off stepper motor 2
    pi.write(ENA_PIN_3,0)
    pi.stop()  # Disconnect from pigpio
  
def move_servo_smoothly(target_position, step_duration):
    # Initial position for gripper
    global gripper_position
    pi.set_servo_pulsewidth(GRIPPER_SERVO_GPIO, int(500 + (gripper_position / 270.0) * 2000))  # 
    
    while gripper_position != target_position:
        if gripper_position < target_position:
            gripper_position += 1  # Increase angle
        else:
            gripper_position -= 1  # Decrease angle
        
        pulse_width = int(500 + (gripper_position / 270.0) * 2000)
        pi.set_servo_pulsewidth(GRIPPER_SERVO_GPIO, pulse_width)
        
        time.sleep(step_duration)  # delay

def move_gripper(position):
    pulse_width = int(500 + (position / 180.0) * 2000)
    pi.set_servo_pulsewidth(GRIPPER_SERVO_GPIO, pulse_width)

def open_gripper():
    move_servo_smoothly(0,0.02)

def close_gripper():
    move_servo_smoothly(90,0.02)

def degrees_to_microsteps(degrees, gear_ratio):
    return int((degrees / 360.0) * microsteps_per_revolution * gear_ratio)


def step_motor(pul_pin, dir_pin, microsteps, delay):
    pi.write(dir_pin, 1 if microsteps > 0 else 0)
    for _ in range(abs(microsteps)):
        pi.write(pul_pin, 1)
        time.sleep(delay)
        pi.write(pul_pin, 0)
        time.sleep(delay)


# Moving to target
def go_target(theta1, theta2, theta3):
    print("Moving to target...")
    
    # Move first arm
    microsteps1 = degrees_to_microsteps(theta1, gear_ratio1)
    step_motor(PUL_PIN_1, DIR_PIN_1, microsteps1, delay)
    
    # Move third arm
    microsteps3=degrees_to_microsteps(theta3, gear_ratio3)
    step_motor(PUL_PIN_3, DIR_PIN_3, microsteps3,delay)
    
    # Move second arm
    microsteps2 = degrees_to_microsteps(theta2, gear_ratio2)
    step_motor(PUL_PIN_2, DIR_PIN_2, microsteps2, delay)
    
    print("Pick up the object")
    # Close gripper
    close_gripper()
    time.sleep(0.5)
# Moving to trash and then go home

def go_trash(theta1, theta2, theta3):
    print("Moving to trash and returning home...")

    # Move second arm up to 45 degrees
    adjusted_theta2 = -theta2 - 45
    microsteps2 = degrees_to_microsteps(adjusted_theta2, gear_ratio2)
    step_motor(PUL_PIN_2, DIR_PIN_2, microsteps2, delay)

    # Move first arm, go to trash
    adjusted_theta1 = -theta1 - 15
    microsteps1 = degrees_to_microsteps(adjusted_theta1, gear_ratio1)
    step_motor(PUL_PIN_1, DIR_PIN_1, microsteps1, delay)
    
    print("Drop off the object")
    # Open gripper
    open_gripper()
    time.sleep(1)
    
    print("returning to home")
    # Return arms to initial position
    microsteps1_back = degrees_to_microsteps(15,gear_ratio1)
    step_motor(PUL_PIN_1, DIR_PIN_1, microsteps1_back, delay)

    microsteps2_back = degrees_to_microsteps(45, gear_ratio2)
    step_motor(PUL_PIN_2, DIR_PIN_2, microsteps2_back, delay)
    
    microsteps3 =degrees_to_microsteps(-theta3, gear_ratio3)
    step_motor(PUL_PIN_3, DIR_PIN_3, microsteps3,delay)
"""   
try:
    initialize_position()
    while True:
        user_input = input("Enter angles (theta1, theta2, theta3) (or 'q' to quit): ")
        if user_input.lower() == 'q':
            break
        theta1, theta2, theta3 = map(float, user_input.split(','))  # Split string into list
        
        # Move first arm
        microsteps1 = degrees_to_microsteps(theta1, gear_ratio1)
        step_motor(PUL_PIN_1, DIR_PIN_1, microsteps1, delay)
        time.sleep(2)
    
        # Move second arm
        microsteps2 = degrees_to_microsteps(theta2, gear_ratio2)
        step_motor(PUL_PIN_2, DIR_PIN_2, microsteps2, delay)
        
        #close the gripper
        close_gripper()
        time.sleep(2)
	
	
finally:
	clear_gpio()

"""
