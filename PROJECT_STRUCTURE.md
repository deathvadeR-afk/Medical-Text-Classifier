# Medical Text Classification - Project Structure

## 📁 **Current Project Structure**

```
medical-text-classification/
├── .env.example                    # Environment configuration template
├── .gitignore                      # Git ignore rules
├── .dockerignore                   # Docker ignore rules
├── docker-compose.yml              # Docker services configuration
├── Dockerfile                      # API container configuration
├── LICENSE                         # Project license
├── Makefile                        # Build and development commands
├── README.md                       # Project documentation
├── requirements.txt                # Python dependencies
├── requirements-test.txt           # Testing dependencies
├── pytest.ini                     # Pytest configuration
├── pyproject.toml                  # Python project configuration
├── PROJECT_STRUCTURE.md            # This file
│
├── 📂 data/                        # Data directory
│   ├── external/                   # External data sources
│   ├── interim/                    # Intermediate processed data
│   ├── processed/                  # Final processed data
│   ├── raw/                        # Raw data files
│   └── medical_texts.csv           # Medical text dataset
│
├── 📂 docs/                        # Documentation
│   ├── README.md                   # Documentation index
│   ├── CI_CD.md                    # CI/CD pipeline documentation
│   ├── CI_CD_QUICK_REFERENCE.md    # Quick CI/CD reference
│   ├── COLAB_TRAINING_GUIDE.md     # Model training guide
│   ├── MONITORING.md               # Monitoring setup guide
│   └── SECURITY.md                 # Security implementation guide
│
├── 📂 frontend/                    # React frontend application
│   ├── public/                     # Static assets
│   ├── src/                        # React source code
│   ├── package.json                # Node.js dependencies
│   ├── package-lock.json           # Dependency lock file
│   └── tsconfig.json               # TypeScript configuration
│
├── 📂 models/                      # Trained model artifacts
│   ├── model.pt                    # PyTorch model weights
│   ├── tokenizer.json              # Tokenizer configuration
│   ├── tokenizer_config.json       # Tokenizer settings
│   ├── vocab.txt                   # Vocabulary file
│   ├── special_tokens_map.json     # Special tokens mapping
│   ├── label_mapping.json          # Label to ID mapping
│   └── reverse_label_mapping.json  # ID to label mapping
│
├── 📂 monitoring/                  # Monitoring and observability
│   ├── prometheus.yml              # Prometheus configuration
│   ├── alert_rules.yml             # Alerting rules
│   └── grafana/                    # Grafana dashboards and config
│       ├── dashboards/             # Dashboard definitions
│       └── provisioning/           # Grafana provisioning config
│
├── 📂 notebooks/                   # Jupyter notebooks
│   ├── Classifying_medical_text.ipynb     # Original research notebook
│   └── Train_BiomedBERT_Colab.ipynb       # Colab training notebook
│
├── 📂 src/                         # Source code
│   ├── __init__.py                 # Package initialization
│   ├── db.py                       # Database models and connection
│   └── api/                        # FastAPI application
│       ├── __init__.py             # API package initialization
│       ├── main.py                 # FastAPI application entry point
│       ├── models.py               # Pydantic request/response models
│       ├── inference.py            # ML model inference logic
│       ├── security.py             # Security configuration and utilities
│       └── middleware.py           # Security middleware implementations
│
└── 📂 tests/                       # Test suite
    ├── __init__.py                 # Test package initialization
    ├── conftest.py                 # Pytest configuration and fixtures
    ├── test_data.py                # Test data utilities
    ├── README.md                   # Testing documentation
    ├── unit/                       # Unit tests
    ├── integration/                # Integration tests
    ├── e2e/                        # End-to-end tests
    ├── performance/                # Performance tests
    └── security/                   # Security tests
        └── test_security.py        # Comprehensive security tests
```

## 🏗️ **Architecture Overview**

### **Core Components**

1. **FastAPI Backend** (`src/api/`)
   - RESTful API with automatic OpenAPI documentation
   - ML model inference endpoints
   - Comprehensive security middleware stack
   - Health checks and monitoring endpoints

2. **React Frontend** (`frontend/`)
   - Modern TypeScript-based React application
   - User-friendly interface for medical text classification
   - Real-time prediction results with confidence scores

