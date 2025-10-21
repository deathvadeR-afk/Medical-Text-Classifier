#!/bin/bash

# Render Start Script for Medical Text Classification API
set -e

echo "🚀 Starting Medical Text Classification API..."

# Wait for database to be ready
echo "⏳ Waiting for database connection..."
python -c "
import os
import sys
import time
import psycopg2
from psycopg2 import OperationalError

def wait_for_db():
    max_retries = 30
    retry_count = 0
    
    while retry_count < max_retries:
        try:
            conn = psycopg2.connect(
                host=os.getenv('POSTGRES_HOST'),
                port=os.getenv('POSTGRES_PORT', 5432),
                database=os.getenv('POSTGRES_DB'),
                user=os.getenv('POSTGRES_USER'),
                password=os.getenv('POSTGRES_PASSWORD')
            )
            conn.close()
            print('✅ Database connection successful!')
            return True
        except OperationalError as e:
            retry_count += 1
            print(f'⏳ Database not ready (attempt {retry_count}/{max_retries}): {e}')
            time.sleep(2)
    
    print('❌ Failed to connect to database after maximum retries')
    return False

if not wait_for_db():
    sys.exit(1)
"

# Create database tables
echo "🗄️  Setting up database tables..."
python -c "
import sys
sys.path.append('.')

try:
    from src.db import engine, Base
    print('Creating database tables...')
    Base.metadata.create_all(bind=engine)
    print('✅ Database tables created successfully')
except Exception as e:
    print(f'❌ Database setup failed: {e}')
    sys.exit(1)
"

# Verify model files
echo "🤖 Verifying ML model files..."
python -c "
import os
import sys

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

if missing_files:
    print(f'❌ Missing required model files: {missing_files}')
    print('Please ensure all model files are included in your repository.')
    sys.exit(1)
else:
    print('✅ All required model files found')
"

# Start the application
echo "🎯 Starting FastAPI application..."
exec uvicorn src.api.main:app \
    --host 0.0.0.0 \
    --port ${PORT:-8000} \
    --workers ${UVICORN_WORKERS:-4} \
    --access-log \
    --log-level info
