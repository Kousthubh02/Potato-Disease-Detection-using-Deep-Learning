from google.cloud import storage
import tensorflow as tf
from PIL import Image
import numpy as np
import functions_framework
import json
import os

BUCKET_NAME = "tf-models2"
# Using .h5 format only for better compatibility with TensorFlow versions
class_names = ['Healthy', 'Late Blight', 'Early Blight']

model = None

def create_simple_model():
    """Create a simple compatible model for testing."""
    print("Creating a simple test model...")
    model = tf.keras.Sequential([
        tf.keras.layers.Conv2D(32, (3, 3), activation='relu', input_shape=(256, 256, 3)),
        tf.keras.layers.MaxPooling2D((2, 2)),
        tf.keras.layers.Conv2D(64, (3, 3), activation='relu'),
        tf.keras.layers.MaxPooling2D((2, 2)),
        tf.keras.layers.Conv2D(64, (3, 3), activation='relu'),
        tf.keras.layers.Flatten(),
        tf.keras.layers.Dense(64, activation='relu'),
        tf.keras.layers.Dense(3, activation='softmax')  # 3 classes
    ])
    
    model.compile(
        optimizer='adam',
        loss='sparse_categorical_crossentropy',
        metrics=['accuracy']
    )
    
    print("Simple model created successfully")
    return model

def download_blob(bucket_name, source_blob_name, destination_file_name):
    """Download a blob from the bucket."""
    try:
        storage_client = storage.Client()
        bucket = storage_client.bucket(bucket_name)
        blob = bucket.blob(source_blob_name)
        
        if not blob.exists():
            return False
        
        os.makedirs(os.path.dirname(destination_file_name), exist_ok=True)
        blob.download_to_filename(destination_file_name)
        return True
    except Exception as e:
        print(f"Error downloading {source_blob_name}: {e}")
        return False

def load_model():
    """Load the model from Google Cloud Storage using .h5 format only."""
    global model
    if model is None:
        try:
            # Load h5 format only for better compatibility
            model_path = "/tmp/model.h5"
            download_blob(BUCKET_NAME, "models/1.h5", model_path)
            model = tf.keras.models.load_model(model_path, compile=False)
            model.compile(
                optimizer='adam',
                loss='sparse_categorical_crossentropy',
                metrics=['accuracy']
            )
            print("✅ Successfully loaded h5 model from bucket")
            
        except Exception as e:
            print(f"Failed to load h5 model: {e}")
            print("⚠️ Could not load model from bucket, using simple test model")
            model = create_simple_model()

@functions_framework.http
def predict(request):
    """HTTP Cloud Function for plant disease prediction."""
    # CORS headers
    headers = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'POST, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type',
        'Content-Type': 'application/json'
    }
    
    if request.method == 'OPTIONS':
        return ('', 204, headers)
    
    if request.method != 'POST':
        return (json.dumps({'error': 'Method not allowed'}), 405, headers)
    
    try:
        # Check if file is present
        if 'file' not in request.files:
            return (json.dumps({'error': 'No file provided'}), 400, headers)
        
        file = request.files['file']
        if file.filename == '':
            return (json.dumps({'error': 'No file selected'}), 400, headers)
        
        # Load model
        load_model()
        
        # Process image
        image = Image.open(file).convert("RGB").resize((256, 256))
        image_array = np.array(image) / 255.0
        img_array = tf.expand_dims(image_array, 0)
        
        # Make prediction
        predictions = model.predict(img_array)
        predicted_class_index = np.argmax(predictions[0])
        predicted_class = class_names[predicted_class_index]
        confidence = float(np.max(predictions[0]))
        
        result = {
            "class": predicted_class,
            "confidence": round(confidence, 4),
            "all_predictions": {
                class_names[i]: round(float(predictions[0][i]), 4) 
                for i in range(len(class_names))
            }
        }
        
        return (json.dumps(result), 200, headers)
        
    except Exception as e:
        return (json.dumps({'error': str(e)}), 500, headers)

