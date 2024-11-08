import motor_control
import kinematics
import math
import cv2
import camera_control
import time
def main():
	#Initialize the robot's starting positions
    motor_control.initialize_position()
    while True:
        user_input = input("Press 'c' to continue setting up the robot arm: ")
        if user_input.lower() == 'c':
            break
            
        else:
            print("Please press 'c' to continue.")
    while(True):
		# call get_stored_object_coordinates from camera_control.py
        image_with_objects = camera_control.get_sorted_object_coordinates()
        print("\nScanned Object Coordinates:")
        for i, obj in enumerate(camera_control.scanned_object_centers):
            print(f"Object {i + 1}: X={obj[0]:.2f} cm, Y={obj[1]:.2f} cm")
        cv2.imshow("Detected Objects", image_with_objects)
        
        for i, obj in enumerate(camera_control.scanned_object_centers):
            z=2 #default z= 0
            # Check (x,y,z) within in workspace
            if(kinematics.is_within_workspace(obj[0], obj[1], z)):
                theta1, theta2, theta3 = kinematics.inverse_kinematics(obj[0], obj[1], z)
                print(f"\nCalculated joint angles:")
                print(f"Theta1 = {theta1:.2f} degrees")
                print(f"Theta2 = {theta2:.2f} degrees")
                print(f"Theta3 = {theta3:.2f} degrees")
                motor_control.go_target(theta1, theta2, theta3)
                time.sleep(0.5)
                motor_control.go_trash(theta1, theta2, theta3)
        
                time.sleep(0.01)
		
        k = cv2.waitKey(5)  # Wait for a key press before closing the window
        if k == 27:
            break
			
    cv2.destroyAllWindows()  # Clean up the window
    motor_control.clear_gpio () # Disconnect from pigpio
	

if __name__ == "__main__":
    main()

