#!/usr/bin/env python3
"""
Ultra-simple test that just checks basic imports work.
"""
import os
import sys

def main():
    print("🚀 Starting ultra-simple test...")
    
    # Set environment variables
    os.environ["TESTING"] = "1"
    os.environ["LOG_LEVEL"] = "WARNING"
    os.environ["MODEL_PATH"] = "models"
    
    try:
        print("📦 Testing basic imports...")
        
        # Test FastAPI import
        import fastapi
        print("✅ FastAPI imported")
        
        # Test our basic modules
        from src.api import models
        print("✅ API models imported")
        
        from src.api import security
        print("✅ Security module imported")
        
        print("🎉 All basic imports work!")
        return True
        
    except Exception as e:
        print(f"❌ Import failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
