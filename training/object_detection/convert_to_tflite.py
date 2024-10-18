import tensorflow as tf

# Convert the model
converter = tf.lite.TFLiteConverter.from_saved_model('inference_graph_mobilenet_final/saved_model') # path to the SavedModel directory
tflite_model = converter.convert()

# Save the model.
with open('inference_graph_mobilenet_final/saved_model/detect.tflite', 'wb') as f:
  f.write(tflite_model)