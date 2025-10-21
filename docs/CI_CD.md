# CI/CD Pipeline Documentation

## Overview

This project uses GitHub Actions for continuous integration and continuous deployment (CI/CD). The pipeline includes automated testing, Docker image building, security scanning, and deployment to multiple platforms.

## Pipeline Architecture

```
┌─────────────────┐
│  Code Push/PR   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Test Pipeline  │
│  - Lint         │
│  - Type Check   │
│  - Unit Tests   │
│  - Integration  │
│  - E2E Tests    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Docker Build    │
│  - Build Image  │
│  - Security Scan│
│  - Push to Reg  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   Deployment    │
│  - Frontend     │
│  - Backend API  │
│  - Smoke Tests  │
└─────────────────┘
```

## Workflows

### 1. Test Workflow (`.github/workflows/test.yml`)

**Triggers:**
- Push to `main` or `develop` branches
- Pull requests to `main` or `develop`

**Jobs:**

#### a. Unit & Integration Tests
- **Matrix Testing:** Python 3.8, 3.9, 3.10, 3.11
- **Services:** PostgreSQL 13
- **Steps:**
  1. Checkout code
  2. Set up Python environment
  3. Cache pip dependencies
  4. Install dependencies
  5. Run linting (flake8)
  6. Run type checking (mypy)
  7. Run security checks (bandit)
  8. Run unit tests with coverage
  9. Run integration tests with coverage
  10. Upload coverage to Codecov
  11. Upload test results as artifacts

#### b. End-to-End Tests
- **Runs:** Only on push to `main`
- **Services:** PostgreSQL 13
- **Steps:**
  1. Set up Python and Node.js
  2. Install backend and frontend dependencies
  3. Build frontend
  4. Start API server
  5. Start frontend server
  6. Run E2E tests
  7. Upload test results

#### c. Performance Tests
- **Runs:** Only on push to `main`
- **Steps:**
  1. Set up Python environment
  2. Install dependencies
  3. Run performance benchmarks
  4. Upload results

### 2. Docker Build Workflow (`.github/workflows/docker-build.yml`)

**Triggers:**
- Push to `main` or `develop` branches
- Tags matching `v*`
- Pull requests to `main`
- Manual workflow dispatch

**Jobs:**

#### a. Build and Push
- **Steps:**
  1. Checkout repository
  2. Set up Docker Buildx
  3. Log in to GitHub Container Registry
  4. Extract metadata (tags, labels)
  5. Build and push multi-platform image (amd64, arm64)
  6. Run Trivy vulnerability scanner
  7. Upload security results to GitHub Security

**Image Tags:**
- `latest` - Latest commit on main branch
- `develop` - Latest commit on develop branch
- `v1.2.3` - Semantic version tags
- `sha-abc123` - Commit SHA tags

#### b. Test Image
- **Runs:** After successful build (not on PRs)
- **Steps:**
  1. Pull built Docker image
  2. Run container with test database
  3. Test API endpoints (health, docs, predict)
  4. Check container logs
  5. Clean up

### 3. Deployment Workflow (`.github/workflows/deploy.yml`)

**Triggers:**
- Push to `main` branch
- Tags matching `v*`
- Manual workflow dispatch with environment selection

**Jobs:**

#### a. Deploy Frontend
- **Platform:** Netlify
- **Steps:**
  1. Checkout code
  2. Set up Node.js
  3. Install dependencies
  4. Build frontend with production API URL
  5. Deploy to Netlify
  6. Enable PR comments and commit comments

**Required Secrets:**
- `NETLIFY_AUTH_TOKEN`
- `NETLIFY_SITE_ID`
- `API_URL` (optional, defaults to localhost)

#### b. Deploy Backend
- **Platforms:** Google Cloud Run, AWS ECS, or Kubernetes
- **Environment:** Staging or Production (manual selection)
- **Steps:**
  1. Checkout code
  2. Log in to container registry
  3. Determine image tag
  4. Deploy to selected platform
  5. Run smoke tests
  6. Notify deployment status (Slack)

**Deployment Options:**

**Google Cloud Run:**
```yaml
Required Secrets:
- GCP_PROJECT_ID
- GCP_SA_KEY
- DATABASE_URL
- MLFLOW_TRACKING_URI
- MINIO_ENDPOINT
- MINIO_ACCESS_KEY
- MINIO_SECRET_KEY
```

**AWS ECS:**
```yaml
Required Secrets:
- AWS_ACCOUNT_ID
- AWS_ACCESS_KEY_ID
- AWS_SECRET_ACCESS_KEY
```

