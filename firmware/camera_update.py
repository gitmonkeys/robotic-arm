import cv2
import numpy as np
from PIL import Image
import time

# Global list to store the scanned object centers and their classes
scanned_object_centers = []

# Function to create a homogeneous transformation matrix
def homogeneous_transform():
    T = np.array([[1, 0, 0, -24],  # X-axis translation 
                  [0, -1, 0, 59],  # Y-axis translation (upside down)
                  [0, 0, -1, 0],   # Z-axis remains unchanged
                  [0, 0, 0, 1]])   # Homogeneous coordinates
    return T

# Function to apply the transformation matrix to a point
def apply_transformation(T, point):
    point_homogeneous = np.array([point[0], point[1], point[2], 1])  # Convert point to homogeneous coordinates
    transformed_point_homogeneous = np.dot(T, point_homogeneous)     # Apply the transformation matrix
    return transformed_point_homogeneous[:3]                         # Return transformed 3D point

# Function to preprocess the image
def preprocess_image(image, target_size=(320, 320)):
    img = Image.fromarray(image)
    img.thumbnail(target_size, Image.LANCZOS)
    new_img = Image.new("RGB", target_size, (0, 0, 0))  # Padding with black
    paste_position = (
        (target_size[0] - img.size[0]) // 2,
        (target_size[1] - img.size[1]) // 2
    )
    new_img.paste(img, paste_position)
    img_array = np.array(new_img).astype(np.uint8)
    img_array = np.expand_dims(img_array, axis=0)
    return img_array

pred_recycle = 0.75
pred_trash = 0.65
# Updated function for class detection
def class_detection(image):
    """
    Perform object classification using a TensorFlow Lite model.
    """
    import tflite_runtime.interpreter as tflite

    model_path = '/home/jroc/Desktop/final/model.tflite'
    interpreter = tflite.Interpreter(model_path=model_path)
    interpreter.allocate_tensors()

    input_details = interpreter.get_input_details()
    output_details = interpreter.get_output_details()

    img_array = preprocess_image(image)
    input_index = input_details[0]['index']
    interpreter.set_tensor(input_index, img_array)
    interpreter.invoke()
    output_data = interpreter.get_tensor(output_details[0]['index'])

    prediction_probability = np.max(output_data)
    predicted_class_index = np.argmax(output_data)

    # Custom classification logic
    if prediction_probability >= pred_recycle:
        predicted_class = 'recycle'
    elif pred_trash < prediction_probability < pred_recycle:
        predicted_class = 'trash'
    else:
        predicted_class = None  # Skip this object

    return predicted_class, prediction_probability

# Function to capture an image, detect objects, and store their centers
def get_sorted_object_coordinates():
    global scanned_object_centers

    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)  # Set the width of the frame
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)  # Set the height of the frame

    if not cap.isOpened():
        print("Error: Unable to open the camera.")
        return None

    actual_width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
    cm_to_pixel = 54 / actual_width  # Conversion factor from pixels to centimeters

    T = homogeneous_transform()
    scanned_object_centers.clear()

    ret, frame = cap.read()
    if not ret:
        print("Error: Cannot capture frame from the camera.")
        cap.release()
        return None

    gray_image = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Convert to binary image using adaptive thresholding
    binary_image = cv2.adaptiveThreshold(
        gray_image, 255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY_INV, 11, 2
    )

    # Find contours in the binary image
    contours, _ = cv2.findContours(binary_image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    scanned_object_centers.clear()

    for contour in contours:
        # Filter out small contours to avoid noise
        if cv2.contourArea(contour) < 1000:
            continue

        x, y, w, h = cv2.boundingRect(contour)

        # Ignore objects that are too small or too large
        if w * cm_to_pixel < 1 or h * cm_to_pixel < 1 or w * cm_to_pixel > 8 or h * cm_to_pixel >15:
            continue

        object_roi = frame[y:y+h, x:x+w]
        object_class, probability = class_detection(object_roi)

        # Skip objects not meeting thresholds
        if object_class is None:
            continue

        # Calculate the center of the bounding box
        X_Location = (x + w / 2) * cm_to_pixel  # X coordinate in cm
        Y_Location = (y + h / 2) * cm_to_pixel  # Y coordinate in cm
        Z_Location = 0  # Z-location assumed to be 0 for 2D

        # Apply the transformation matrix to the detected location
        transformed_point = apply_transformation(T, (X_Location, Y_Location, Z_Location))

        # Append the transformed object center to the list
        scanned_object_centers.append((transformed_point[0], transformed_point[1], object_class))

        # Draw the bounding box and center on the original image
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)  # Draw bounding box

        # Prepare text for object class and probability
        label = f"{object_class} ({probability:.2f})"
        label_position = (x, y - 10 if y - 10 > 10 else y + 10)
        cv2.putText(frame, label, label_position, cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)

        # Draw center point
        center = (int(transformed_point[0] / cm_to_pixel), int(transformed_point[1] / cm_to_pixel))
        cv2.circle(frame, center, 5, (0, 0, 255), -1)  # Draw center point

    # Sort the scanned object centers by their distance from the origin (0, 0)
    scanned_object_centers.sort(key=lambda obj: np.sqrt(obj[0]**2 + obj[1]**2))
    
    # Release the camera
    cap.release()
    
    # Return the image with drawn objects
    return frame

# Main function
def main():
    print("Starting program...")
    while True:
        # Detect and process objects
        image_with_objects = get_sorted_object_coordinates()

        if image_with_objects is None:
            print("Exiting due to no image...")
            break

        # Print the coordinates of detected objects
        print("\nScanned Object Coordinates and Classes:")
        for i, obj in enumerate(scanned_object_centers):
            print(f"Object {i + 1}: X={obj[0]:.2f} cm, Y={obj[1]:.2f} cm, Class={obj[2]}")

        # Display the image
        cv2.imshow("Detected Objects", image_with_objects)

        # Wait for a key press (ESC to exit)
        if cv2.waitKey(1) & 0xFF == 27:  # ESC key
            print("Exiting program on user request.")
            break

    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()



