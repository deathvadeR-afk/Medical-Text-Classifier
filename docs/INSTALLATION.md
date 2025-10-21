# 🛠️ Installation Guide
## Medical Text Classification App

Complete installation guide for setting up the Medical Text Classification application in development and production environments.

## 📋 Prerequisites

### System Requirements
- **Operating System**: Windows 10+, macOS 10.15+, or Linux (Ubuntu 18.04+)
- **Python**: 3.8 or higher (3.12 recommended)
- **Node.js**: 18.0 or higher
- **Memory**: 8GB RAM minimum (16GB recommended)
- **Storage**: 10GB free space
- **GPU**: Optional (CUDA-compatible for faster inference)

### Required Software
- **Git**: Version control system
- **Docker**: Container runtime (optional but recommended)
- **PostgreSQL**: 13+ (for production) or SQLite (for development)

## 🚀 Quick Installation

### Option 1: Docker Compose (Recommended)

1. **Clone the repository**:
   ```bash
   git clone https://github.com/YOUR_USERNAME/Medical-Text-Classification.git
   cd Medical-Text-Classification
   ```

2. **Start all services**:
   ```bash
   docker-compose up -d
   ```

3. **Verify installation**:
   ```bash
   # Check API health
   curl http://localhost:8000/health
   
   # Open frontend
   open http://localhost:3000
   ```

### Option 2: Local Development Setup

1. **Clone and setup Python environment**:
   ```bash
   git clone https://github.com/YOUR_USERNAME/Medical-Text-Classification.git
   cd Medical-Text-Classification
   
   # Create virtual environment
   python -m venv .medtext
   source .medtext/bin/activate  # On Windows: .medtext\Scripts\activate
   
   # Install dependencies
   pip install -r requirements.txt
   ```

2. **Setup frontend**:
   ```bash
   cd frontend
   npm install
   cd ..
   ```

3. **Start services**:
   ```bash
   # Terminal 1: Start API
   uvicorn src.api.main:app --reload --port 8000
   
   # Terminal 2: Start frontend
   cd frontend && npm start
   ```

## 🔧 Detailed Installation

### Step 1: Environment Setup

#### Python Environment
```bash
# Check Python version
python --version  # Should be 3.8+

# Create virtual environment
python -m venv .medtext

# Activate virtual environment
# On Windows:
.medtext\Scripts\activate
# On macOS/Linux:
source .medtext/bin/activate

# Upgrade pip
pip install --upgrade pip
```

#### Node.js Environment
```bash
# Check Node.js version
node --version  # Should be 18.0+
npm --version

# Install global dependencies (optional)
npm install -g create-react-app typescript
```

### Step 2: Repository Setup

```bash
# Clone repository
git clone https://github.com/YOUR_USERNAME/Medical-Text-Classification.git
cd Medical-Text-Classification

# Verify model files exist
ls -la models/
# Should contain: model.pt, tokenizer.json, label_mapping.json, etc.
```

### Step 3: Backend Installation

```bash
# Install Python dependencies
pip install -r requirements.txt

# Verify installation
python -c "import torch, transformers, fastapi; print('Dependencies installed successfully')"

# Test model loading
python -c "
import sys
sys.path.append('.')
from src.ml.model import MedicalTextClassifier
classifier = MedicalTextClassifier()
print('Model loaded successfully')
"
```

### Step 4: Frontend Installation

```bash
cd frontend

# Install dependencies
npm install

# Verify installation
npm list --depth=0

# Build for production (optional)
npm run build

cd ..
```

### Step 5: Database Setup

#### Option A: PostgreSQL (Production)
```bash
# Install PostgreSQL
# Ubuntu/Debian:
sudo apt-get install postgresql postgresql-contrib

# macOS (with Homebrew):
brew install postgresql

# Windows: Download from https://www.postgresql.org/download/

# Create database
sudo -u postgres createdb medical_db
sudo -u postgres createuser meduser
sudo -u postgres psql -c "ALTER USER meduser PASSWORD 'medpass123';"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE medical_db TO meduser;"
```

#### Option B: SQLite (Development)
```bash
# SQLite is included with Python, no additional setup needed
# Database will be created automatically
```

### Step 6: Environment Configuration

```bash
# Copy environment template
cp .env.example .env

# Edit environment variables
nano .env  # or use your preferred editor
```

