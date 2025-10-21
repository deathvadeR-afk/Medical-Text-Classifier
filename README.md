# Medical Text Classifier App

[![Tests](https://github.com/{username}/{repo}/workflows/Tests/badge.svg)](https://github.com/{username}/{repo}/actions/workflows/test.yml)
[![Docker Build](https://github.com/{username}/{repo}/workflows/Docker%20Build%20and%20Push/badge.svg)](https://github.com/{username}/{repo}/actions/workflows/docker-build.yml)
[![codecov](https://codecov.io/gh/{username}/{repo}/branch/main/graph/badge.svg)](https://codecov.io/gh/{username}/{repo})
[![License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)

End-to-end medical text classification app built with open-source production tooling.

## 🚀 Features

- **Advanced ML Model**: Fine-tuned BiomedBERT for medical text classification (99% accuracy)
- **Production-Ready API**: FastAPI backend with comprehensive error handling
- **Modern Frontend**: React + TypeScript with glassmorphism UI
- **Database Integration**: PostgreSQL with SQLAlchemy ORM (optional)
- **Monitoring & Observability**: Prometheus metrics and Grafana dashboards
- **Comprehensive Testing**: Unit, integration, E2E, and performance tests
- **CI/CD Pipeline**: Automated testing, building, and deployment
- **Docker Support**: Containerized application with docker-compose
- **Security**: Vulnerability scanning with Trivy

## 📋 Table of Contents

- [Quick Start](#quick-start)
- [Architecture](#architecture)
- [Development](#development)
- [Testing](#testing)
- [Deployment](#deployment)
- [CI/CD](#cicd)
- [Documentation](#documentation)
- [Contributing](#contributing)

## 🏃 Quick Start

### Prerequisites

- Python 3.8+
- Node.js 18+
- Docker and Docker Compose
- PostgreSQL 13+

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/{username}/{repo}.git
   cd {repo}
   ```

2. **Set up Python environment**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Start services with Docker Compose**
   ```bash
   docker-compose up -d
   ```

4. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. **Start the API server**
   ```bash
   python -m uvicorn src.api.main:app --host 127.0.0.1 --port 8000 --reload
   ```

6. **Start the frontend** (in a new terminal)
   ```bash
   cd frontend
   npm install
   npm start
   ```

7. **Access the application**
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
│  BiomedBERT      │  │  PostgreSQL  │  │    MinIO     │
│  Model           │  │  Database    │  │  (S3 Store)  │
└──────────────────┘  └──────────────┘  └──────────────┘
```

## 💻 Development

### Project Structure

```
medical-text-classifier/
├── .github/workflows/      # CI/CD workflows
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
python run_tests.py --all --coverage --html

# Run specific test types
python run_tests.py --unit
python run_tests.py --integration
python run_tests.py --e2e
python run_tests.py --performance

# Run specific test file
python run_tests.py --file tests/unit/test_models.py

# Run with parallel execution
python run_tests.py --all -n 4
```

### Test Coverage

Current coverage: **80%+**

View detailed coverage report:
```bash
python run_tests.py --all --coverage --html
open htmlcov/index.html
```

## 🚢 Deployment

### ⚡ Quick Deploy to Vercel (Frontend + Serverless API)

```bash
# Install Vercel CLI
npm i -g vercel

# Deploy with automated script
python scripts/deploy_vercel.py

# Or deploy manually
vercel --prod
```

**Features:**
- ✅ Frontend deployed as static site
- ✅ API as serverless functions
- ✅ Automatic HTTPS and CDN
- ✅ Zero-config deployment

### 🎯 Deploy to Render (Full-Stack - Recommended)

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy?repo=https://github.com/YOUR_USERNAME/Medical-Text-Classification)

**One-click deployment to production:**

1. **Fork this repository** to your GitHub account
2. **Click the Deploy to Render button** above
3. **Configure environment variables** in Render dashboard
4. **Deploy!** 🎉

**Manual Render Setup:**
```bash
# Prepare for deployment
python deploy/render/deploy.py

# Follow the guide
open docs/RENDER_DEPLOYMENT.md
```

### Docker Deployment

```bash
# Build and run with Docker
docker build -t medical-text-classifier .
docker run -p 8000:8000 \
  -e DATABASE_URL=postgresql://user:pass@host:5432/db \
  medical-text-classifier
```

### Other Cloud Platforms

The application also supports deployment to:
- **Render.com** (recommended for simplicity)
- **Google Cloud Run**
- **AWS ECS**
- **Kubernetes**

See deployment guides:
- [Render Deployment](docs/RENDER_DEPLOYMENT.md) - Complete Render guide
- [Kubernetes Deployment](k8s/) - Kubernetes manifests
- [Docker Compose](docker-compose.prod.yml) - Production Docker setup

## 🔄 CI/CD

The project uses GitHub Actions for continuous integration and deployment:

### Workflows

1. **Tests** - Runs on every push and PR
   - Linting and type checking
   - Unit and integration tests
   - E2E tests (main branch only)
   - Coverage reporting

2. **Docker Build** - Builds and pushes Docker images
   - Multi-platform builds (amd64, arm64)
   - Security scanning with Trivy
   - Automated tagging

3. **Deploy** - Deploys to staging/production
   - Frontend deployment to Netlify
   - Backend deployment to Cloud Run/ECS/K8s
   - Smoke tests
   - Rollback on failure

### Setting Up CI/CD

1. **Configure GitHub Secrets**:
   - `NETLIFY_AUTH_TOKEN`
   - `NETLIFY_SITE_ID`
   - `GCP_SA_KEY` (for Google Cloud)
   - `DATABASE_URL`
   - `SLACK_WEBHOOK` (optional)

2. **Enable GitHub Actions**:
   - Go to repository Settings → Actions
   - Enable workflows

3. **Configure Codecov** (optional):
   - Sign up at codecov.io
   - Add `CODECOV_TOKEN` to secrets

See [CI/CD Documentation](docs/CI_CD.md) for complete setup guide.

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

### 🛡️ Security & Production
- [🔒 Security Guide](docs/SECURITY.md) - Security features and configuration
- [✅ Production Checklist](docs/PRODUCTION_CHECKLIST.md) - Pre-deployment verification
- [📊 Monitoring Guide](docs/MONITORING.md) - Observability and alerting setup

### 🚀 Deployment Options
- [☁️ Render Deployment](docs/RENDER_DEPLOYMENT.md) - **Recommended** for full-stack deployment
- [⚡ Vercel Deployment](docs/VERCEL_DEPLOYMENT.md) - **New!** Frontend + Serverless API
- [🐳 Docker Deployment](docker-compose.yml) - Local containerized deployment
- [☸️ Kubernetes Deployment](k8s/) - Cloud-native orchestration

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
