import pigpio
import time
import math

# Global variable for starting angles of robot arm
q1 = 0
q2 = 90  # Move the second arm to CCW
q3 = 90  # Move the third arm to CW


# Function to convert degrees to microsteps
def degrees_to_microsteps(degrees):
    microsteps_per_revolution = 6400  # Number of microsteps per revolution
    return int((degrees / 360.0) * microsteps_per_revolution)  # ratio


# Function to initialize pigpio and setup motors
def setup_motors(stepper_motors):
    # Initialize pigpio
    pi = pigpio.pi()  # Connect to pigpio daemon

    # Check connection
    if not pi.connected:
        print("Failed to connect to pigpio daemon.")
        exit()

    # Set GPIO mode for the pins of each motor
    for motor in stepper_motors:
        pi.set_mode(motor[0], pigpio.OUTPUT)  # PUL_PIN
        pi.set_mode(motor[1], pigpio.OUTPUT)  # DIR_PIN
        pi.set_mode(motor[2], pigpio.OUTPUT)  # ENA_PIN

    # Enable all three motors
    for motor in stepper_motors:
        pi.write(motor[2], 1)  # Enable motor (HIGH)

    return pi


# Function to control motor with PWM
def step_motor(pi, motor, microsteps, delay):
    if microsteps > 0:
        pi.write(motor[1], 1)  # Rotate counterclockwise
    else:
        pi.write(motor[1], 0)  # Rotate clockwise

    for _ in range(abs(microsteps)):
        pi.write(motor[0], 1)  # Send pulse
        time.sleep(delay)  # Pulse hold time
        pi.write(motor[0], 0)  # Turn off pulse
        time.sleep(delay)  # Delay between steps


# Function for Forward Kinematics
def forward_kinematics(L1, L2, L3, theta1, theta2, theta3):
    # Convert angles from degrees to radians
    theta1 = math.radians(theta1)
    theta2 = math.radians(theta2)
    theta3 = math.radians(theta3)

    # Calculate coordinates x, y, z
    x = L2 * math.cos(theta1) * math.cos(theta2) + L3 * math.cos(theta1) * math.cos(theta2 + theta3)
    y = L2 * math.sin(theta1) * math.cos(theta2) + L3 * math.sin(theta1) * math.cos(theta2 + theta3)
    z = L1 + L2 * math.sin(theta2) + L3 * math.sin(theta2 + theta3)

    return x, y, z


# Function for Inverse Kinematics
def inverse_kinematics(L1, L2, L3, x, y, z):
    # Calculate angle theta1
    theta1 = math.atan2(y, x)

    # Calculate the distance from the origin to the projection of the end-effector on the XY plane
    d = math.sqrt(x ** 2 + y ** 2)

    # Calculate the distance from the origin to the end-effector on the Z plane
    r = math.sqrt(d ** 2 + (z - L1) ** 2)

    # Check the condition for the existence of a solution
    if r > (L2 + L3) or r < abs(L2 - L3):
        raise ValueError("The coordinates cannot be reached with the current robot structure.")

    # Calculate the angle between segment L2 and the vertical axis from the origin to the end-effector
    phi = math.atan2(z - L1, d)

    # Use the cosine law to calculate theta2 and theta3
    cos_theta2 = (L2 ** 2 + r ** 2 - L3 ** 2) / (2 * L2 * r)
    if not (-1 <= cos_theta2 <= 1):
        raise ValueError("Invalid angle calculation for theta2.")

    theta2 = phi + math.acos(cos_theta2)

    cos_theta3 = (L2 ** 2 + L3 ** 2 - r ** 2) / (2 * L2 * L3)
    if not (-1 <= cos_theta3 <= 1):
        raise ValueError("Invalid angle calculation for theta3.")

    theta3 = math.acos(cos_theta3) - math.pi

    # Convert angles from radians to degrees
    theta1 = math.degrees(theta1)
    theta2 = math.degrees(theta2) - q2
    theta3 = math.degrees(theta3) + q3

    return theta1, theta2, theta3


# Function to check if the point is within the workspace
def is_within_workspace(L1, L2, L3, x, y, z):
    # Calculate the distance squared between the base and the target point
    distance_squared = x ** 2 + y ** 2 + (z - L1) ** 2

    # Calculate the minimum and maximum reach squared
    min_reach_squared = (L2 - L3) ** 2
    max_reach_squared = (L2 + L3) ** 2

    # Check if the point is within the range
    return min_reach_squared <= distance_squared <= max_reach_squared


# Main function for the program
def main():
    # Define the lengths of the arms
    L1 = 14
    L2 = 13
    L3 = 17

    # Define GPIO pins for three motors
    # Each motor has the structure: [PUL_PIN, DIR_PIN, ENA_PIN]
    stepper_motors = [
        [22, 27, 17],  # Motor 1
        [23, 24, 25],  # Motor 2
        [5, 6, 13]  # Motor 3
    ]

    pi = setup_motors(stepper_motors)  # Setup motors and return pi instance
    delay_step = 0.001  # Change this value to adjust speed

    # Main loop to get user input
    try:
        while True:
            user_input = input("Enter x, y, z coordinates (or 'q' to quit): ")

            if user_input.lower() == 'q':
                break  # Exit the program if user enters 'q'

            try:
                # Split input into coordinates
                coords = list(map(float, user_input.split()))  # Split by spaces

                if len(coords) != 3:
                    print("Please enter exactly 3 coordinates.")
                    continue

                # Extract x, y, z coordinates
                x, y, z = coords

                # Check if the target position is within the robot's workspace
                if is_within_workspace(L1, L2, L3, x, y, z):
                    # Calculate joint angles using inverse kinematics
                    theta1, theta2, theta3 = inverse_kinematics(L1, L2, L3, x, y, z)
                    print(f"\nCalculated joint angles:")
                    print(f"Theta1 = {theta1:.2f} degrees")
                    print(f"Theta2 = {theta2:.2f} degrees")
                    print(f"Theta3 = {theta3:.2f} degrees")

                    # Control motors based on calculated angles
                    for i in range(3):
                        microsteps = degrees_to_microsteps([theta1, theta2, theta3][i])
                        print(
                            f"Controlling motor {i + 1} with angle {theta1 if i == 0 else theta2 if i == 1 else theta3:.2f} degrees, microsteps: {microsteps}")
                        step_motor(pi, stepper_motors[i], microsteps, delay_step)

                else:
                    print("The point is outside the robot's reachable workspace.")

            except ValueError:
                print("Please enter valid coordinates or 'q' to quit.")

    finally:
        # Disable all motors and cleanup
        for motor in stepper_motors:
            pi.write(motor[2], 0)  # Disable motor (LOW)

        pi.stop()  # Disconnect from pigpio


if __name__ == "__main__":
    main()
