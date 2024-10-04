import cv2
import numpy as np

import math
import pigpio
import time
import RPi.GPIO as GPIO

# Start angles for robot arm
# Global variable
q1 = 0
q2 = 90  # move the second arm to CCW
q3 = 90  # move the third arm to CW


# Function to convert degrees to microsteps
def degrees_to_microsteps(degrees):
    microsteps_per_revolution = 6400  # 400 # Number of microsteps per revolution
    # ratio between 2 gears = 4.5
    return int((degrees / 360.0) * microsteps_per_revolution * 4.5)


# Initialize pigpio
pi = pigpio.pi()  # Connect to pigpio daemon

# Check connection
if not pi.connected:
    exit()

# Define GPIO pins for three motors
# Each motor has the structure: [PUL_PIN, DIR_PIN, ENA_PIN]
stepper_motors = [
    [5, 6, 13],  # Motor 1
    [23, 24, 25],  # Motor 2
    [22, 27, 17]  # Motor 3
]

# Set mode for the GPIO pins of each motor
for motor in stepper_motors:
    pi.set_mode(motor[0], pigpio.OUTPUT)  # PUL_PIN
    pi.set_mode(motor[1], pigpio.OUTPUT)  # DIR_PIN
    pi.set_mode(motor[2], pigpio.OUTPUT)  # ENA_PIN

# Enable all three motors
for motor in stepper_motors:
    pi.write(motor[2], 1)  # Enable motor (HIGH)


def target(motor, microsteps, delay):
    if microsteps > 0:
        pi.write(motor[1], 1)  # Rotate counter-clockwise
    else:
        pi.write(motor[1], 0)  # Rotate clockwise

    for _ in range(abs(microsteps)):
        pi.write(motor[0], 1)  # Send pulse
        time.sleep(delay)  # Hold pulse
        pi.write(motor[0], 0)  # Turn off pulse
        time.sleep(delay)  # Wait between steps


def move_to_target(angles, delay_step):
    for i in range(3):
        microsteps = degrees_to_microsteps(angles[i])
        print(f"Control motor {i + 1} with angle {angles[i]} degrees, microsteps: {microsteps}")
        target(stepper_motors[i], microsteps, delay_step)


"""
def home(motor, microsteps, delay):
    # Reverse the direction by negating microsteps
    microsteps = -microsteps

    # Set the direction for the motor based on microsteps
    if microsteps > 0:
        pi.write(motor[1], 1)  # Rotate counterclockwise
    else:
        pi.write(motor[1], 0)  # Rotate clockwise

    # Loop to send pulses from abs(microsteps) down to 0
    for _ in range(abs(microsteps), -1, -1):  # Corrected syntax
        pi.write(motor[0], 1)  # Send pulse (step)
        time.sleep(delay)       # Hold pulse
        pi.write(motor[0], 0)  # Turn off pulse
        time.sleep(delay)       # Wait before next step  
"""


def move_to_home(angles, delay_step):
    for i in range(2, -1, -1):  # Change loop to start from motor 2, 1, 0
        microsteps = degrees_to_microsteps(angles[i])
        print(f"Return to old position for motor {i + 1} with angle {angles[i]} degrees, microsteps: {-microsteps}")
        target(stepper_motors[i], -microsteps, delay_step)  # Invert microsteps


# Part I
# Global list to store the scanned object centers and their dimensions
scanned_objects = []

# Length of robot arms
L1 = 13  # Length of the base arm
L2 = 15  # Length of the second arm
L3 = 17  # Length of the third arm


# Function to create a homogeneous transformation matrix
def homogeneous_transform():
    T = np.array([[1, 0, 0, -30],
                  [0, -1, 0, 45],
                  [0, 0, -1, 0],
                  [0, 0, 0, 1]])
    return T


# Function to apply the transformation matrix to a point
def apply_transformation(T, point):
    point_homogeneous = np.array([point[0], point[1], point[2], 1])
    transformed_point_homogeneous = np.dot(T, point_homogeneous)
    return transformed_point_homogeneous[:3]


# Function to check if the point is within the workspace using the given equation
def is_within_workspace(L1, L2, L3, x, y, z):
    # Calculate the distance squared between the base and the target point
    distance_squared = x ** 2 + y ** 2 + (z - L1) ** 2

    # Calculate the minimum and maximum reach squared
    min_reach_squared = (L2 - L3) ** 2
    max_reach_squared = (L2 + L3) ** 2

    # Check if the point is within the range
    return min_reach_squared <= distance_squared <= max_reach_squared


def inverse_kinematics(x, y, z):
    # Calculate angle theta1
    theta1 = math.atan2(y, x)

    # Calculate the distance from the origin to the projection of the end-effector on the XY plane
    d = math.sqrt(x ** 2 + y ** 2)

    # Calculate the distance from the origin to the end-effector on the Z plane
    r = math.sqrt(d ** 2 + (z - L1) ** 2)

    # Check the condition for the existence of a solution
    if r > (L2 + L3) or r < abs(L2 - L3):
        raise ValueError(f"The coordinates cannot be reached with the current robot structure. (x= {x}, y = {y})")

    # Calculate the angle between segment L2 and the vertical axis from the origin to the end-effector
    phi = math.atan2(z - L1, d)

    # Use the cosine law to calculate theta2 and theta3
    cos_theta2 = (L2 ** 2 + r ** 2 - L3 ** 2) / (2 * L2 * r)
    if not (-1 <= cos_theta2 <= 1):
        raise ValueError(f"Invalid angle calculation for theta2. (x= {x}, y = {y})")

    theta2 = phi + math.acos(cos_theta2)

    cos_theta3 = (L2 ** 2 + L3 ** 2 - r ** 2) / (2 * L2 * L3)
    if not (-1 <= cos_theta3 <= 1):
        raise ValueError(f"Invalid angle calculation for theta3. (x= {x}, y = {y})")

    theta3 = math.acos(cos_theta3) - math.pi

    # Convert angles from radians to degrees
    theta1 = math.degrees(theta1)
    theta2 = math.degrees(theta2) - q2
    theta3 = math.degrees(theta3) + q3

    if (theta2 > 45):
        raise ValueError(f"The theta 2 too big. (x= {x}, y = {y})")
    if (theta2 < -90):
        raise ValueError(f"The theta 2 too small. (x= {x}, y = {y})")
    if (theta3 > 90):
        raise ValueError(f"The theta3 too big. (x= {x}, y = {y})")
    if (theta3 < -90):
        raise ValueError(f"The theta3 too small. (x= {x}, y = {y})")

    return theta1, theta2, theta3


