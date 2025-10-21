#!/usr/bin/env python3
"""
Render Deployment Helper Script
Medical Text Classification App

This script helps prepare your repository for Render deployment.
"""

import os
import sys
import json
import secrets
import subprocess
from pathlib import Path

def generate_secret_key(length=64):
    """Generate a secure secret key."""
    return secrets.token_urlsafe(length)

def generate_api_keys(count=3):
    """Generate secure API keys."""
    return [secrets.token_urlsafe(32) for _ in range(count)]

def check_model_files():
    """Check if required model files are present."""
    required_files = [
        'models/model.pt',
        'models/tokenizer.json',
        'models/label_mapping.json',
        'models/reverse_label_mapping.json'
    ]
    
    missing_files = []
    for file_path in required_files:
        if not os.path.exists(file_path):
            missing_files.append(file_path)
    
    return missing_files

def check_frontend_files():
    """Check if frontend files are present."""
    required_files = [
        'frontend/package.json',
        'frontend/src/App.tsx',
        'frontend/public/index.html'
    ]
    
    missing_files = []
    for file_path in required_files:
        if not os.path.exists(file_path):
            missing_files.append(file_path)
    
    return missing_files

def create_env_template():
    """Create environment variables template."""
    secret_key = generate_secret_key()
    api_keys = generate_api_keys()
    
    env_template = f"""# Render Environment Variables Template
# Copy these values to your Render service environment variables

# Application Settings
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=INFO

# Database (Auto-provided by Render when you connect PostgreSQL)
# DATABASE_URL=postgresql://user:password@host:port/database

# Security (CHANGE THESE VALUES!)
SECRET_KEY={secret_key}
REQUIRE_API_KEY=true
API_KEYS={','.join(api_keys)}

# CORS (UPDATE WITH YOUR ACTUAL DOMAINS)
ALLOWED_ORIGINS=https://medtext-frontend.onrender.com
ALLOWED_HOSTS=medtext-api.onrender.com

# Rate Limiting
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_WINDOW=3600

# Security Features
ENABLE_SECURITY_HEADERS=true
MAX_TEXT_LENGTH=5000
MIN_TEXT_LENGTH=1
LOG_REQUESTS=true
LOG_SENSITIVE_DATA=false

# Frontend Environment Variables
NODE_ENV=production
REACT_APP_API_URL=https://medtext-api.onrender.com
REACT_APP_ENVIRONMENT=production
"""
    
    with open('deploy/render/.env.template', 'w') as f:
        f.write(env_template)
    
    return secret_key, api_keys

def check_git_status():
    """Check if repository is clean and ready for deployment."""
    try:
        # Check if we're in a git repository
        subprocess.run(['git', 'status'], check=True, capture_output=True)
        
        # Check for uncommitted changes
        result = subprocess.run(['git', 'status', '--porcelain'], 
                              capture_output=True, text=True)
        
        if result.stdout.strip():
            return False, "You have uncommitted changes"
        
        return True, "Repository is clean"
    
    except subprocess.CalledProcessError:
        return False, "Not a git repository or git not available"

def main():
    """Main deployment preparation function."""
    print("🚀 Render Deployment Preparation")
    print("=" * 50)
    
    # Check current directory
    if not os.path.exists('src/api/main.py'):
        print("❌ Error: Please run this script from the project root directory")
        sys.exit(1)
    
    print("✅ Running from correct directory")
    
    # Check model files
    print("\n📁 Checking model files...")
    missing_models = check_model_files()
    if missing_models:
        print(f"❌ Missing model files: {missing_models}")
        print("   Please ensure all model files are in the models/ directory")
        print("   You may need to download them from your training environment")
    else:
        print("✅ All required model files found")
    
    # Check frontend files
    print("\n🎨 Checking frontend files...")
    missing_frontend = check_frontend_files()
    if missing_frontend:
        print(f"❌ Missing frontend files: {missing_frontend}")
        print("   Please ensure the frontend is properly set up")
    else:
        print("✅ Frontend files found")
    
    # Check git status
    print("\n📝 Checking git repository...")
    git_clean, git_message = check_git_status()
    if git_clean:
        print(f"✅ {git_message}")
    else:
        print(f"⚠️  {git_message}")
        print("   Consider committing changes before deployment")
    
    # Generate environment variables
    print("\n🔐 Generating environment variables...")
    secret_key, api_keys = create_env_template()
    print("✅ Environment template created: deploy/render/.env.template")
    
    # Create deployment summary
    print("\n📋 Deployment Summary")
    print("-" * 30)
    print(f"Secret Key: {secret_key[:20]}...")
    print(f"API Keys: {len(api_keys)} keys generated")
    print(f"Model Files: {'✅ Ready' if not missing_models else '❌ Missing'}")
    print(f"Frontend: {'✅ Ready' if not missing_frontend else '❌ Missing'}")
    print(f"Git Status: {'✅ Clean' if git_clean else '⚠️  Has changes'}")
    
    # Next steps
    print("\n🎯 Next Steps:")
    print("1. Review the environment template: deploy/render/.env.template")
    print("2. Go to https://dashboard.render.com")
    print("3. Create a new PostgreSQL database")
    print("4. Create a new Web Service for the API")
    print("5. Create a new Static Site for the frontend")
    print("6. Copy environment variables from the template")
    print("7. Follow the deployment guide: docs/RENDER_DEPLOYMENT.md")
    
    if missing_models or missing_frontend:
        print("\n⚠️  Warning: Missing files detected!")
        print("   Please resolve missing files before deployment")
        return False
    
    print("\n🎉 Repository is ready for Render deployment!")
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
