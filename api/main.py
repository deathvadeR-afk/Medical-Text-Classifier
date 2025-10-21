"""
Vercel Serverless API for Medical Text Classification
Simplified version of the FastAPI backend optimized for Vercel deployment
"""

import os
import json
import time
from typing import Dict, Any
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, validator
import torch
from transformers import AutoTokenizer, AutoModel
import numpy as np

# Initialize FastAPI app
app = FastAPI(
    title="Medical Text Classification API",
    description="Serverless API for medical text classification using BiomedBERT",
    version="1.0.0"
)

# CORS configuration for Vercel
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend domain
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

# Global variables for model caching
_model = None
_tokenizer = None
_label_mapping = None

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

def load_model():
    """Load model components with caching for serverless optimization."""
    global _model, _tokenizer, _label_mapping
    
    if _model is None:
        try:
            # For Vercel deployment, we'll use a lightweight approach
            # In production, you might want to load from a cloud storage
            model_name = "microsoft/BiomedNLP-BiomedBERT-base-uncased-abstract-fulltext"
            
            _tokenizer = AutoTokenizer.from_pretrained(model_name)
            _model = AutoModel.from_pretrained(model_name)
            _label_mapping = FOCUS_GROUPS
            
            # Set model to evaluation mode
            _model.eval()
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to load model: {str(e)}")
    
    return _model, _tokenizer, _label_mapping

def predict_text(text: str) -> Dict[str, Any]:
    """Perform text classification prediction."""
    start_time = time.time()
    
    try:
        model, tokenizer, label_mapping = load_model()
        
        # Tokenize input
        inputs = tokenizer(
            text,
            return_tensors="pt",
            truncation=True,
            padding=True,
            max_length=512
        )
        
        # Get model predictions
        with torch.no_grad():
            outputs = model(**inputs)
            # For this simplified version, we'll use a basic classification approach
            # In production, you'd load your fine-tuned model weights
            
            # Simplified prediction logic (replace with your actual model)
            pooled_output = outputs.last_hidden_state.mean(dim=1)
            
            # Mock classification for demo (replace with actual model inference)
            # This is a simplified approach - in production, load your trained weights
            logits = torch.randn(1, 5)  # Mock logits for 5 classes
            probabilities = torch.softmax(logits, dim=-1).squeeze().tolist()
            predicted_class = int(torch.argmax(logits, dim=-1).item())
            confidence = float(max(probabilities))
        
        processing_time = (time.time() - start_time) * 1000
        
        return {
            "predicted_class": predicted_class,
            "confidence": confidence,
            "focus_group": label_mapping[predicted_class],
            "probabilities": probabilities,
            "processing_time_ms": processing_time,
            "model_version": "biomedbert-v1.0-serverless",
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")

@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Medical Text Classification API - Vercel Serverless",
        "version": "1.0.0",
        "status": "healthy",
        "endpoints": {
            "health": "/health",
            "predict": "/predict",
            "docs": "/docs"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    try:
        # Basic health check
        model_status = "healthy"
        try:
            load_model()
        except Exception:
            model_status = "unhealthy"
        
        return {
            "status": "healthy" if model_status == "healthy" else "degraded",
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "components": {
                "model": {"status": model_status},
                "api": {"status": "healthy"}
            },
            "version": "1.0.0"
        }
    except Exception as e:
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "error": str(e),
                "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
            }
        )

@app.post("/predict", response_model=PredictionResponse)
async def predict(request: PredictionRequest):
    """Predict medical text classification."""
    try:
        result = predict_text(request.text)
        return PredictionResponse(**result)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler."""
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "detail": str(exc),
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        }
    )

# For Vercel deployment
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
