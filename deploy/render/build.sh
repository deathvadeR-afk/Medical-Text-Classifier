#!/bin/bash

# Render Build Script for Medical Text Classification API
set -e

echo "🚀 Starting Render build process..."

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Download models if not present (for first deployment)
echo "🤖 Checking for ML models..."
if [ ! -f "models/model.pt" ]; then
    echo "⚠️  Models not found. Please ensure models are included in your repository."
    echo "   You can download them from your training environment or use git-lfs."
fi

# Run any database migrations if needed
echo "🗄️  Running database setup..."
python -c "
import os
import sys
sys.path.append('.')

try:
    from src.db import engine, Base
    print('Creating database tables...')
    Base.metadata.create_all(bind=engine)
    print('✅ Database tables created successfully')
except Exception as e:
    print(f'⚠️  Database setup warning: {e}')
    print('This is normal if database is not yet available during build')
"

echo "✅ Build completed successfully!"
