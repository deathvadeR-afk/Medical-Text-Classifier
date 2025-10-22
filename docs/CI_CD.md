# CI/CD Pipeline Documentation

## Overview

This document explains the simplified CI/CD pipeline for the Medical Text Classification application. The pipeline consolidates all functionality from the previous four separate workflows into a single, more maintainable workflow.

## Pipeline Structure

The simplified pipeline consists of a single workflow file: [.github/workflows/ci-cd.yml](../.github/workflows/ci-cd.yml)

### Jobs

1. **test-and-quality** - Code quality checks and testing
2. **build-and-scan** - Docker image building and security scanning
3. **test-image** - Docker image validation
4. **deploy** - Application deployment

## Workflow Details

### 1. Test and Quality (`test-and-quality`)

This job combines all testing and code quality checks:

- **Matrix Testing**: Runs on Python versions 3.9 and 3.11
- **Code Quality Checks**:
  - Python linting with Ruff and Flake8
  - Code formatting with Black and isort
  - Type checking with MyPy
  - Security scanning with Bandit
- **Testing**:
  - Unit tests
  - Integration tests
  - Coverage reporting to Codecov

### 2. Build and Scan (`build-and-scan`)

This job handles Docker image building and security scanning:

- **Docker Build**: Multi-stage build using Buildx
- **Image Push**: Pushes to GitHub Container Registry (GHCR)
- **Security Scan**: Vulnerability scanning with Trivy
- **Metadata**: Automated tagging based on Git references

### 3. Test Image (`test-image`)

This job validates the built Docker image:

- **Image Pull**: Pulls the built image from GHCR
- **Container Run**: Starts the container with test configuration
- **Health Checks**: Validates container health endpoints
- **API Testing**: Tests key API endpoints
- **Logs**: Captures container logs for debugging

### 4. Deploy (`deploy`)

This job handles application deployment:

- **Platform Support**: Google Cloud Run, AWS ECS, Kubernetes
- **Environment**: Staging/Production deployment
- **Smoke Tests**: Validates deployment health
- **Notifications**: Slack notifications on deployment status

## Triggers

The pipeline is triggered by:

- **Push** to `main` and `develop` branches
- **Pull Requests** to `main` and `develop` branches
- **Tags** matching pattern `v*`
- **Manual Dispatch** via GitHub Actions UI

## Environment Variables

Key environment variables used in the pipeline:

- `REGISTRY`: Container registry (GHCR)
- `IMAGE_NAME`: Repository name for Docker images

## Secrets

Required secrets for full functionality:

- `GCP_SA_KEY`: Google Cloud service account key for Cloud Run deployment
- `DATABASE_URL`: Database connection string
- `SLACK_WEBHOOK`: Slack webhook URL for notifications

## Benefits of Simplification

1. **Reduced Complexity**: Single workflow file instead of four separate files
2. **Improved Maintainability**: Easier to understand and modify
3. **Better Performance**: Reduced duplication of steps
4. **Clearer Dependencies**: Explicit job dependencies make the flow obvious
5. **Faster Execution**: Eliminates redundant setup steps

## Migration from Previous Pipeline

If you were using the previous four-workflow system:

1. **Tests** → Integrated into `test-and-quality`
2. **Code Quality** → Integrated into `test-and-quality`
3. **Docker Build** → `build-and-scan` job
4. **Deploy** → `deploy` job

All functionality has been preserved while reducing complexity.
