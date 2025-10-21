# 📚 Medical Text Classification - Documentation Hub

Welcome to the comprehensive documentation for the Medical Text Classification application. This hub provides access to all documentation needed to understand, deploy, and maintain the system.

## 🎯 Quick Navigation

### 🚀 Getting Started
- [**Quick Start Guide**](../README.md#quick-start) - Get up and running in 5 minutes
- [**Installation Guide**](INSTALLATION.md) - Detailed setup instructions
- [**Architecture Overview**](ARCHITECTURE.md) - System design and components

### 🔧 Development
- [**API Documentation**](API.md) - Complete API reference and examples
- [**Frontend Guide**](FRONTEND.md) - React application development
- [**Testing Guide**](TESTING.md) - Running and writing tests
- [**Contributing Guide**](../CONTRIBUTING.md) - How to contribute to the project

### 🛡️ Security
- [**Security Guide**](SECURITY.md) - Security features and best practices
- [**Authentication**](SECURITY.md#authentication) - API key and JWT authentication
- [**Rate Limiting**](SECURITY.md#rate-limiting) - Request throttling configuration

### 📊 Monitoring & Operations
- [**Monitoring Guide**](MONITORING.md) - Prometheus and Grafana setup
- [**Health Checks**](MONITORING.md#health-checks) - System health monitoring
- [**Troubleshooting**](TROUBLESHOOTING.md) - Common issues and solutions

### 🚢 Deployment
- [**Render Deployment**](RENDER_DEPLOYMENT.md) - Deploy to Render.com (Recommended)
- [**Docker Deployment**](DOCKER.md) - Containerized deployment
- [**Kubernetes Deployment**](../k8s/README.md) - Cloud-native deployment
- [**Production Checklist**](PRODUCTION_CHECKLIST.md) - Pre-deployment verification

### 🔄 CI/CD
- [**CI/CD Pipeline**](CI_CD.md) - GitHub Actions workflows
- [**Automated Testing**](CI_CD.md#testing) - Continuous testing setup
- [**Deployment Automation**](CI_CD.md#deployment) - Automated deployments

## 📋 Documentation Structure

```
docs/
├── README.md                    # This file - Documentation hub
├── INSTALLATION.md              # Detailed installation guide
├── ARCHITECTURE.md              # System architecture and design
├── API.md                       # Complete API documentation
├── FRONTEND.md                  # Frontend development guide
├── TESTING.md                   # Testing strategies and guides
├── SECURITY.md                  # Security implementation guide
├── MONITORING.md                # Monitoring and observability
├── TROUBLESHOOTING.md           # Common issues and solutions
├── RENDER_DEPLOYMENT.md         # Render.com deployment guide
├── DOCKER.md                    # Docker deployment guide
├── PRODUCTION_CHECKLIST.md      # Production readiness checklist
├── CI_CD.md                     # CI/CD pipeline documentation
├── PERFORMANCE.md               # Performance optimization guide
├── MAINTENANCE.md               # Ongoing maintenance procedures
└── CHANGELOG.md                 # Version history and changes
```

## 🎯 Quick Reference

### Essential Commands
```bash
# Development
make install          # Install dependencies
make dev             # Start development environment
make test            # Run all tests
make lint            # Run code quality checks

# Production
make build           # Build production images
make deploy          # Deploy to production
make monitor         # Open monitoring dashboard
```

### Key URLs (Development)
- **Frontend**: http://localhost:3000
- **API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health
- **Metrics**: http://localhost:8000/metrics
- **Grafana**: http://localhost:3001
- **Prometheus**: http://localhost:9090

### Key URLs (Production)
- **Frontend**: https://medtext-frontend.onrender.com
- **API**: https://medtext-api.onrender.com
- **API Docs**: https://medtext-api.onrender.com/docs
- **Health Check**: https://medtext-api.onrender.com/health

## 🏗️ System Components

### Core Services
1. **FastAPI Backend** - ML model serving and API endpoints
2. **React Frontend** - User interface for text classification
3. **PostgreSQL Database** - Query logging and user data
4. **Prometheus** - Metrics collection and monitoring
5. **Grafana** - Visualization and alerting dashboards

### ML Pipeline
1. **BiomedBERT Model** - Fine-tuned medical text classifier (99% accuracy)
2. **Tokenizer** - Text preprocessing and tokenization
3. **Label Mapping** - Classification categories and focus groups
4. **Inference Engine** - Real-time prediction serving

### Security Layer
1. **API Key Authentication** - Production access control
2. **Rate Limiting** - Request throttling and abuse prevention
3. **Input Validation** - XSS and injection protection
4. **Security Headers** - CORS, CSP, and security policies

## 🎯 Focus Groups Classification

The system classifies medical text into 5 focus groups:

| Class | Focus Group | Examples |
|-------|-------------|----------|
| 0 | Neurological & Cognitive Disorders | Alzheimer's, Parkinson's, dementia |
| 1 | Cancers | Breast cancer, lung cancer, oncology |
| 2 | Cardiovascular Diseases | Heart disease, hypertension, stroke |
| 3 | Metabolic & Endocrine Disorders | Diabetes, thyroid, metabolism |
| 4 | Other Age-Related & Immune Disorders | Arthritis, autoimmune, aging |

## 📊 Performance Metrics

### Model Performance
- **Accuracy**: 99% on test dataset
- **Inference Time**: <100ms per request
- **Throughput**: 1000+ requests/minute
- **Model Size**: ~400MB (BiomedBERT base)

### System Performance
- **API Response Time**: <200ms (95th percentile)
- **Frontend Load Time**: <2s (first contentful paint)
- **Database Query Time**: <50ms (average)
- **Memory Usage**: <2GB (API container)

## 🔍 Health Monitoring

### Health Check Endpoints
- **API Health**: `/health` - Overall system health
- **Database Health**: `/health/db` - Database connectivity
- **Model Health**: `/health/model` - ML model status
- **Dependencies**: `/health/deps` - External dependencies

### Key Metrics
- **Request Rate**: Requests per second
- **Error Rate**: 4xx/5xx response percentage
- **Response Time**: Request latency percentiles
- **Resource Usage**: CPU, memory, disk utilization

## 🆘 Getting Help

### Documentation Issues
If you find issues with the documentation:
1. Check the [Troubleshooting Guide](TROUBLESHOOTING.md)
2. Search existing [GitHub Issues](https://github.com/YOUR_USERNAME/Medical-Text-Classification/issues)
3. Create a new issue with the `documentation` label

### Technical Support
For technical issues:
1. Review the relevant documentation section
2. Check the [FAQ](TROUBLESHOOTING.md#faq)
3. Join our [Discord Community](https://discord.gg/YOUR_INVITE)
4. Open a GitHub issue with detailed information

### Contributing
Want to improve the documentation?
1. Read the [Contributing Guide](../CONTRIBUTING.md)
2. Fork the repository
3. Make your improvements
4. Submit a pull request

---

## 🎉 Welcome to Medical Text Classification!

This documentation hub is your gateway to understanding and working with our production-grade medical text classification system. Whether you're a developer, operator, or user, you'll find the information you need to be successful.

**Start with the [Quick Start Guide](../README.md#quick-start) and explore from there!**
