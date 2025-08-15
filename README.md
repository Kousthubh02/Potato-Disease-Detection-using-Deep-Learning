# Potato Disease Detection - React Frontend

A React.js web application for uploading potato leaf images and getting disease predictions from a machine learning model.

## 🚀 Quick Start

### 1. Install Dependencies
```bash
npm install
```

### 2. Configure Environment
Create a `.env` file in the root of this React app directory:

```env
# For Cloud Function (Production)
REACT_APP_API_URL=https://predict-qwzeghkfwq-uc.a.run.app

# For Local Development
# REACT_APP_API_URL=http://localhost:8000/predict

# Optional Configuration
REACT_APP_ENABLE_DEBUG=false
REACT_APP_MAX_FILE_SIZE=5242880
```

### 3. Start Development Server
```bash
npm start
```

The app will open at `http://localhost:3000`

## 🔧 Environment Configuration

### Required Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `REACT_APP_API_URL` | Backend API endpoint | `https://your-function-url/predict` |

### Optional Variables

| Variable | Description | Default | Example |
|----------|-------------|---------|---------|
| `REACT_APP_ENABLE_DEBUG` | Enable debug logging | `false` | `true` |
| `REACT_APP_MAX_FILE_SIZE` | Max upload size in bytes | `5242880` | `10485760` |

## 🌐 Backend Options

### Option 1: Google Cloud Function (Recommended)

```env
REACT_APP_API_URL=https://predict-qwzeghkfwq-uc.a.run.app
```

**Advantages**:
- ✅ Production ready
- ✅ Scalable
- ✅ No local setup required
- ✅ Always available

**Use Case**: Production deployment, demo, sharing with others

### Option 2: Local FastAPI Server

```env
REACT_APP_API_URL=http://localhost:8000/predict
```

**Requirements**: 
1. Start the local API server:
   ```bash
   cd ../api
   python api.py
   ```

**Advantages**:
- ✅ Faster development cycle
- ✅ No cloud costs
- ✅ Full control over backend
- ✅ Offline development

**Use Case**: Local development, testing, debugging

## 📱 Features

- **Drag & Drop Upload**: Easy image uploading interface
- **Real-time Preview**: See uploaded image before prediction
- **Instant Results**: Get predictions in seconds
- **Confidence Scores**: View prediction confidence levels
- **Responsive Design**: Works on desktop and mobile
- **Error Handling**: User-friendly error messages

## 🎯 Usage

1. **Upload Image**: 
   - Click "Choose File" or drag & drop
   - Select a potato leaf image (JPG, PNG)
   - Image will be automatically resized to 256x256

2. **Get Prediction**:
   - Click "Predict Disease"
   - Wait for model inference (2-5 seconds)

3. **View Results**:
   - See predicted disease class
   - Check confidence percentage
   - View all class probabilities

## 🔍 Supported Image Types

- **Formats**: JPG, JPEG, PNG
- **Max Size**: 5MB (configurable)
- **Optimal Size**: 256x256 pixels
- **Content**: Potato leaf images

## ⚙️ Development

### Project Structure

```
react_js/
├── public/
│   ├── index.html
│   └── manifest.json
├── src/
│   ├── App.js          # Main component
│   ├── App.css         # Styling
│   ├── index.js        # Entry point
│   └── index.css       # Global styles
├── .env                # Environment config
├── package.json        # Dependencies
└── README.md          # This file
```

## 🐛 Troubleshooting

### Common Issues

#### 1. CORS Errors
```
Access to fetch at 'API_URL' from origin 'http://localhost:3000' has been blocked by CORS policy
```

**Solution**: Ensure backend has proper CORS headers configured

#### 2. Environment Variables Not Loading
```
Cannot read property of undefined
```

**Solution**: 
- Ensure `.env` file is in React app root
- Variables must start with `REACT_APP_`
- Restart development server after changes

#### 3. Network/Connection Errors
```
Failed to fetch
```

**Solutions**:
- Check if backend is running (local) or deployed (cloud)
- Verify URL in `.env` file
- Check network connectivity

## 🚀 Available Scripts

### `npm start`
Runs the app in development mode at [http://localhost:3000](http://localhost:3000)

### `npm test`
Launches the test runner in interactive watch mode

### `npm run build`
Builds the app for production to the `build` folder

### `npm run eject`
**Note: this is a one-way operation. Once you `eject`, you can't go back!**

## 🔗 API Contract

### Request Format
```javascript
const formData = new FormData();
formData.append('file', imageFile);

fetch(apiUrl, {
  method: 'POST',
  body: formData
})
```

### Response Format
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

## 📝 Learn More

- [Create React App documentation](https://facebook.github.io/create-react-app/docs/getting-started)
- [React documentation](https://reactjs.org/)
- [Main Project README](../README.md)
