# 🚀 Vercel Deployment Guide
## Medical Text Classification App

Complete guide for deploying the Medical Text Classification application on Vercel with both frontend and serverless API.

## 🎯 Deployment Strategy

### **Hybrid Approach**
- **Frontend**: React app deployed as static site on Vercel
- **Backend**: FastAPI converted to Vercel serverless functions
- **Database**: External PostgreSQL (Supabase, Neon, or Render)

### **Important Considerations**

⚠️ **Model Size Limitation**: Vercel serverless functions have a 50MB deployment size limit. The full BiomedBERT model (~400MB) exceeds this limit.

**Solutions:**
1. **Lightweight Model**: Use a smaller model or model quantization
2. **External Model Hosting**: Host model on cloud storage (S3, GCS) and load dynamically
3. **Hybrid Deployment**: Keep API on Render/Railway, deploy only frontend on Vercel

## 📁 Required Files

### 1. Vercel Configuration (`vercel.json`)
```json
{
  "version": 2,
  "name": "medical-text-classification",
  "buildCommand": "cd frontend && npm ci && npm run build",
  "outputDirectory": "frontend/build",
  "builds": [
    {
      "src": "api/main.py",
      "use": "@vercel/python"
    }
  ],
  "routes": [
    {
      "src": "/api/(.*)",
      "dest": "/api/main.py"
    },
    {
      "src": "/static/(.*)",
      "headers": {
        "cache-control": "public, max-age=31536000, immutable"
      }
    },
    {
      "src": "/(.*\\.(js|css|ico|png|jpg|jpeg|gif|svg|woff|woff2|ttf|eot))",
      "headers": {
        "cache-control": "public, max-age=31536000, immutable"
      }
    },
    {
      "src": "/(.*)",
      "dest": "/index.html"
    }
  ],
  "env": {
    "ENVIRONMENT": "production",
    "DEBUG": "false",
    "LOG_LEVEL": "INFO"
  },
  "functions": {
    "api/main.py": {
      "maxDuration": 30,
      "memory": 1024
    }
  },
  "regions": ["iad1"]
}
```

### 2. Serverless API (`api/main.py`)
```python
"""
Vercel Serverless API for Medical Text Classification
Simplified version optimized for serverless deployment
"""

import os
import json
import time
from typing import Dict, Any
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, validator

# Initialize FastAPI app
app = FastAPI(
    title="Medical Text Classification API",
    description="Serverless API for medical text classification",
    version="1.0.0"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure for your domain in production
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

# Request/Response models
class PredictionRequest(BaseModel):
    text: str
    
    @validator('text')
    def validate_text(cls, v):
        if not v or not v.strip():
            raise ValueError('Text cannot be empty')
        if len(v) > 5000:
            raise ValueError('Text too long (max 5000 characters)')
        return v.strip()

class PredictionResponse(BaseModel):
    predicted_class: int
    confidence: float
    focus_group: str
    probabilities: list
    processing_time_ms: float
    model_version: str
    timestamp: str

# Focus group mapping
FOCUS_GROUPS = {
    0: "Neurological & Cognitive Disorders",
    1: "Cancers",
    2: "Cardiovascular Diseases", 
    3: "Metabolic & Endocrine Disorders",
    4: "Other Age-Related & Immune Disorders"
}

@app.get("/")
async def root():
    return {
        "message": "Medical Text Classification API - Vercel Serverless",
        "version": "1.0.0",
        "status": "healthy"
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "version": "1.0.0"
    }

@app.post("/predict", response_model=PredictionResponse)
async def predict(request: PredictionRequest):
    """Predict medical text classification."""
    start_time = time.time()
    
    # Simplified prediction logic for demo
    # In production, implement your model inference here
    import random
    
    # Mock prediction based on keywords
    text_lower = request.text.lower()
    if any(word in text_lower for word in ['diabetes', 'insulin', 'glucose']):
        predicted_class = 3  # Metabolic & Endocrine
        confidence = 0.95
    elif any(word in text_lower for word in ['heart', 'cardiac', 'blood pressure']):
        predicted_class = 2  # Cardiovascular
        confidence = 0.92
    elif any(word in text_lower for word in ['cancer', 'tumor', 'oncology']):
        predicted_class = 1  # Cancers
        confidence = 0.89
    elif any(word in text_lower for word in ['alzheimer', 'brain', 'neurological']):
        predicted_class = 0  # Neurological
        confidence = 0.87
    else:
        predicted_class = 4  # Other
        confidence = 0.75
    
    # Generate mock probabilities
    probabilities = [0.1] * 5
    probabilities[predicted_class] = confidence
    remaining = 1.0 - confidence
    for i in range(5):
        if i != predicted_class:
            probabilities[i] = remaining / 4
    
    processing_time = (time.time() - start_time) * 1000
    
    return PredictionResponse(
        predicted_class=predicted_class,
        confidence=confidence,
        focus_group=FOCUS_GROUPS[predicted_class],
        probabilities=probabilities,
        processing_time_ms=processing_time,
        model_version="demo-v1.0",
        timestamp=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    )
```

### 3. API Requirements (`api/requirements.txt`)
```
fastapi==0.104.1
pydantic==2.5.0
uvicorn==0.24.0
```

### 4. Frontend Environment (`.env.production`)
```bash
REACT_APP_API_URL=/api
REACT_APP_ENVIRONMENT=production
REACT_APP_ENABLE_ANALYTICS=false
REACT_APP_ENABLE_DEBUG=false
```