**Required environment variables**:
```bash
# Application
ENVIRONMENT=development
DEBUG=true
LOG_LEVEL=INFO

# Database
DATABASE_URL=postgresql://meduser:medpass123@localhost:5432/medical_db
# Or for SQLite: DATABASE_URL=sqlite:///./medical.db

# Security (generate secure values for production)
SECRET_KEY=your-secret-key-here
REQUIRE_API_KEY=false
API_KEYS=dev-key-1,dev-key-2

# CORS
ALLOWED_ORIGINS=http://localhost:3000
ALLOWED_HOSTS=localhost,127.0.0.1

# Rate Limiting
RATE_LIMIT_REQUESTS=1000
RATE_LIMIT_WINDOW=3600
```

### Step 7: Initialize Database

```bash
# Create database tables
python -c "
import sys
sys.path.append('.')
from src.db import init_db
init_db()
print('Database initialized successfully')
"
```

### Step 8: Verification

```bash
# Test API
python -c "
import requests
response = requests.get('http://localhost:8000/health')
print(f'API Health: {response.json()}')
"

# Test model inference
python -c "
import requests
response = requests.post(
    'http://localhost:8000/predict',
    json={'text': 'What are the symptoms of diabetes?'}
)
print(f'Prediction: {response.json()}')
"
```

## 🐳 Docker Installation

### Prerequisites
- Docker 20.0+
- Docker Compose 2.0+

### Installation Steps

1. **Install Docker**:
   ```bash
   # Ubuntu/Debian
   curl -fsSL https://get.docker.com -o get-docker.sh
   sudo sh get-docker.sh
   
   # macOS/Windows: Download Docker Desktop
   # https://www.docker.com/products/docker-desktop
   ```

2. **Build and run**:
   ```bash
   # Build images
   docker-compose build
   
   # Start services
   docker-compose up -d
   
   # Check status
   docker-compose ps
   ```

3. **Verify installation**:
   ```bash
   # Check API health
   curl http://localhost:8000/health
   
   # Check frontend
   curl http://localhost:3000
   
   # View logs
   docker-compose logs api
   docker-compose logs frontend
   ```

## 🔍 Troubleshooting

### Common Issues

#### 1. Python Dependencies
```bash
# Error: No module named 'torch'
pip install torch --index-url https://download.pytorch.org/whl/cpu

# Error: Microsoft Visual C++ required (Windows)
# Install Visual Studio Build Tools or Visual Studio Community
```

#### 2. Model Loading Issues
```bash
# Error: Model files not found
# Ensure model files are in the models/ directory
ls -la models/

# Download models if missing (example)
# You may need to download from your training environment
```

#### 3. Database Connection
```bash
# Error: Could not connect to database
# Check PostgreSQL is running
sudo systemctl status postgresql

# Check connection string
psql postgresql://meduser:medpass123@localhost:5432/medical_db
```

#### 4. Frontend Issues
```bash
# Error: npm install fails
# Clear npm cache
npm cache clean --force
rm -rf node_modules package-lock.json
npm install

# Error: Port 3000 already in use
# Kill process using port
lsof -ti:3000 | xargs kill -9
```

#### 5. Docker Issues
```bash
# Error: Permission denied
sudo usermod -aG docker $USER
# Log out and log back in

# Error: Port already in use
docker-compose down
docker system prune -f
```

### Performance Optimization

#### 1. Model Loading
```bash
# Use GPU if available
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

# Verify GPU support
python -c "import torch; print(f'CUDA available: {torch.cuda.is_available()}')"
```

#### 2. Memory Optimization
```bash
# Increase Docker memory limit (Docker Desktop)
# Settings → Resources → Memory → 8GB+

# Monitor memory usage
docker stats
```

#### 3. Database Performance
```bash
# PostgreSQL optimization
sudo nano /etc/postgresql/13/main/postgresql.conf
# Increase shared_buffers, effective_cache_size
```

## 📚 Next Steps

After successful installation:

1. **Read the [API Documentation](API.md)** to understand available endpoints
2. **Explore the [Frontend Guide](FRONTEND.md)** for UI customization
3. **Review [Security Guide](SECURITY.md)** for production deployment
4. **Setup [Monitoring](MONITORING.md)** for observability
5. **Follow [Testing Guide](TESTING.md)** to run tests

## 🆘 Getting Help

If you encounter issues:

1. **Check the [Troubleshooting Guide](TROUBLESHOOTING.md)**
2. **Search [GitHub Issues](https://github.com/YOUR_USERNAME/Medical-Text-Classification/issues)**
3. **Create a new issue** with:
   - Operating system and version
   - Python and Node.js versions
   - Complete error messages
   - Steps to reproduce

---

**🎉 Installation complete! Your Medical Text Classification app is ready for development.**
