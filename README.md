# Potato Disease Detection using Deep Learning

A machine learning project that detects potato diseases (Healthy, Early Blight, Late Blight) using Convolutional Neural Networks (CNN) with TensorFlow/Keras.

## 🚀 Project Overview

This project consists of:
- **Machine Learning Model**: CNN trained on potato leaf images
- **Backend API**: Google Cloud Function for model inference
- **Frontend**: React.js web application for image upload and prediction
- **Training Pipeline**: Jupyter notebook for model development

## 🏗️ Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   React.js      │───▶│  Cloud Function  │───▶│   ML Model      │
│   Frontend      │    │  (Python/Flask)  │    │   (.h5 format)  │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                │
                                ▼
                       ┌──────────────────┐
                       │ Google Cloud     │
                       │ Storage Bucket   │
                       └──────────────────┘
```

## 📁 Project Structure

```
project/
├── project.ipynb          # Main training notebook
├── gcp/
│   ├── main.py           # Cloud Function code
│   └── requirements.txt  # Python dependencies
├── models/
│   └── 1.h5             # Trained model (HDF5 format)
├── api/
│   └── api.py           # Local FastAPI server (optional)
└── react_js/            # Frontend (separate branch)
    ├── src/
    │   └── App.js       # Main React component
    ├── .env             # Environment configuration
    └── package.json     # Node.js dependencies
```

## 🔧 Setup Instructions

### 1. Clone the Repository

```bash
git clone https://github.com/Kousthubh02/Potato-Disease-Detection-using-Deep-Learning.git
cd Potato-Disease-Detection-using-Deep-Learning
```

### 2. Machine Learning Model Training

```bash
# Install Python dependencies (if running locally)
pip install tensorflow keras matplotlib numpy pandas pillow kagglehub

# Open and run the Jupyter notebook
jupyter notebook project.ipynb
```

The notebook will:
- Download the PlantVillage dataset
- Train a CNN model on potato disease images
- Save the model as `models/1.h5`

### 3. Backend Setup

#### Option A: Google Cloud Function (Recommended for Production)

1. **Setup Google Cloud**:
   ```bash
   # Install Google Cloud CLI
   curl https://sdk.cloud.google.com | bash
   gcloud init
   gcloud auth login
   ```

2. **Create Storage Bucket**:
   ```bash
   gsutil mb gs://your-bucket-name
   gsutil cp models/1.h5 gs://your-bucket-name/models/1.h5
   ```

3. **Deploy Cloud Function**:
   ```bash
   cd gcp/
   gcloud functions deploy predict \
     --runtime python38 \
     --trigger-http \
     --allow-unauthenticated \
     --memory 1024MB \
     --timeout 300s
   ```

4. **Get Function URL**:
   ```bash
   gcloud functions describe predict --format="value(httpsTrigger.url)"
   ```

#### Option B: Local FastAPI Server (Development)

```bash
cd api/
pip install fastapi uvicorn python-multipart pillow tensorflow
python api.py
# Server runs on http://localhost:8000
```

### 4. Frontend Setup (React.js)

**Note**: The React frontend is maintained in a separate branch. Switch to the React branch first:

```bash
git checkout react-branch  # or your React branch name
cd react_js/
```

1. **Install Dependencies**:
   ```bash
   npm install
   ```

2. **Configure Environment**:
   Create `.env` file in `react_js/` directory:
   
   **For Cloud Function**:
   ```env
   REACT_APP_API_URL=https://your-cloud-function-url.cloudfunctions.net/predict
   ```
   
   **For Local Development**:
   ```env
   REACT_APP_API_URL=http://localhost:8000/predict
   ```

3. **Start Development Server**:
   ```bash
   npm start
   # App runs on http://localhost:3000
   ```

## 🔑 Environment Configuration

### React App (.env file)

The React app uses environment variables to configure the API endpoint:

```env
# Cloud Function (Production)
REACT_APP_API_URL=https://predict-qwzeghkfwq-uc.a.run.app

# Local FastAPI (Development)
REACT_APP_API_URL=http://localhost:8000/predict

# Optional: Enable/disable features
REACT_APP_ENABLE_DEBUG=false
REACT_APP_MAX_FILE_SIZE=5242880
```

### Backend Configuration

Update the bucket name in `gcp/main.py`:
```python
BUCKET_NAME = "your-bucket-name"  # Change this to your bucket
```

## 🚀 Usage

1. **Upload Image**: Select a potato leaf image using the file picker
2. **Get Prediction**: The model will classify the image as:
   - Healthy
   - Early Blight
   - Late Blight
3. **View Results**: See prediction confidence and probabilities

## 📊 Model Performance

- **Classes**: 3 (Healthy, Early Blight, Late Blight)
- **Architecture**: CNN with data augmentation
- **Input Size**: 256x256x3 RGB images
- **Format**: HDF5 (.h5) for optimal compatibility

## 🛠️ API Endpoints

### POST /predict
Upload an image for disease classification.

**Request**:
```bash
curl -X POST \
  -F "file=@potato_leaf.jpg" \
  https://your-function-url/predict
```

**Response**:
```json
{
  "class": "Healthy",
  "confidence": 0.8945,
  "all_predictions": {
    "Healthy": 0.8945,
    "Early Blight": 0.0821,
    "Late Blight": 0.0234
  }
}
```

## 🔧 Troubleshooting

### Common Issues

1. **CORS Errors**: Make sure the Cloud Function has proper CORS headers configured
2. **Model Loading**: Ensure the model file exists in the correct bucket path
3. **Memory Issues**: Cloud Function uses 1GB memory for TensorFlow model loading
4. **File Size**: Maximum upload size is ~5MB for images

### Debug Mode

Enable debug logging in the Cloud Function:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 📝 Development Notes

- Model format: Using .h5 format for better TensorFlow version compatibility
- CORS: Configured for cross-origin requests from React frontend
- Memory: Cloud Function configured with 1GB RAM for model loading
- Timeout: 300 seconds to handle model initialization

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/new-feature`)
3. Commit changes (`git commit -am 'Add new feature'`)
4. Push to branch (`git push origin feature/new-feature`)
5. Create Pull Request

## 📄 License

This project is open source and available under the MIT License.

## 🔗 Links

- **Live Demo**: [Your deployed React app URL]
- **API Endpoint**: [Your Cloud Function URL]
- **Dataset**: [PlantVillage Dataset](https://www.kaggle.com/datasets/arjuntejaswi/plant-village)
