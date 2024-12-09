import motor_control
import kinematics
import cv2
import camera_update
import time

def main():
    # Initialize the robot's starting positions
    motor_control.initialize_position()
   

    processed_objects = []  # List to track already processed objects

    while True:
        user_input = input("Press 'c' to continue setting up the robot arm: ")
        if user_input.lower() == 'c':
            break
        else:
            print("Please press 'c' to continue.")

    while True:
        # Call get_stored_object_coordinates from camera_update.py
        image_with_objects = camera_update.get_sorted_object_coordinates()
        
        cv2.imshow("Detected Objects", image_with_objects)
        time.sleep(0.2)
        
        if image_with_objects is None or len(camera_update.scanned_object_centers) == 0:
            print("No objects detected. Waiting...")

            # Continue waiting if no objects are detected
            if cv2.waitKey(1) & 0xFF == 27:  # ESC key to exit
                print("Exiting the program.")
                break
            continue
        

        print("\nScanned Object Coordinates:")

        new_objects = []
        for obj in camera_update.scanned_object_centers:
            # Check if the object has already been processed within a small tolerance
            if not any(
                abs(obj[0] - p[0]) < 0.5 and abs(obj[1] - p[1]) < 0.5
                for p in processed_objects
            ):
                new_objects.append(obj)

        for i, obj in enumerate(new_objects):
            print(f"Object {i + 1}: X={obj[0]:.2f} cm, Y={obj[1]:.2f} cm")

            z = 1  # Default z-coordinate
            if kinematics.is_within_workspace(obj[0], obj[1], z):
                theta1, theta2, theta3 = kinematics.inverse_kinematics(obj[0], obj[1], z)
                print(f"\nCalculated joint angles:")
                print(f"Theta1 = {theta1:.2f} degrees")
                print(f"Theta2 = {theta2:.2f} degrees")
                print(f"Theta3 = {theta3:.2f} degrees")

                motor_control.go_target(theta1, theta2, theta3)

                if obj[2] == 'trash':
                    motor_control.go_trash(theta1, theta2, theta3)
                else:
                    motor_control.go_recycle(theta1, theta2, theta3)

                time.sleep(0.2)  # Delay to avoid rapid repeated movements

                # Add processed object to the list
                #processed_objects.append(obj)

        #cv2.imshow("Detected Objects", image_with_objects)

        k = cv2.waitKey(5)  # Wait for a key press
        if k == 27:  # ESC key to exit
            break
    camera_update.canned_object_centers.clear()
    cv2.destroyAllWindows()  # Clean up the window
    motor_control.clear_gpio()  # Disconnect from pigpio

if __name__ == "__main__":
    main()