# Function to capture an image, detect all objects, and store their centers and dimensions
def get_sorted_object_coordinates():
    global scanned_objects

    # Initialize video capture
    cap = cv2.VideoCapture(0)  # Use V4L2
    time.sleep(1)
    if not cap.isOpened():
        print("Cannot open camera.")
        return None

    cap.set(3, 640)  # Set the width of the frame
    cap.set(4, 480)  # Set the height of the frame
    cm_to_pixel = 60 / 640.0  # Conversion factor from pixels to centimeters

    T = homogeneous_transform()

    _, frame = cap.read()
    if frame is None:
        print("Error: Could not capture frame.")
        cap.release()
        return None

    gray_image = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    binary_image = cv2.adaptiveThreshold(gray_image, 255,
                                         cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                         cv2.THRESH_BINARY_INV, 11, 2)

    contours, _ = cv2.findContours(binary_image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Clear the scanned_objects list before storing new coordinates and dimensions
    scanned_objects.clear()

    for contour in contours:
        if cv2.contourArea(contour) < 500:
            continue

        # Get the bounding box of the contour
        x, y, w, h = cv2.boundingRect(contour)

        # Calculate the center of the bounding box in cm
        X_Location = (x + w / 2) * cm_to_pixel
        Y_Location = (y + h / 2) * cm_to_pixel
        Z_Location = 0

        # Apply the transformation matrix to the detected location
        transformed_point = apply_transformation(T, (X_Location, Y_Location, Z_Location))

        # Store the transformed object center and its width and height
        width_cm = w * cm_to_pixel  # Convert width to cm
        height_cm = h * cm_to_pixel  # Convert height to cm

        scanned_objects.append({
            "center": (transformed_point[0], transformed_point[1]),
            "width": width_cm,
            "height": height_cm
        })

        # Draw bounding box and center for debugging
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
        center = (int(transformed_point[0] / cm_to_pixel), int(transformed_point[1] / cm_to_pixel))
        cv2.circle(frame, center, 5, (0, 0, 255), -1)

        # Display details (width, height, distance) on the screen
        distance = np.sqrt(transformed_point[0] ** 2 + transformed_point[1] ** 2)
        details = f"W: {width_cm:.2f}cm, H: {height_cm:.2f}cm, D: {distance:.2f}cm"
        cv2.putText(frame, details, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)

    # Sort the scanned objects by their distance from the origin (0, 0)
    scanned_objects.sort(key=lambda obj: np.sqrt(obj["center"][0] ** 2 + obj["center"][1] ** 2))
    cap.release()
    # cv2.imshow("Detected Objects with Details", frame)
    return frame


# Main program
if __name__ == "__main__":
    while True:  # Start an infinite loop
        image_with_objects = get_sorted_object_coordinates()

        delay = 0.001
        delay_step = 0.0001
        if image_with_objects is not None:
            print("\nScanned Object Information (Center, Width, Height, Distance):")
            cv2.imshow("Detected Objects with Details", image_with_objects)
            success = cv2.imwrite("output_image.jpg", image_with_objects)
            if not success:
                print("Failed to save image.")

            for i, obj in enumerate(scanned_objects):
                center_x, center_y = obj["center"]
                z = 0  # Assuming Z=0 for this example

                # Attempt to calculate inverse kinematics
                try:
                    angles = inverse_kinematics(center_x, center_y, z)
                    if angles:
                        print(f"Inverse Kinematics angles for Object {i + 1}: {angles}")
                        theta1, theta2, theta3 = angles
                        print(f"Object {i + 1}:")
                        print(f"  X={center_x:.2f} cm, Y={center_y:.2f} cm, Z={z:.2f} cm")
                        print(
                            f"  Inverse Kinematics angles: theta1={theta1:.2f}°, theta2={theta2:.2f}°, theta3={theta3:.2f}°")

                        # move_to_target(angles, delay_step)
                        move_to_target(angles, delay_step)
                        # close_gripper()
                        # Move back to the starting position
                        move_to_home(angles, delay_step)
                        # open_gripper()
                        time.sleep(0.001)


                    else:
                        print(
                            f"Object {i + 1} at X={center_x:.2f} cm, Y={center_y:.2f} cm, Z={z:.2f} cm is out of bounds or IK failed.")

                except ValueError as e:
                    print(f"Error calculating IK for Object {i + 1}: {str(e)}")

            # Display the processed frame

            # cv2.imshow("Detected Objects with Details", image_with_objects)
            time.sleep(0.01)
            # cv2.destroyAllWindows()
            # Check for the ESC key to exit
            if cv2.waitKey(1) & 0xFF == 27:  # 27 is the ASCII code for ESC
                break

    # Clean up
    cv2.destroyAllWindows()
