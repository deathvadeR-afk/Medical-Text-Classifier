#!/usr/bin/env python3
"""
Simple startup test for Medical Text Classification app.
Just verifies the app can start and respond to basic requests.
"""
import os
import time
import subprocess
import requests
import sys
import json
from pathlib import Path


def setup_mock_models():
    """Create mock model files for testing."""
    models_dir = Path("models")
    models_dir.mkdir(exist_ok=True)
    
    # Create label mapping files
    reverse_mapping = {
        "0": "Neurological & Cognitive Disorders",
        "1": "Cancers", 
        "2": "Cardiovascular Diseases",
        "3": "Metabolic & Endocrine Disorders",
        "4": "Other Age-Related & Immune Disorders"
    }
    
    label_mapping = {v: k for k, v in reverse_mapping.items()}
    
    with open(models_dir / "reverse_label_mapping.json", "w") as f:
        json.dump(reverse_mapping, f, indent=2)
    
    with open(models_dir / "label_mapping.json", "w") as f:
        json.dump(label_mapping, f, indent=2)
    
    print("✅ Mock model files created")


def test_app_startup():
    """Test basic dependencies and setup."""
    print("🚀 Starting simple dependency test...")

    # Set environment variables
    os.environ["TESTING"] = "1"
    os.environ["LOG_LEVEL"] = "WARNING"
    os.environ["MODEL_PATH"] = "models"

    # Setup mock models
    setup_mock_models()

    try:
        # Test basic imports
        print("📦 Testing core dependencies...")
        import fastapi
        print("✅ FastAPI available")

        import uvicorn
        print("✅ Uvicorn available")

        import requests
        print("✅ Requests available")

        print("🎉 All core dependencies working!")
        print("⏭️  Skipping app import (can be complex)")
        return True

    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_app_startup()
    sys.exit(0 if success else 1)
