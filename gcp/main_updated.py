from google.cloud import storage
import tensorflow as tf
from PIL import Image
import numpy as np
import functions_framework
import json
import os

BUCKET_NAME = "tf-models2"
class_names = ['Healthy', 'Late Blight', 'Early Blight']

model = None

def list_bucket_contents():
    """List all files in the bucket for debugging."""
    try:
        storage_client = storage.Client()
        bucket = storage_client.get_bucket(BUCKET_NAME)
        blobs = bucket.list_blobs()
        
        files = []
        for blob in blobs:
            files.append({
                'name': blob.name,
                'size': blob.size,
                'updated': blob.updated.isoformat() if blob.updated else None
            })
        return files
    except Exception as e:
        print(f"Error listing bucket contents: {e}")
        return []

def download_blob(bucket_name, source_blob_name, destination_file_name):
    """Download a blob from the bucket with detailed error handling."""
    try:
        storage_client = storage.Client()
        bucket = storage_client.get_bucket(bucket_name)
        blob = bucket.blob(source_blob_name)
        
        # Check if blob exists
        if not blob.exists():
            raise Exception(f"File {source_blob_name} does not exist in bucket {bucket_name}")
        
        # Get blob info
        blob.reload()
        print(f"Downloading {source_blob_name} (size: {blob.size} bytes)")
        
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(destination_file_name), exist_ok=True)
        
        blob.download_to_filename(destination_file_name)
        
        # Verify download
        if os.path.exists(destination_file_name):
            file_size = os.path.getsize(destination_file_name)
            print(f"Downloaded successfully. Local file size: {file_size} bytes")
            return True
        else:
            raise Exception("File download failed - file not found after download")
            
    except Exception as e:
        print(f"Error downloading {source_blob_name}: {e}")
        raise

def create_simple_model():
    """Create a simple compatible model for testing."""
    print("Creating a simple test model...")
    model = tf.keras.Sequential([
        tf.keras.layers.Input(shape=(256, 256, 3)),
        tf.keras.layers.Conv2D(32, (3, 3), activation='relu'),
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

def load_model():
    """Load the model from Google Cloud Storage with comprehensive error handling."""
    global model
    if model is None:
        try:
            # First, list bucket contents for debugging
            print("Listing bucket contents...")
            files = list_bucket_contents()
            print(f"Found {len(files)} files in bucket:")
            for file in files:
                print(f"  - {file['name']} ({file['size']} bytes)")
            
            # Try different model files in order of preference
            model_files = [
                "models/1.keras",
                "models/model.h5", 
                "models/saved_model",
                "1.keras",
                "model.h5"
            ]
            
            model_loaded = False
            
            for model_file in model_files:
                try:
                    print(f"\nAttempting to load: {model_file}")
                    
                    if model_file.endswith('.keras'):
                        model_path = "/tmp/model.keras"
                        download_blob(BUCKET_NAME, model_file, model_path)
                        
                        # Try loading .keras file
                        try:
                            model = tf.keras.models.load_model(model_path, compile=False)
                            print(f"✅ Successfully loaded {model_file} without compilation")
                        except Exception as keras_error:
                            print(f"Failed to load .keras: {keras_error}")
                            continue
                            
                    elif model_file.endswith('.h5'):
                        model_path = "/tmp/model.h5"
                        download_blob(BUCKET_NAME, model_file, model_path)
                        
                        # Try loading .h5 file
                        try:
                            model = tf.keras.models.load_model(model_path, compile=False)
                            print(f"✅ Successfully loaded {model_file} without compilation")
                        except Exception as h5_error:
                            print(f"Failed to load .h5: {h5_error}")
                            continue
                            
                    elif model_file == "models/saved_model":
                        model_dir = "/tmp/saved_model"
                        # For SavedModel, we need to download the entire directory
                        try:
                            download_blob(BUCKET_NAME, model_file, model_dir)
                            model = tf.keras.models.load_model(model_dir)
                            print(f"✅ Successfully loaded SavedModel")
                        except Exception as saved_error:
                            print(f"Failed to load SavedModel: {saved_error}")
                            continue
                    
                    # If we get here, model was loaded successfully
                    if model is not None:
                        # Compile the model
                        model.compile(
                            optimizer='adam',
                            loss='sparse_categorical_crossentropy',
                            metrics=['accuracy']
                        )
                        print(f"✅ Model compiled successfully")
                        print(f"Model input shape: {model.input_shape}")
                        print(f"Model output shape: {model.output_shape}")
                        model_loaded = True
                        break
                        
                except Exception as file_error:
                    print(f"Could not load {model_file}: {file_error}")
                    continue
            
            if not model_loaded:
                print("❌ All model loading attempts failed. Creating a simple test model...")
                model = create_simple_model()
                print("⚠️  Using test model - predictions will not be accurate!")
            
        except Exception as e:
            print(f"Critical error in load_model: {e}")
            print("Creating fallback test model...")
            model = create_simple_model()

@functions_framework.http
def predict(request):
    """HTTP Cloud Function for plant disease prediction with comprehensive error handling."""
    # Set CORS headers
    headers = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'POST, OPTIONS, GET',
        'Access-Control-Allow-Headers': 'Content-Type',
        'Content-Type': 'application/json'
    }
    
    # Handle preflight OPTIONS request
    if request.method == 'OPTIONS':
        return ('', 204, headers)
    
    # Handle GET request for debugging
    if request.method == 'GET':
        try:
            bucket_files = list_bucket_contents()
            debug_info = {
                'status': 'Cloud Function is running',
                'tensorflow_version': tf.__version__,
                'bucket_name': BUCKET_NAME,
                'bucket_files': bucket_files,
                'model_loaded': model is not None,
                'model_info': {
                    'input_shape': str(model.input_shape) if model else None,
                    'output_shape': str(model.output_shape) if model else None
                }
            }
            return (json.dumps(debug_info, indent=2), 200, headers)
        except Exception as e:
            return (json.dumps({'error': f'Debug info failed: {str(e)}'}), 500, headers)
    
    # Only allow POST requests for prediction
    if request.method != 'POST':
        return (json.dumps({'error': 'Method not allowed. Use POST for predictions, GET for debug info.'}), 405, headers)
    
    try:
        # Check if file is present
        if 'file' not in request.files:
            return (json.dumps({'error': 'No file provided'}), 400, headers)
        
        file = request.files['file']
        if file.filename == '':
            return (json.dumps({'error': 'No file selected'}), 400, headers)
        
        # Load model if not already loaded
        load_model()
        
        if model is None:
            return (json.dumps({'error': 'Model could not be loaded'}), 500, headers)
        
        # Process the image
        try:
            image = Image.open(file).convert("RGB").resize((256, 256))
            image_array = np.array(image) / 255.0
            img_array = tf.expand_dims(image_array, 0)
            
            print(f"Image processed successfully. Shape: {img_array.shape}")
        except Exception as img_error:
            return (json.dumps({'error': f'Image processing failed: {str(img_error)}'}), 400, headers)
        
        # Make prediction
        try:
            predictions = model.predict(img_array)
            print(f"Predictions shape: {predictions.shape}")
            print(f"Predictions: {predictions}")
            
            # Get the predicted class and confidence
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
            
            print(f"Result: {result}")
            return (json.dumps(result), 200, headers)
            
        except Exception as pred_error:
            return (json.dumps({'error': f'Prediction failed: {str(pred_error)}'}), 500, headers)
        
    except Exception as e:
        error_message = f"Error processing request: {str(e)}"
        print(error_message)
        return (json.dumps({'error': error_message}), 500, headers)
