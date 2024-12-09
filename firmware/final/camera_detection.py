
"""
   Update your system
     sudo apt-get update
     sudo apt-get upgrade
     
   Install system dependencies
     sudo apt-get install python3-pip libjpeg-dev libatlas-base-dev -y
     
   Install NumPy (specific version)
      pip3 install numpy==1.23.5
      
    Install TensorFlow Lite Runtime
       pip3 install tflite-runtime

  Install Pillow (for image processing):
      pip3 install --upgrade Pillow
   
   Install OpenCV: If full OpenCV is too large, use the lightweight version
      pip3 install opencv-python-headless

   Ensure the camera is enabled in Raspberry Pi configuration
      sudo raspi-config

   Reboot
      sudo reboot

   Run your program to verify everything is working:
      python3 camera_detection.py



"""


import cv2
from PIL import Image, ImageDraw, ImageFont
import numpy as np
import tflite_runtime.interpreter as tflite

# Path to the TensorFlow Lite model
model_path = '/home/jroc/Desktop/final/model.tflite'

# Load TensorFlow Lite model
interpreter = tflite.Interpreter(model_path=model_path)

# Allocate tensors
interpreter.allocate_tensors()

# Get input and output details
input_details = interpreter.get_input_details()
output_details = interpreter.get_output_details()

# Function to preprocess the image
def preprocess_image(image, target_size=(320, 320)):
    if isinstance(image, str):
        img = Image.open(image)
    elif isinstance(image, Image.Image):
        img = image
    else:
        raise ValueError("The argument must be an image path or a PIL Image object.")

    img.thumbnail(target_size, Image.Resampling.LANCZOS)
    new_img = Image.new("RGB", target_size, (0, 0, 0))
    paste_position = (
        (target_size[0] - img.size[0]) // 2,
        (target_size[1] - img.size[1]) // 2
    )
    new_img.paste(img, paste_position)
    img_array = np.array(new_img).astype(np.uint8)
    img_array = np.expand_dims(img_array, axis=0)
    return img_array

# Function to run inference on the model
def run_inference(img_array):
    input_index = input_details[0]['index']
    interpreter.set_tensor(input_index, img_array)
    interpreter.invoke()
    output_index = output_details[0]['index']
    output_data = interpreter.get_tensor(output_index)
    return output_data

# Function to get the predicted class
def get_predicted_class(output_data, class_labels=['recycle', 'non-recycle'], threshold=0.75):
    predicted_class_index = np.argmax(output_data)
    predicted_class = class_labels[predicted_class_index]
    prediction_probability = output_data[0][predicted_class_index]
    if prediction_probability >= threshold:
        predicted_class = 'recycle'
    elif prediction_probability > 0.60:
        predicted_class = 'trash'
    else : predicted_class ='none'
    return predicted_class, prediction_probability

# Function to use the camera for detection
def camera_detection():
    """
    Use the camera to detect and display predictions on frames.
    """
    cap = cv2.VideoCapture(0)  # Open the camera (0 is the default ID)
    
    # Set camera resolution to 640x480
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

    if not cap.isOpened():
        print("Cannot open the camera.")
        return

    print("Press 'q' to exit.")
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Cannot read frames from the camera.")
            break

        # Convert frame from OpenCV (BGR) to PIL (RGB)
        img = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        img_array = preprocess_image(img)
        output_data = run_inference(img_array)
        predicted_class, prediction_probability = get_predicted_class(output_data)

        # Display the result on the frame
        cv2.putText(
            frame,
            f"Predicted: {predicted_class}",
            (10, 30),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (0, 255, 0),
            2
        )
        cv2.putText(
            frame,
            f"Probability: {prediction_probability:.2f}",
            (10, 60),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (0, 255, 0),
            2
        )

        # Show the frame with predictions
        cv2.imshow('Camera Detection', frame)

        # Exit when 'q' is pressed
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

# Main program to test the functions
if __name__ == "__main__":
    camera_detection()
