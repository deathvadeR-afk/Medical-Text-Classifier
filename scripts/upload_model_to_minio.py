#!/usr/bin/env python3
"""
Upload Model Files to MinIO Storage
"""

import os
from minio import Minio
from minio.error import S3Error
import sys
from pathlib import Path

def upload_model_to_minio():
    """Upload model files to MinIO storage."""
    
    # MinIO configuration (using the correct credentials from your .env)
    minio_client = Minio(
        "localhost:9000",  # MinIO server endpoint
        access_key="minioadmin",  # Default MinIO credentials
        secret_key="minioadmin123",  # Updated from your .env file
        secure=False  # Set to True if using HTTPS
    )
    
    bucket_name = "medical-models"
    model_dir = Path("models/biomedbert_model")
    
    # Create bucket if it doesn't exist
    try:
        if not minio_client.bucket_exists(bucket_name):
            minio_client.make_bucket(bucket_name)
            print(f"✅ Created bucket: {bucket_name}")
        else:
            print(f"✅ Bucket already exists: {bucket_name}")
    except S3Error as e:
        print(f"❌ Error creating bucket: {e}")
        return False
    
    # Upload model files
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
    
    print("📤 Uploading model files to MinIO...")
    
    for filename in model_files:
        file_path = model_dir / filename
        if not file_path.exists():
            print(f"⚠️  File not found: {file_path}")
            continue
            
        try:
            minio_client.fput_object(
                bucket_name,
                f"biomedbert/{filename}",
                str(file_path)
            )
            print(f"✅ Uploaded: {filename}")
        except S3Error as e:
            print(f"❌ Failed to upload {filename}: {e}")
            return False
    
    print("🎉 All model files uploaded successfully!")
    print(f"🔗 Access URLs:")
    for filename in model_files:
        print(f"   http://localhost:9000/{bucket_name}/biomedbert/{filename}")
    
    return True

if __name__ == "__main__":
    success = upload_model_to_minio()
    sys.exit(0 if success else 1)