## 🚀 Deployment Steps

### **Option 1: Frontend Only on Vercel (Recommended)**

1. **Deploy API on Render/Railway**:
   ```bash
   # Use existing Render configuration
   # API will be available at: https://your-api.onrender.com
   ```

2. **Deploy Frontend on Vercel**:
   ```bash
   # Install Vercel CLI
   npm i -g vercel
   
   # Login to Vercel
   vercel login
   
   # Deploy frontend
   cd frontend
   vercel --prod
   ```

3. **Configure Environment Variables**:
   ```bash
   # In Vercel dashboard, set:
   REACT_APP_API_URL=https://your-api.onrender.com
   REACT_APP_ENVIRONMENT=production
   ```

### **Option 2: Full Stack on Vercel (Limited)**

1. **Prepare Repository**:
   ```bash
   # Ensure all files are in place
   # - vercel.json
   # - api/main.py
   # - api/requirements.txt
   # - frontend/ directory
   ```

2. **Deploy to Vercel**:
   ```bash
   # Install Vercel CLI
   npm i -g vercel
   
   # Login and deploy
   vercel login
   vercel --prod
   ```

3. **Configure Environment Variables**:
   ```bash
   # In Vercel dashboard, add:
   ENVIRONMENT=production
   DEBUG=false
   LOG_LEVEL=INFO
   ```

## 🔧 Configuration

### **Frontend Build Configuration**

Update `frontend/package.json`:
```json
{
  "scripts": {
    "start": "react-scripts start",
    "build": "react-scripts build",
    "test": "react-scripts test",
    "vercel-build": "react-scripts build"
  }
}
```

### **API Configuration**

For production ML model integration:

```python
# In api/main.py, add model loading
import torch
from transformers import AutoTokenizer, AutoModel

# Load model from cloud storage
def load_model():
    # Download model from S3/GCS if not cached
    model_url = os.getenv('MODEL_URL')
    # Implementation depends on your model hosting solution
    pass
```

## 🌐 Domain Configuration

### **Custom Domain Setup**

1. **Add Domain in Vercel**:
   - Go to Project Settings → Domains
   - Add your custom domain
   - Configure DNS records

2. **Update CORS Configuration**:
   ```python
   # In api/main.py
   app.add_middleware(
       CORSMiddleware,
       allow_origins=["https://yourdomain.com"],
       allow_credentials=True,
       allow_methods=["GET", "POST", "OPTIONS"],
       allow_headers=["*"],
   )
   ```

## 📊 Monitoring

### **Vercel Analytics**

1. **Enable Analytics**:
   ```bash
   # In Vercel dashboard
   Project → Analytics → Enable
   ```

2. **Add Analytics to Frontend**:
   ```bash
   npm install @vercel/analytics
   ```

   ```typescript
   // In src/index.tsx
   import { Analytics } from '@vercel/analytics/react';
   
   root.render(
     <React.StrictMode>
       <App />
       <Analytics />
     </React.StrictMode>
   );
   ```

## 🚨 Limitations & Considerations

### **Vercel Limitations**
- **Function Size**: 50MB limit (model files too large)
- **Execution Time**: 30s max for serverless functions
- **Memory**: 1GB max for serverless functions
- **Cold Starts**: Initial requests may be slower

### **Recommended Architecture**
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Vercel        │    │   Render/       │    │   Database      │
│   (Frontend)    │───▶│   Railway       │───▶│   (Supabase/    │
│                 │    │   (API + ML)    │    │    Neon)        │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 💰 Cost Estimation

### **Vercel Pricing**
- **Hobby Plan**: Free (100GB bandwidth, 100 function executions/day)
- **Pro Plan**: $20/month (1TB bandwidth, unlimited functions)

### **Total Monthly Cost**
- **Frontend (Vercel)**: $0-20
- **API (Render)**: $25
- **Database (Supabase)**: $0-25
- **Total**: $25-70/month

## 🔄 CI/CD Integration

### **GitHub Actions for Vercel**

```yaml
# .github/workflows/vercel.yml
name: Vercel Deployment
on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Setup Node.js
        uses: actions/setup-node@v2
        with:
          node-version: '18'
          
      - name: Install dependencies
        run: cd frontend && npm ci
        
      - name: Build frontend
        run: cd frontend && npm run build
        
      - name: Deploy to Vercel
        uses: amondnet/vercel-action@v20
        with:
          vercel-token: ${{ secrets.VERCEL_TOKEN }}
          vercel-org-id: ${{ secrets.ORG_ID }}
          vercel-project-id: ${{ secrets.PROJECT_ID }}
          vercel-args: '--prod'
```

## 🎯 Next Steps

1. **Choose Deployment Strategy**: Frontend-only or full-stack
2. **Set Up External Services**: Database, model hosting
3. **Configure Domain**: Custom domain and SSL
4. **Enable Monitoring**: Analytics and error tracking
5. **Test Thoroughly**: End-to-end testing in production

---

## 📞 Support

For deployment issues:
- **Vercel Docs**: https://vercel.com/docs
- **GitHub Issues**: Create issue in repository
- **Community**: Vercel Discord/GitHub Discussions

This guide provides a complete setup for deploying your Medical Text Classification app on Vercel with optimal performance and cost efficiency.