3. **BiomedBERT Model** (`models/`)
   - Fine-tuned microsoft/BiomedNLP-BiomedBERT-base-uncased-abstract-fulltext
   - 99% accuracy on medical text classification
   - 5-class focus group classification system

4. **PostgreSQL Database**
   - Stores user queries and prediction history
   - No sensitive medical data storage
   - Query analytics and usage tracking

5. **Security Layer** (`src/api/security.py`, `src/api/middleware.py`)
   - Rate limiting and DDoS protection
   - Input validation and sanitization
   - API key authentication (optional)
   - Comprehensive security headers
   - Request logging and monitoring

6. **Monitoring Stack** (`monitoring/`)
   - Prometheus metrics collection
   - Grafana dashboards for visualization
   - Alerting rules for critical events
   - Performance and security monitoring

### **Data Flow**

```
User Input → Frontend → FastAPI → Security Middleware → Model Inference → Database → Response
```

### **Security Architecture**

```
Request → Input Sanitization → Host Validation → Security Headers → Request Logging → Rate Limiting → CORS → API Endpoints
```

## 🔧 **Key Features**

### **✅ Completed Features**

- **High-Accuracy ML Model**: 99% accuracy BiomedBERT classification
- **FastAPI Backend**: API with comprehensive error handling
- **Modern Frontend**: React TypeScript application
- **Comprehensive Security**: Rate limiting, input validation, security headers
- **Full Monitoring**: Prometheus + Grafana observability stack
- **Complete Testing**: Unit, integration, E2E, and security tests
- **CI/CD Pipeline**: GitHub Actions automated workflows
- **Docker Support**: Multi-service containerized development
- **Documentation**: Comprehensive guides and API documentation

### **🎯 Focus Groups Classification**

The model classifies medical text into 5 focus groups:

0. **Neurological & Cognitive Disorders**
1. **Cancers**
2. **Cardiovascular Diseases**
3. **Metabolic & Endocrine Disorders**
4. **Other Age-Related & Immune Disorders**

### **🔒 Security Features**

- **Rate Limiting**: Configurable request limits per client
- **Input Validation**: XSS, SQL injection, and malicious pattern detection
- **API Key Authentication**: Optional authentication
- **Security Headers**: CSRF, XSS, clickjacking protection
- **Host Validation**: DNS rebinding attack prevention
- **Request Logging**: Comprehensive security event logging
- **CORS Configuration**: Proper cross-origin resource sharing

### **📊 Monitoring Features**

- **API Metrics**: Request rates, response times, error rates
- **Model Performance**: Prediction confidence, classification distribution
- **Security Metrics**: Rate limit violations, security events
- **System Health**: Database connectivity, model loading status
- **Custom Dashboards**: Real-time visualization and alerting

## 🚀 **Running Locally**

### **Development**
```bash
# Start all services
docker-compose up -d

# Start API only
python -m uvicorn src.api.main:app --reload

# Start frontend
cd frontend && npm start
```

### **Accessing the Application**
```bash
# Access services
# API: http://localhost:8000
# Frontend: http://localhost:3000
# Grafana: http://localhost:3001
# Prometheus: http://localhost:9090
```

## 📈 **Performance**

- **Model Accuracy**: 99% on medical text classification
- **API Response Time**: < 2 seconds per prediction
- **Throughput**: 100+ requests per minute (configurable)
- **Memory Usage**: ~2GB for model + API
- **Startup Time**: ~30 seconds for model loading

## 🧪 **Testing**

```bash
# Run all tests
pytest

# Run specific test suites
pytest tests/unit/ -v           # Unit tests
pytest tests/integration/ -v    # Integration tests
pytest tests/security/ -v       # Security tests
pytest tests/e2e/ -v           # End-to-end tests
```

## 📝 **Learning and Development**

1. **Model Exploration**: Experiment with different text inputs
2. **Performance Optimization**: Model quantization and caching
3. **Advanced Analytics**: User behavior and prediction analytics
4. **API Usage**: Learn how to integrate with other applications
5. **Security Features**: Understand rate limiting and input validation
6. **Monitoring**: Learn to interpret metrics and dashboards

---

**🎉 The Medical Text Classification application is ready for local development and learning with 99% model accuracy, comprehensive security, full monitoring, and complete documentation!**