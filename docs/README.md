# 🍕 Smart Restaurant Ordering Assistant

A complete AI-powered restaurant ordering system that processes natural language orders using Flask, Firebase Firestore, and advanced NLP techniques.

## 📋 Table of Contents

- [Features](#features)
- [Project Structure](#project-structure)
- [Prerequisites](#prerequisites)
- [Installation & Setup](#installation--setup)
- [Configuration](#configuration)
- [Usage](#usage)
- [API Documentation](#api-documentation)
- [Testing](#testing)
- [Deployment](#deployment)
- [Improvements Needed](#improvements-needed)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)

## ✨ Features

### 🤖 Natural Language Processing
- **Intent Classification**: Understands user intentions (order, menu, cancel, greeting)
- **Entity Extraction**: Extracts food items and quantities from natural language
- **Fuzzy Matching**: Handles misspellings and variations in item names
- **Multi-language Support**: Basic support for casual language and abbreviations

### 🗄️ Database Management (Firebase Firestore)
- **Menu Management**: Complete menu with categories, prices, and availability
- **Order Processing**: Store and manage orders with full order tracking
- **Chat Logging**: Conversation history for each order
- **User Management**: Basic user information storage

### 🌐 Web Interface
- **Backend API**: RESTful Flask API with comprehensive endpoints
- **Frontend**: Clean Streamlit interface for ordering and management
- **Real-time Updates**: Live order status updates
- **Admin Features**: Order management and menu viewing

### 🛠️ Technical Features
- **Error Handling**: Comprehensive error handling and logging
- **Testing Suite**: Complete NLP testing framework
- **Security**: Environment-based configuration and secure API endpoints
- **Performance**: Optimized for fast response times and scalability

## 📁 Project Structure

```
restaurant-assistant/
├── backend/
│   ├── app.py                 # Main Flask application
│   ├── nlp.py                 # NLP processing module
│   ├── firebase_client.py     # Firebase connection
│   ├── seed_data.py          # Database seeding script
│   ├── requirements.txt      # Python dependencies
│   └── .env.example         # Environment template
├── frontend/
│   └── streamlit_app.py     # Streamlit frontend
├── data/
│   └── sample_orders.csv    # Test data for NLP
├── tests/
│   └── test_nlp.py         # NLP testing suite
├── docs/
│   ├── API_DOCUMENTATION.md
│   └── DEPLOYMENT_GUIDE.md
└── README.md               # This file
```

## 📋 Prerequisites

### System Requirements
- Python 3.9 or higher
- Git
- Internet connection (for Firebase)

### Accounts Needed
1. **Firebase Account** (Google account)
   - Create project at [Firebase Console](https://console.firebase.google.com)
   - Enable Firestore Database
   - Generate service account key

2. **Deployment Platform** (optional)
   - [Render](https://render.com) (recommended)
   - [Railway](https://railway.app)
   - [Streamlit Cloud](https://share.streamlit.io) for frontend

## 🚀 Installation & Setup

### 1. Clone the Repository
```bash
git clone <your-repo-url>
cd restaurant-assistant
```

### 2. Create Virtual Environment
```bash
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

### 3. Install Dependencies
```bash
cd backend
pip install -r requirements.txt
```

### 4. Firebase Setup
1. Go to [Firebase Console](https://console.firebase.google.com)
2. Create a new project
3. Enable Firestore Database (start in test mode)
4. Go to Project Settings → Service Accounts
5. Generate new private key (JSON file)
6. Download and save as `serviceAccountKey.json` in the `backend/` folder

### 5. Environment Configuration
```bash
cd backend
cp .env.example .env
# Edit .env file with your configuration
```

### 6. Seed the Database
```bash
cd backend
python seed_data.py
```

### 7. Test the Setup
```bash
# Test Firebase connection
python firebase_client.py

# Test NLP functionality
cd ../tests
python test_nlp.py --basic
```

## ⚙️ Configuration

### Environment Variables (.env)
```bash
# Flask Configuration
FLASK_ENV=development
FLASK_APP=app.py
PORT=5000

# Firebase (choose one method)
# Method 1: Local file (development)
# Place serviceAccountKey.json in backend folder

# Method 2: Environment variable (deployment)
# FIREBASE_SERVICE_ACCOUNT={"type":"service_account"...}

# Optional configurations
NLP_MODE=basic  # or 'advanced' for transformer models
LOG_LEVEL=INFO
DEBUG=true
```

### Firebase Security Rules (Production)
```javascript
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    // Allow read/write access to authenticated users
    match /{document=**} {
      allow read, write: if request.auth != null;
    }
    
    // Public read access to menu (optional)
    match /menus/{menuId} {
      allow read: if true;
    }
  }
}
```

## 🏃 Usage

### Running Locally

#### Backend Server
```bash
cd backend
python app.py
# Server starts at http://localhost:5000
```

#### Frontend Interface
```bash
cd frontend
streamlit run streamlit_app.py
# Interface opens at http://localhost:8501
```

### Testing the System

#### 1. Health Check
```bash
curl http://localhost:5000/health
```

#### 2. Get Menu
```bash
curl http://localhost:5000/menu
```

#### 3. Place Order
```bash
curl -X POST http://localhost:5000/order \
  -H "Content-Type: application/json" \
  -d '{"message": "I want 2 chicken pizzas and 1 coke"}'
```

#### 4. Sample Test Queries
Try these in the frontend:
- "I want 2 chicken pizzas"
- "Give me a burger and fries"
- "Show me the menu"
- "I need 3 samosas and 2 teas"
- "Cancel my order"

## 📖 API Documentation

### Base URL
- Local: `http://localhost:5000`
- Production: `https://your-app.render.com`

### Endpoints

#### GET /health
Health check endpoint
```json
{
  "status": "healthy",
  "database": "connected",
  "timestamp": "2024-01-01T00:00:00Z"
}
```

#### GET /menu
Get all available menu items
```json
{
  "success": true,
  "menu": [
    {
      "item_id": "pizza_chicken_001",
      "name": "Chicken Pizza",
      "category": "Pizza",
      "price": 500,
      "description": "Delicious chicken pizza",
      "available": true
    }
  ]
}
```

#### POST /order
Process natural language order
```json
// Request
{
  "message": "I want 2 chicken pizzas and 1 coke",
  "user": {
    "name": "John Doe",
    "phone": "+1234567890"
  }
}

// Response
{
  "success": true,
  "intent": "order_food",
  "order": {
    "order_id": "ORD_20240101_001",
    "items": [
      {
        "name": "Chicken Pizza",
        "quantity": 2,
        "unit_price": 500,
        "total_price": 1000
      }
    ],
    "total_price": 1100,
    "status": "Pending"
  }
}
```

#### GET /orders
Get order history
```json
{
  "success": true,
  "orders": [...],
  "count": 10
}
```

## 🧪 Testing

### Run NLP Tests
```bash
cd tests

# Basic functionality tests
python test_nlp.py --basic

# Test with CSV data
python test_nlp.py --csv ../data/sample_orders.csv

# Interactive testing
python test_nlp.py --interactive

# Run all tests
python test_nlp.py
```

### Test Results Interpretation
- **Intent Accuracy**: Should be >85% for production use
- **Item Accuracy**: Should be >80% for production use
- **Quantity Accuracy**: Should be >75% for production use

### Manual Testing Checklist
- [ ] Backend starts without errors
- [ ] Firebase connection successful
- [ ] Menu loads correctly
- [ ] Orders can be placed via API
- [ ] Orders appear in Firebase console
- [ ] Frontend connects to backend
- [ ] Chat interface works
- [ ] Order history displays

## 🚀 Deployment

### Backend Deployment (Render)

1. **Push to GitHub**
   ```bash
   git add .
   git commit -m "Initial commit"
   git push origin main
   ```

2. **Create Render Web Service**
   - Connect your GitHub repository
   - Set build command: `pip install -r backend/requirements.txt`
   - Set start command: `cd backend && gunicorn app:app`
   - Add environment variables:
     - `FIREBASE_SERVICE_ACCOUNT`: Paste your JSON key content
     - `FLASK_ENV`: `production`
     - `PORT`: `10000` (or leave default)

3. **Deploy and Test**
   - Wait for deployment to complete
   - Test API endpoints with your new URL

### Frontend Deployment (Streamlit Cloud)

1. **Update Backend URL**
   ```python
   # In streamlit_app.py, update:
   BACKEND_URL = "https://your-app.render.com"
   ```

2. **Deploy on Streamlit Cloud**
   - Go to [share.streamlit.io](https://share.streamlit.io)
   - Connect your GitHub repository
   - Set main file path: `frontend/streamlit_app.py`
   - Deploy

### Environment Variables for Deployment
```bash
# Render Environment Variables
FIREBASE_SERVICE_ACCOUNT={"type":"service_account","project_id":"your-project",...}
FLASK_ENV=production
PORT=10000
PYTHON_VERSION=3.9.18
```

## 🔧 Improvements Needed

### 1. NLP Accuracy (Priority: High)
**Current State**: Basic rule-based + fuzzy matching (~70% accuracy)
**Improvements Needed**:
- Train custom model on restaurant domain data
- Better quantity-to-item pairing logic
- Handle complex orders (sizes, modifications, special requests)
- Support for multiple languages

**Implementation**:
```python
# Add to nlp.py
def train_custom_model(training_data):
    # Implement custom model training
    pass

def handle_complex_orders(text, context):
    # Better parsing for "large pizza", "no onions", etc.
    pass
```

### 2. Error Handling & Robustness (Priority: High)
**Current State**: Basic error handling
**Improvements Needed**:
- Comprehensive try-catch blocks
- Graceful failure responses
- Input validation and sanitization
- Rate limiting and abuse prevention

**Implementation**:
```python
# Add to app.py
from functools import wraps
import time

def rate_limit(max_calls=100, window=3600):
    # Implement rate limiting decorator
    pass

@app.errorhandler(429)
def rate_limit_exceeded(error):
    return jsonify({"error": "Rate limit exceeded"}), 429
```

### 3. User Interface & Experience (Priority: Medium)
**Current State**: Basic Streamlit interface
**Improvements Needed**:
- Modern React-based frontend
- Voice input capability
- Order confirmation dialogs
- Real-time order tracking
- Mobile-responsive design

### 4. Security (Priority: High)
**Current State**: Basic security
**Improvements Needed**:
- User authentication and authorization
- API key management
- Input sanitization
- HTTPS enforcement
- Session management

### 5. Analytics & Monitoring (Priority: Medium)
**Current State**: Basic logging
**Improvements Needed**:
- Order analytics dashboard
- Performance monitoring
- Error tracking and alerting
- Business intelligence features

### 6. Scalability (Priority: Medium)
**Current State**: Single server deployment
**Improvements Needed**:
- Database connection pooling
- Caching layer (Redis)
- Load balancing
- Microservices architecture

## 🔍 How to Verify It's Working

### 1. Backend Health Check
```bash
# Should return healthy status
curl http://localhost:5000/health

# Should return 200 OK
curl -I http://localhost:5000/menu
```

### 2. Database Connection
- Check Firebase console for new collections
- Verify menu items are populated
- Test order creation and storage

### 3. NLP Processing Test
```python
from backend.nlp import parse_order
result = parse_order("I want 2 pizzas", ["Pizza", "Burger", "Coke"])
print(result)  # Should extract items and quantities correctly
```

### 4. End-to-End Test
1. Start backend server ✅
2. Start frontend ✅
3. Place order through UI ✅
4. Check Firebase console for stored order ✅
5. Verify order appears in order history ✅

### 5. Performance Benchmarks
- Response time: <3 seconds for normal requests
- NLP processing: <2 seconds
- Database operations: <1 second
- Frontend load time: <2 seconds

## 🐛 Troubleshooting

### Common Issues & Solutions

#### 1. Firebase Connection Error
**Error**: `Authentication failed`
**Solution**:
- Check if `serviceAccountKey.json` exists in backend folder
- Verify JSON file is valid
- Ensure Firebase project has Firestore enabled
- Check environment variable `FIREBASE_SERVICE_ACCOUNT` format

#### 2. NLP Model Loading Slow
**Error**: Long startup time
**Solution**:
- Set `NLP_MODE=basic` in .env for faster startup
- Use model caching
- Consider using lighter models in production

#### 3. Frontend Can't Connect to Backend
**Error**: CORS errors or connection refused
**Solution**:
- Check backend URL in `streamlit_app.py`
- Ensure backend server is running
- Add CORS headers (already implemented)
- Check firewall settings

#### 4. Fuzzy Matching Not Working
**Error**: Menu items not found
**Solution**:
- Check menu seeding was successful
- Lower similarity threshold in `nlp.py`
- Verify menu names match expected format

#### 5. Deployment Issues
**Error**: Environment variables not set
**Solution**:
- Double-check all required env vars in deployment platform
- Ensure JSON formatting is correct for Firebase credentials
- Verify build and start commands

### Debug Mode
```bash
# Enable debug logging
export LOG_LEVEL=DEBUG
export FLASK_ENV=development

# Run with verbose output
python app.py
```

### Getting Help
1. Check the logs first (`app.log` if configured)
2. Test individual components separately
3. Use the testing scripts to isolate issues
4. Check Firebase console for data integrity
5. Verify network connectivity and permissions

## 🤝 Contributing

### Development Setup
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests
5. Submit a pull request

### Code Style
- Follow PEP 8 for Python code
- Use meaningful variable names
- Add docstrings for functions
- Include error handling
- Write tests for new features

### Testing Requirements
- All new features must include tests
- NLP accuracy should not decrease
- API endpoints must have integration tests
- Frontend changes should be tested manually

## 📝 License

This project is created for educational purposes. Feel free to use and modify as needed.

## 📞 Support

For support or questions:
1. Check the troubleshooting section
2. Review the test results
3. Check Firebase console for data issues
4. Verify all prerequisites are met

---

**Built with ❤️ using Flask, Firebase, and modern NLP techniques**