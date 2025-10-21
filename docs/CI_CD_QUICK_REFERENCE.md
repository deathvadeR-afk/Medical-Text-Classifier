# CI/CD Quick Reference Card

## 🚀 Quick Commands

### Local Development
```bash
# Setup
make requirements              # Install dependencies
make docker-up                 # Start services (PostgreSQL, MinIO)

# Testing
make test-unit                 # Run unit tests
make test-integration          # Run integration tests
make test-all                  # Run all tests with coverage

# Code Quality
make lint                      # Run linting
make format                    # Format code
make pre-commit                # Run all pre-commit checks

# Docker
make docker-build              # Build Docker image
make docker-run                # Run container
make docker-logs               # View logs
make docker-stop               # Stop container
```

### GitHub Actions Workflows

| Workflow | Trigger | Purpose |
|----------|---------|---------|
| **Tests** | Push/PR to main/develop | Run all tests, linting, type checking |
| **Docker Build** | Push/PR/Tags | Build and push Docker images |
| **Deploy** | Push to main, Tags | Deploy to staging/production |
| **Code Quality** | Push/PR | Comprehensive code quality checks |

## 📋 Workflow Details

### Tests Workflow
```yaml
Triggers: push, pull_request (main, develop)
Jobs:
  - test (Python 3.8, 3.9, 3.10, 3.11)
    - Lint (Flake8)
    - Type check (MyPy)
    - Security (Bandit)
    - Unit tests
    - Integration tests
  - e2e-tests (main only)
  - performance-tests (main only)
```

### Docker Build Workflow
```yaml
Triggers: push, pull_request, tags (v*)
Jobs:
  - build-and-push
    - Build multi-platform (amd64, arm64)
    - Security scan (Trivy)
    - Push to GHCR
  - test-image
    - Run container
    - Test endpoints
```

### Deploy Workflow
```yaml
Triggers: push (main), tags (v*), manual
Jobs:
  - deploy-frontend (Netlify)
  - deploy-backend (GCP/AWS/K8s)
  - rollback (on failure)
```

### Code Quality Workflow
```yaml
Triggers: push, pull_request
Jobs:
  - lint-python (Ruff, Flake8, Black, MyPy)
  - lint-frontend (ESLint, Prettier, TypeScript)
  - dependency-review
  - codeql-analysis
  - check-docs
  - check-docker
```

## 🔑 Required Secrets

### Essential
- `GITHUB_TOKEN` - Auto-provided by GitHub

### Deployment
- `NETLIFY_AUTH_TOKEN` - Frontend deployment
- `NETLIFY_SITE_ID` - Netlify site ID
- `GCP_SA_KEY` - Google Cloud deployment
- `DATABASE_URL` - Production database

### Optional
- `CODECOV_TOKEN` - Coverage reporting
- `SLACK_WEBHOOK` - Notifications
- `AWS_ACCESS_KEY_ID` - AWS deployment
- `KUBE_CONFIG` - Kubernetes deployment

## 📊 Test Commands

```bash
# Run specific test types
python run_tests.py --unit
python run_tests.py --integration
python run_tests.py --e2e
python run_tests.py --performance

# Run with options
python run_tests.py --all --coverage --html
python run_tests.py --unit -v              # Verbose
python run_tests.py --all -n 4             # Parallel (4 workers)
python run_tests.py --file tests/unit/test_models.py
python run_tests.py --pattern "test_predict*"
```

## 🐳 Docker Commands

```bash
# Local development
docker-compose up -d                       # Start services
docker-compose down                        # Stop services
docker-compose logs -f                     # View logs

# Build and run
docker build -t medical-text-classifier .
docker run -p 8000:8000 \
  -e DATABASE_URL=postgresql://... \
  medical-text-classifier

# Registry operations
docker tag medical-text-classifier:latest ghcr.io/user/repo:latest
docker push ghcr.io/user/repo:latest
```

## 🔄 Git Workflow

```bash
# Feature development
git checkout develop
git pull origin develop
git checkout -b feature/my-feature
# ... make changes ...
git add .
git commit -m "feat: add my feature"
git push origin feature/my-feature
# Create PR to develop

# Release
git checkout main
git pull origin main
git tag -a v1.0.0 -m "Release v1.0.0"
git push origin v1.0.0
# Triggers deployment workflow
```

## 📝 Commit Message Format

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types:**
- `feat` - New feature
- `fix` - Bug fix
- `docs` - Documentation
- `style` - Formatting
- `refactor` - Code refactoring
- `test` - Tests
- `chore` - Maintenance
- `perf` - Performance
- `ci` - CI/CD changes

**Examples:**
```bash
feat(api): add batch prediction endpoint
fix(inference): handle empty text input
docs(readme): update installation instructions
ci(workflow): add security scanning
```

## 🎯 Pre-commit Checklist

Before pushing code:
- [ ] Run `make format` to format code
- [ ] Run `make lint` to check linting
- [ ] Run `make test-unit` to run unit tests
- [ ] Update tests for new features
- [ ] Update documentation if needed
- [ ] Write descriptive commit message

Or simply run:
```bash
make pre-commit
```

## 🚨 Troubleshooting

### Tests fail in CI but pass locally
```bash
# Check Python version
python --version

# Run with same Python version as CI
pyenv install 3.10
pyenv local 3.10

# Check environment variables
env | grep DATABASE_URL
```

### Docker build fails
```bash
# Check Dockerfile syntax
docker build --no-cache -t test .

# Check .dockerignore
cat .dockerignore

# View build logs
docker build -t test . 2>&1 | tee build.log
```

### Deployment fails
```bash
# Check secrets are set
gh secret list

# Check deployment logs
gh run view --log

# Manual deployment test
make deploy-staging
```

## 📈 Monitoring

### Coverage
- View at: `https://codecov.io/gh/{user}/{repo}`
- Local: `open htmlcov/index.html`

### Security
- GitHub Security tab
- Trivy scan results in Actions
- Bandit reports in artifacts

### Deployments
- GitHub Deployments tab
- Netlify dashboard
- Cloud provider console

## 🔗 Useful Links

- [GitHub Actions Docs](https://docs.github.com/en/actions)
- [Docker Docs](https://docs.docker.com/)
- [Pytest Docs](https://docs.pytest.org/)
- [FastAPI Docs](https://fastapi.tiangolo.com/)
- [Conventional Commits](https://www.conventionalcommits.org/)

## 💡 Tips

1. **Use caching** - Workflows cache dependencies for faster builds
2. **Run locally first** - Always test locally before pushing
3. **Check logs** - GitHub Actions logs are detailed
4. **Use artifacts** - Download test reports from Actions
5. **Monitor coverage** - Keep coverage above 80%
6. **Review security** - Check Security tab regularly
7. **Tag releases** - Use semantic versioning (v1.2.3)
8. **Document changes** - Update docs with code changes

## 🎓 Learning Resources

### Beginners
1. Run `make help` to see available commands
2. Read `CONTRIBUTING.md` for guidelines
3. Check `docs/CI_CD.md` for detailed docs
4. Review existing PRs for examples

### Advanced
1. Customize workflows in `.github/workflows/`
2. Add new Makefile targets
3. Extend test suite
4. Optimize Docker builds
5. Add monitoring and alerting

---

**Need help?** Open an issue or check the documentation!

