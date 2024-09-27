import cv2
import numpy as np


# Create a homogeneous transformation matrix for a 180-degree rotation around the X-axis
def homogeneous_transform():
    return np.array([[1, 0, 0, -30],
                     [0, -1, 0, 45],
                     [0, 0, -1, 0],
                     [0, 0, 0, 1]])


# Apply transformation matrix to a 3D point
def apply_transformation(T, point):
    point_homogeneous = np.append(point, 1)  # Convert to homogeneous coordinates
    return np.dot(T, point_homogeneous)[:3]  # Apply transformation and return 3D coordinates


# Initialize video capture
cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
cap.set(3, 640)  # Set width
cap.set(4, 480)  # Set height
cm_to_pixel = 60 / 640.0  # Conversion from pixels to centimeters
T = homogeneous_transform()

_, gray_image1 = cap.read()
gray_image1 = cv2.cvtColor(gray_image1, cv2.COLOR_BGR2GRAY)

while True:
    _, frame = cap.read()
    gray_image2 = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Motion detection using absolute difference
    diff_image = cv2.absdiff(gray_image1, gray_image2)
    _, BW = cv2.threshold(diff_image, 100, 255, cv2.THRESH_BINARY)

    # Find contours in the binary image (BW)
    contours, _ = cv2.findContours(BW, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Loop through each detected contour
    for contour in contours:
        # Calculate moments to get the centroid
        M = cv2.moments(contour)
        if M["m00"] > 0:  # Prevent division by zero
            cX = int(M["m10"] / M["m00"])  # X coordinate of the centroid
            cY = int(M["m01"] / M["m00"])  # Y coordinate of the centroid

            # Convert pixel locations to real-world coordinates in cm
            X_Location = cX * cm_to_pixel
            Y_Location = cY * cm_to_pixel


            # Apply transformation to the coordinates
            transformed_point = apply_transformation(T, (X_Location, Y_Location, 0))

            # Draw the contour and centroid on the frame
            cv2.drawContours(frame, [contour], -1, (0, 255, 0), 2)
            cv2.circle(frame, (cX, cY), 5, (255, 0, 0), -1)
            cv2.putText(frame, f"({X_Location:.2f}, {Y_Location:.2f})", (cX - 50, cY - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)

            # Output the transformed center coordinates
            print(f"Object center at (X: {X_Location:.2f} cm, Y: {Y_Location:.2f} cm)")
            print(f"Transformed Location: {transformed_point}")

    # Show the frame with the contours and centroids
    cv2.imshow('Video Feed', frame)

    if cv2.waitKey(5) == 27:  # Press 'Esc' to exit
        break

cap.release()
cv2.destroyAllWindows()
