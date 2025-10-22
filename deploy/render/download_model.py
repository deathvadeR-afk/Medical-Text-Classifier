#!/usr/bin/env python3
"""
Model Download Script for Render Deployment
Downloads model files from MinIO storage during build process
"""

import os
import sys
from pathlib import Path

def download_model_from_minio():
    """Download model files from MinIO storage."""
    
    try:
        from minio import Minio
        from minio.error import S3Error
    except ImportError:
        print("⚠️  MinIO client not available. Using fallback method.")
        return False
    
    # Create models directory if it doesn't exist
    model_dir = Path("models/biomedbert_model")
    model_dir.mkdir(parents=True, exist_ok=True)
    
    # MinIO configuration (these will be set as environment variables in Render)
    minio_endpoint = os.getenv("MINIO_ENDPOINT", "minio:9000")
    minio_access_key = os.getenv("MINIO_ACCESS_KEY", "minioadmin")
    minio_secret_key = os.getenv("MINIO_SECRET_KEY", "minioadmin123")
    bucket_name = os.getenv("MINIO_BUCKET", "medical-models")
    minio_secure = os.getenv("MINIO_SECURE", "false").lower() == "true"
    
    # Initialize MinIO client
    minio_client = Minio(
        minio_endpoint,
        access_key=minio_access_key,
        secret_key=minio_secret_key,
        secure=minio_secure
    )
    
    # Define model files to download
    model_files = [
        "model.pt",
        "config.json",
        "tokenizer.json",
        "vocab.txt",
        "reverse_label_mapping.json",
        "label_mapping.json",
        "special_tokens_map.json",
        "tokenizer_config.json"
    ]
    
    print("📥 Downloading model files from MinIO...")
    
    for filename in model_files:
        file_path = model_dir / filename
        if file_path.exists():
            print(f"✅ {filename} already exists")
            continue
            
        try:
            print(f"⬇️  Downloading {filename}...")
            minio_client.fget_object(
                bucket_name,
                f"biomedbert/{filename}",
                str(file_path)
            )
            print(f"✅ Downloaded {filename}")
        except S3Error as e:
            print(f"❌ Failed to download {filename}: {e}")
            return False
        except Exception as e:
            print(f"❌ Unexpected error downloading {filename}: {e}")
            return False
    
    print("🎉 All model files downloaded successfully from MinIO!")
    return True

def download_model_from_urls():
    """Fallback: Download model files from direct URLs."""
    import urllib.request
    
    # Create models directory if it doesn't exist
    model_dir = Path("models/biomedbert_model")
    model_dir.mkdir(parents=True, exist_ok=True)
    
    # Define model files to download (update with your actual URLs)
    model_files = {
        "model.pt": "YOUR_MINIO_URL/medical-models/biomedbert/model.pt",
        "config.json": "YOUR_MINIO_URL/medical-models/biomedbert/config.json",
        "tokenizer.json": "YOUR_MINIO_URL/medical-models/biomedbert/tokenizer.json",
        "vocab.txt": "YOUR_MINIO_URL/medical-models/biomedbert/vocab.txt",
        "reverse_label_mapping.json": "YOUR_MINIO_URL/medical-models/biomedbert/reverse_label_mapping.json",
        "label_mapping.json": "YOUR_MINIO_URL/medical-models/biomedbert/label_mapping.json",
        "special_tokens_map.json": "YOUR_MINIO_URL/medical-models/biomedbert/special_tokens_map.json",
        "tokenizer_config.json": "YOUR_MINIO_URL/medical-models/biomedbert/tokenizer_config.json"
    }
    
    print("📥 Downloading model files from URLs...")
    
    for filename, url in model_files.items():
        file_path = model_dir / filename
        if file_path.exists():
            print(f"✅ {filename} already exists")
            continue
            
        if url == f"YOUR_MINIO_URL/medical-models/biomedbert/{filename}":
            print(f"❌ Please update the URL for {filename} in the script")
            return False
            
        try:
            print(f"⬇️  Downloading {filename}...")
            urllib.request.urlretrieve(url, file_path)
            print(f"✅ Downloaded {filename}")
        except Exception as e:
            print(f"❌ Failed to download {filename}: {e}")
            return False
    
    print("🎉 All model files downloaded successfully from URLs!")
    return True

if __name__ == "__main__":
    # Try MinIO first, fallback to URLs
    success = download_model_from_minio()
    if not success:
        print("🔄 Falling back to URL download method...")
        success = download_model_from_urls()
    
    sys.exit(0 if success else 1)