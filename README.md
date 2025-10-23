# Medical Text Classifier App

[![CI/CD](https://github.com/{username}/{repo}/workflows/CI/CD%20Pipeline/badge.svg)](https://github.com/{username}/{repo}/actions/workflows/ci-cd.yml)
[![codecov](https://codecov.io/gh/{username}/{repo}/branch/main/graph/badge.svg)](https://codecov.io/gh/{username}/{repo})
[![License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)

Medical text classification app for local development and testing.

## 🚀 Features

- **Advanced ML Model**: Fine-tuned BiomedBERT for medical text classification (99% accuracy)
- **Local API**: FastAPI backend with comprehensive error handling
- **Modern Frontend**: React + TypeScript with glassmorphism UI
- **Database Integration**: PostgreSQL with SQLAlchemy ORM (optional)
- **Monitoring & Observability**: Prometheus metrics and Grafana dashboards
- **Comprehensive Testing**: Unit, integration, E2E, and performance tests
- **Docker Support**: Containerized application with docker-compose

## 📋 Table of Contents

- [Quick Start](#quick-start)
- [Architecture](#architecture)
- [Development](#development)
- [Testing](#testing)
- [Documentation](#documentation)
- [Contributing](#contributing)

## 🏃 Quick Start

### Prerequisites

- Python 3.8+
- Node.js 18+
- Docker and Docker Compose
- PostgreSQL 13+ (optional)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/deathvadeR-afk/Medical-Text-Classifier.git
   cd Medical-Text-Classifier
   ```

2. **Set up Python environment**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Download the BiomedBERT Model**
   Download the fine-tuned BiomedBERT model from [Google Drive](https://drive.google.com/file/d/1obgzof33fehbGQWbFZJEwYzgGvrkCaHb/view?usp=sharing)
   
   Extract the model files and place them in the `models/` folder. The folder structure should look like:
   ```
   models/
   ├── model.pt
   ├── reverse_label_mapping.json
   └── config.json
   ```

4. **Start services with Docker Compose**
   ```bash
   docker-compose up -d
   ```

5. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

6. **Start the API server**
   ```bash
   python -m uvicorn src.api.main:app --host 127.0.0.1 --port 8000 --reload
   ```

7. **Start the frontend** (in a new terminal)
   ```bash
   cd frontend
   npm install
   npm start
   ```

8. **Access the application**
   - Frontend: http://localhost:3000
   - API: http://localhost:8000
   - API Docs: http://localhost:8000/docs
   - Monitoring: http://localhost:3001 (Grafana)
   - Metrics: http://localhost:9090 (Prometheus)

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        Frontend (React)                      │
│                     http://localhost:3001                    │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                    FastAPI Backend                           │
│                  http://localhost:8000                       │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   Inference  │  │   Database   │  │    MLflow    │      │
│  │    Engine    │  │   Operations │  │   Tracking   │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└──────────┬──────────────────┬──────────────────┬────────────┘
           │                  │                  │
           ▼                  ▼                  ▼
┌──────────────────┐  ┌──────────────┐  ┌──────────────┐
│  BiomedBERT      │  │  PostgreSQL  │  │  MinIO     │
│  Model           │  │  Database    │  │  (S3 Store)  │
└──────────────────┘  └──────────────┘  └──────────────┘
```

## 💻 Development

### Project Structure

```
medical-text-classifier/
├── data/                   # Data files (DVC tracked)
├── docs/                   # Documentation
├── frontend/               # React frontend
├── models/                 # Trained models
├── src/                    # Source code
│   ├── api/               # FastAPI application
│   └── db.py              # Database models
├── tests/                  # Test suite
│   ├── unit/              # Unit tests
│   ├── integration/       # Integration tests
│   ├── e2e/               # End-to-end tests
│   └── performance/       # Performance tests
├── docker-compose.yml      # Docker services
├── Dockerfile             # API container
├── Makefile               # Development commands
└── requirements.txt       # Python dependencies
```

### Development Commands

```bash
# Install dependencies
make requirements

# Run linting
make lint

# Format code
make format

# Run tests
make test-unit          # Unit tests only
make test-integration   # Integration tests only
make test-all          # All tests with coverage

# Docker commands
make docker-build      # Build Docker image
make docker-run        # Run container
make docker-up         # Start all services
make docker-down       # Stop all services

# Pre-commit checks
make pre-commit        # Format, lint, and test
```

## 🧪 Testing

The project includes comprehensive test coverage:

- **Unit Tests**: Test individual components in isolation
- **Integration Tests**: Test API endpoints and database operations
- **E2E Tests**: Test complete user workflows
- **Performance Tests**: Benchmark API response times

### Running Tests

```bash
# Run all tests with coverage
python -m pytest tests/ --cov=src --cov-report=html

# Run specific test types
python -m pytest tests/unit/
python -m pytest tests/integration/
python -m pytest tests/e2e/

# Run specific test file
python -m pytest tests/unit/test_models.py
```

### Test Coverage

Current coverage: **80%+**

View detailed coverage report:
```bash
python -m pytest tests/ --cov=src --cov-report=html
open htmlcov/index.html
```

## 📚 Documentation

### 🚀 Getting Started
- [📖 Documentation Hub](docs/README.md) - Complete documentation navigation
- [⚡ Installation Guide](docs/INSTALLATION.md) - Complete setup instructions
- [🏗️ Architecture Overview](docs/ARCHITECTURE.md) - System design and components
- [🔌 API Documentation](docs/API.md) - REST API reference and examples

### 🔧 Development & Operations
- [⚛️ Frontend Development](docs/FRONTEND.md) - React development guide
- [🧪 Testing Guide](docs/TESTING.md) - Comprehensive testing strategy
- [🔧 Troubleshooting](docs/TROUBLESHOOTING.md) - Common issues and solutions

### 🛡️ Local Development
- [🔒 Security Guide](docs/SECURITY.md) - Security features and configuration
- [📊 Monitoring Guide](docs/MONITORING.md) - Observability and alerting setup

### 🔗 Quick Links
- [🌐 Interactive API Docs](http://localhost:8000/docs) - Swagger UI (when running locally)
- [📈 Metrics Dashboard](http://localhost:3001) - Grafana (when running locally)
- [🔍 Integration Verification](scripts/verify_integration.py) - System health check

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run tests (`make pre-commit`)
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- BiomedBERT model by Microsoft
- FastAPI framework
- React and TypeScript communities
- All open-source contributors

## 📧 Contact

For questions or support, please open an issue on GitHub.