**Kubernetes:**
```yaml
Required Secrets:
- KUBE_CONFIG (base64 encoded)
```

#### c. Rollback
- **Runs:** On deployment failure
- **Steps:**
  1. Execute rollback logic
  2. Notify team via Slack

## Local Development

### Running Tests Locally

```bash
# Run all tests
make test-all

# Run unit tests only
make test-unit

# Run integration tests only
make test-integration

# Run with coverage report
python run_tests.py --all --coverage --html
```

### Docker Commands

```bash
# Build Docker image
make docker-build

# Run Docker container
make docker-run

# View logs
make docker-logs

# Stop container
make docker-stop

# Start all services (PostgreSQL, MinIO)
make docker-up

# Stop all services
make docker-down
```

### Pre-commit Checks

```bash
# Run all pre-commit checks
make pre-commit

# This runs:
# - Code formatting (ruff)
# - Linting (ruff)
# - Unit tests
```

### CI Pipeline Locally

```bash
# Run full CI pipeline
make ci

# This runs:
# - Clean compiled files
# - Linting
# - All tests with coverage
```

## Environment Variables

### Required for CI/CD

**GitHub Secrets:**
- `GITHUB_TOKEN` - Automatically provided by GitHub Actions
- `CODECOV_TOKEN` - For uploading coverage reports (optional)

**Deployment Secrets:**
- `NETLIFY_AUTH_TOKEN` - Netlify authentication
- `NETLIFY_SITE_ID` - Netlify site identifier
- `GCP_PROJECT_ID` - Google Cloud project ID
- `GCP_SA_KEY` - Google Cloud service account key
- `DATABASE_URL` - Production database connection string
- `MLFLOW_TRACKING_URI` - MLflow tracking server URL
- `MINIO_ENDPOINT` - MinIO endpoint URL
- `MINIO_ACCESS_KEY` - MinIO access key
- `MINIO_SECRET_KEY` - MinIO secret key
- `SLACK_WEBHOOK` - Slack webhook for notifications

### Required for Local Development

```bash
# Database
DATABASE_URL=postgresql://meduser:medpass123@localhost:5432/medical_db

# MLflow
MLFLOW_TRACKING_URI=http://localhost:5000

# MinIO
MINIO_ENDPOINT=localhost:9000
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin123

# Testing
TESTING=1
LOG_LEVEL=WARNING
```

## Monitoring and Notifications

### Coverage Reports
- Uploaded to Codecov after each test run
- Available in PR comments
- Viewable at: `https://codecov.io/gh/{username}/{repo}`

### Security Scanning
- Trivy scans Docker images for vulnerabilities
- Results uploaded to GitHub Security tab
- Critical vulnerabilities fail the build

### Deployment Notifications
- Slack notifications on deployment success/failure
- PR comments for Netlify deployments
- GitHub deployment status updates

## Best Practices

1. **Always run tests locally before pushing:**
   ```bash
   make pre-commit
   ```

2. **Use semantic versioning for releases:**
   ```bash
   git tag -a v1.2.3 -m "Release version 1.2.3"
   git push origin v1.2.3
   ```

3. **Review security scan results:**
   - Check GitHub Security tab regularly
   - Address critical vulnerabilities immediately

4. **Monitor deployment status:**
   - Check Slack notifications
   - Verify smoke tests pass
   - Monitor application logs

5. **Use feature branches:**
   ```bash
   git checkout -b feature/new-feature
   # Make changes
   git push origin feature/new-feature
   # Create PR to develop
   ```

## Troubleshooting

### Tests Failing in CI but Passing Locally
- Check Python version compatibility
- Verify environment variables are set correctly
- Check for race conditions in tests
- Review CI logs for specific errors

### Docker Build Failures
- Check Dockerfile syntax
- Verify all required files are included
- Check .dockerignore is not excluding needed files
- Review build logs for specific errors

### Deployment Failures
- Verify all required secrets are set
- Check deployment platform status
- Review deployment logs
- Verify database connectivity
- Check resource limits

### Coverage Drops
- Identify uncovered code in Codecov report
- Add tests for new features
- Remove dead code
- Update test fixtures

## Additional Resources

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Docker Documentation](https://docs.docker.com/)
- [Netlify Documentation](https://docs.netlify.com/)
- [Google Cloud Run Documentation](https://cloud.google.com/run/docs)
- [Pytest Documentation](https://docs.pytest.org/)

