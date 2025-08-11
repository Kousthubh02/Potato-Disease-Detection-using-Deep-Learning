import React, { useState, useCallback } from 'react';
import './App.css';

function App() {
  const [dragActive, setDragActive] = useState(false);
  const [uploadedFile, setUploadedFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [prediction, setPrediction] = useState(null);

  // Handle drag events
  const handleDrag = useCallback((e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  }, []);

  // Handle dropped files
  const handleDrop = useCallback((e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      const file = e.dataTransfer.files[0];
      if (file.type.startsWith('image/')) {
        setUploadedFile(file);
        setPrediction(null); // Clear previous prediction
      } else {
        alert('Please upload only image files');
      }
    }
  }, []);

  // Handle file input change
  const handleFileChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      const file = e.target.files[0];
      if (file.type.startsWith('image/')) {
        setUploadedFile(file);
        setPrediction(null); // Clear previous prediction
      } else {
        alert('Please upload only image files');
      }
    }
  };

  // Handle file upload to backend
  const handleUpload = async () => {
    if (!uploadedFile) return;

    setUploading(true);
    setPrediction(null);
    const formData = new FormData();
    formData.append('file', uploadedFile);

    try {
      console.log('Uploading to: http://127.0.0.1:8000/predict');
      const response = await fetch('http://127.0.0.1:8000/predict', {
        method: 'POST',
        body: formData,
        mode: 'cors',
      });
      
      console.log('Response status:', response.status);
      console.log('Response ok:', response.ok);
      
      if (response.ok) {
        const result = await response.json();
        console.log('Prediction result:', result);
        setPrediction(result);
      } else {
        const errorText = await response.text();
        console.error('Server error:', errorText);
        alert(`Upload failed: ${response.status} - ${errorText}`);
      }
    } catch (error) {
      console.error('Fetch error:', error);
      if (error.name === 'TypeError' && error.message.includes('fetch')) {
        alert('Cannot connect to backend server. Please ensure:\n1. Backend is running on http://127.0.0.1:8000\n2. CORS is properly configured\n3. No firewall is blocking the connection');
      } else {
        alert(`Error: ${error.message}`);
      }
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="App">
      <div className="farmer-background">
        <div className="content-overlay">
          <h1 className="app-title">Plant Disease Detection</h1>
          <p className="app-subtitle">Upload an image of a plant leaf to detect diseases</p>
          
          <div 
            className={`upload-area ${dragActive ? 'drag-active' : ''}`}
            onDragEnter={handleDrag}
            onDragLeave={handleDrag}
            onDragOver={handleDrag}
            onDrop={handleDrop}
          >
            <div className="upload-content">
              {uploadedFile ? (
                <div className="file-preview">
                  <img 
                    src={URL.createObjectURL(uploadedFile)} 
                    alt="Uploaded preview" 
                    className="preview-image"
                  />
                  <p className="file-name">{uploadedFile.name}</p>
                  <button 
                    className="upload-btn"
                    onClick={handleUpload}
                    disabled={uploading}
                  >
                    {uploading ? 'Analyzing...' : 'Analyze Plant'}
                  </button>
                  <button 
                    className="clear-btn"
                    onClick={() => {
                      setUploadedFile(null);
                      setPrediction(null);
                    }}
                  >
                    Clear
                  </button>
                </div>
              ) : (
                <>
                  <div className="upload-icon">📁</div>
                  <p className="upload-text">
                    Drag and drop your plant image here
                  </p>
                  <p className="upload-text-or">or</p>
                  <label className="file-input-label">
                    <input
                      type="file"
                      accept="image/*"
                      onChange={handleFileChange}
                      className="file-input"
                    />
                    Choose File
                  </label>
                </>
              )}
            </div>
          </div>
          
          {/* Prediction Results */}
          {prediction && (
            <div className="prediction-results">
              <h3 className="prediction-title">Analysis Results</h3>
              <div className="prediction-content">
                <div className="prediction-class">
                  <span className="prediction-label">Detected Condition:</span>
                  <span className={`prediction-value ${prediction.class.toLowerCase().replace(' ', '-')}`}>
                    {prediction.class}
                  </span>
                </div>
                <div className="prediction-confidence">
                  <span className="prediction-label">Confidence:</span>
                  <div className="confidence-bar-container">
                    <div 
                      className="confidence-bar" 
                      style={{width: `${(prediction.confidence * 100).toFixed(1)}%`}}
                    ></div>
                    <span className="confidence-text">
                      {(prediction.confidence * 100).toFixed(1)}%
                    </span>
                  </div>
                </div>
                <div className="prediction-advice">
                  {prediction.class === 'Healthy' ? (
                    <p className="advice healthy">✅ Your plant appears to be healthy! Continue with regular care.</p>
                  ) : prediction.class === 'Early Blight' ? (
                    <p className="advice warning">⚠️ Early Blight detected. Consider applying fungicide and improve air circulation.</p>
                  ) : prediction.class === 'Late Blight' ? (
                    <p className="advice danger">🚨 Late Blight detected. Immediate treatment required. Remove affected leaves and apply appropriate fungicide.</p>
                  ) : (
                    <p className="advice">Analysis complete. Please consult with an agricultural expert for specific treatment recommendations.</p>
                  )}
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default App;
