import cv2
import numpy as np
import time

# Global list to store the scanned object centers
scanned_object_centers = []

# Function to create a homogeneous transformation matrix
def homogeneous_transform():
    """
    Creates a 4x4 homogeneous transformation matrix for a 180-degree rotation around the X-axis
    and a translation by (dx=-30, dy=45, dz=0).
    """
    T = np.array([[1, 0, 0, -25],  # X-axis translation
                  [0, -1, 0, 63],  # Y-axis translation (upside down)
                  [0, 0, -1, 0],   # Z-axis remains unchanged
                  [0, 0, 0, 1]])   # Homogeneous coordinates
    return T

# Function to apply the transformation matrix to a point
def apply_transformation(T, point):
    """
    Applies the homogeneous transformation matrix T to a 3D point.
    Args:
        T: 4x4 homogeneous transformation matrix.
        point: 3D coordinates of the point to be transformed.
    Returns:
        Transformed 3D coordinates (x, y, z).
    """
    point_homogeneous = np.array([point[0], point[1], point[2], 1])  # Convert point to homogeneous coordinates [x, y, z, 1]
    transformed_point_homogeneous = np.dot(T, point_homogeneous)      # Apply the transformation matrix to the point
    return transformed_point_homogeneous[:3]                          # Return the first three elements (x, y, z) as transformed 3D point

# Function to capture an image, detect all objects, and store their centers
def get_sorted_object_coordinates():
    """
    Captures a single video frame, detects all objects in the frame,
    calculates the X and Y coordinates of their centers, applies a transformation matrix,
    and arranges the centers in ascending order based on their distance from the origin (0, 0).
    The coordinates are stored in a global list.
    """
    global scanned_object_centers

    # Initialize video capture
    cap = cv2.VideoCapture(0)
    cap.set(16, 1280)  # Set the width of the frame
    cap.set(9, 720)  # Set the height of the frame
    cm_to_pixel = 53 / 1280.0  # Conversion factor from pixels to centimeters

    # Create the transformation matrix
    T = homogeneous_transform()

    # Capture a single frame
    _, frame = cap.read()
    gray_image = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Convert to binary image using adaptive thresholding
    binary_image = cv2.adaptiveThreshold(gray_image, 255,
                                         cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                         cv2.THRESH_BINARY_INV, 11, 2)

    # Find contours in the binary image
    contours, _ = cv2.findContours(binary_image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Clear the scanned_object_centers list before storing new coordinates
    scanned_object_centers.clear()

    for contour in contours:
        # Filter out small contours to avoid noise
        if cv2.contourArea(contour) < 1000:  # Adjust this value based on your needs
            continue

        # Get the bounding box of the contour
        x, y, w, h = cv2.boundingRect(contour)

        # Calculate the center of the bounding box
        X_Location = (x + w / 2) * cm_to_pixel  # X coordinate of the center in cm
        Y_Location = (y + h / 2) * cm_to_pixel  # Y coordinate of the center in cm
        Z_Location = 0  # Z-location is assumed to be 0 for 2D

        # Apply the transformation matrix to the detected location
        transformed_point = apply_transformation(T, (X_Location, Y_Location, Z_Location))
        #print(transformed_point[0], transformed_point[1])
        print(f"Width: {w * cm_to_pixel:.2f} cm, Height: {h * cm_to_pixel:.2f} cm")


        if(w>2 and h>2 ):
            # Append the transformed object center to the list
            scanned_object_centers.append((transformed_point[0], transformed_point[1]))

        # Draw the bounding box and center on the original image
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)  # Draw bounding box
        center = (int(transformed_point[0] / cm_to_pixel), int(transformed_point[1] / cm_to_pixel))  # Adjust for cm_to_pixel
        cv2.circle(frame, center, 5, (0, 0, 255), -1)  # Draw center point

    # Sort the scanned object centers by their distance from the origin (0, 0)
    scanned_object_centers.sort(key=lambda obj: np.sqrt(obj[0]**2 + obj[1]**2))

    # Release the camera
    cap.release()

    # Return the image with drawn objects
    return frame
    

# Main program to call the function and print the scanned object coordinates
if __name__ == "__main__":
    while True:
        # Call the function to start detecting and storing object coordinates
        image_with_objects = get_sorted_object_coordinates()

        # Print the scanned object coordinates
        print("\nScanned Object Coordinates:")
        for i, obj in enumerate(scanned_object_centers):
            print(f"Object {i + 1}: X={obj[0]:.2f} cm, Y={obj[1]:.2f} cm")

        # Display the image with detected objects
        cv2.imshow("Detected Objects", image_with_objects)
        time.sleep(0.5)
        if cv2.waitKey(1) & 0xFF == 27:  # 27 is the ASCII code for ESC
            break
    cv2.waitKey(0)  # Wait for a key press before closing the window
    cv2.destroyAllWindows()  # Clean up the window



