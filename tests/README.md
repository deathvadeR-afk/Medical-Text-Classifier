# Testing Documentation

This directory contains comprehensive tests for the Medical Text Classification project.

## Test Structure

```
tests/
├── __init__.py                 # Test package initialization
├── conftest.py                 # Shared fixtures and configuration
├── README.md                   # This documentation
├── unit/                       # Unit tests
│   ├── __init__.py
│   ├── test_models.py          # Pydantic model tests
│   ├── test_inference.py       # Inference logic tests
│   └── test_database.py        # Database model tests
├── integration/                # Integration tests
│   ├── __init__.py
│   └── test_api.py             # API endpoint tests
├── e2e/                        # End-to-end tests
│   ├── __init__.py
│   └── test_full_pipeline.py   # Complete workflow tests
└── performance/                # Performance tests
    ├── __init__.py
    └── test_load.py             # Load and performance tests
```

## Test Categories

### 1. Unit Tests (`tests/unit/`)
- **Purpose**: Test individual components in isolation
- **Scope**: Functions, classes, and modules
- **Speed**: Fast (< 1 second per test)
- **Dependencies**: Minimal, uses mocks extensively

**Files:**
- `test_models.py`: Tests for Pydantic request/response models
- `test_inference.py`: Tests for classification logic and rule-based inference
- `test_database.py`: Tests for SQLAlchemy models and database operations

### 2. Integration Tests (`tests/integration/`)
- **Purpose**: Test component interactions
- **Scope**: API endpoints, database integration, service interactions
- **Speed**: Medium (1-10 seconds per test)
- **Dependencies**: Test database, mocked external services

**Files:**
- `test_api.py`: Tests for FastAPI endpoints, request/response handling, error cases

### 3. End-to-End Tests (`tests/e2e/`)
- **Purpose**: Test complete user workflows
- **Scope**: Full application stack from frontend to database
- **Speed**: Slow (10+ seconds per test)
- **Dependencies**: Running API server, frontend server, database

**Files:**
- `test_full_pipeline.py`: Tests complete prediction workflows, frontend-API integration

### 4. Performance Tests (`tests/performance/`)
- **Purpose**: Test performance characteristics and scalability
- **Scope**: Response times, throughput, resource usage
- **Speed**: Slow (30+ seconds per test)
- **Dependencies**: Running services, performance monitoring tools

**Files:**
- `test_load.py`: Load testing, concurrent request handling, performance benchmarks

## Running Tests

### Quick Start

```bash
# Install test dependencies
pip install -r requirements-test.txt

# Run fast tests (unit + integration)
python run_tests.py

# Run all tests
python run_tests.py --all
```

### Test Categories

```bash
# Unit tests only
python run_tests.py --unit

# Integration tests only
python run_tests.py --integration

# End-to-end tests only (requires running servers)
python run_tests.py --e2e

# Performance tests only
python run_tests.py --performance
```

### Coverage Reports

```bash
# Run with coverage
python run_tests.py --coverage

# Generate HTML coverage report
python run_tests.py --coverage --html
# View at: htmlcov/index.html
```

### Specific Tests

```bash
# Run specific test file
python run_tests.py --file tests/unit/test_models.py

# Run tests matching pattern
python run_tests.py --pattern "test_prediction"

# Run last failed tests
python run_tests.py --lf
```

### Parallel Execution

```bash
# Run tests in parallel (requires pytest-xdist)
python run_tests.py --parallel 4
```

## Test Configuration

### Pytest Configuration (`pytest.ini`)
- Test discovery settings
- Coverage configuration
- Marker definitions
- Logging configuration

### Fixtures (`conftest.py`)
- **`client`**: FastAPI test client with mocked dependencies
- **`db_session`**: Test database session with sample data
- **`sample_medical_texts`**: Sample texts for testing predictions
- **`mock_classifier`**: Mocked classifier for unit tests

### Environment Variables
- `TESTING=1`: Enables test mode
- `LOG_LEVEL=WARNING`: Reduces log noise during testing
- `DATABASE_URL`: Test database connection string

## Test Data

### Sample Medical Texts
The tests use predefined medical texts covering all focus groups:
- Diabetes (Metabolic & Endocrine Disorders)
- Chest pain (Cardiovascular Diseases)
- Breast cancer (Cancers)
- Alzheimer's (Neurological & Cognitive Disorders)
- Arthritis (Other Age-Related & Immune Disorders)

### Database Test Data
Test database is populated with sample medical records for integration testing.

## Continuous Integration

### GitHub Actions (`.github/workflows/test.yml`)
- **Matrix Testing**: Python 3.8, 3.9, 3.10, 3.11
- **Services**: PostgreSQL database
- **Stages**:
  1. Linting and type checking
  2. Unit and integration tests
  3. End-to-end tests (main branch only)
  4. Performance tests (main branch only)
- **Artifacts**: Coverage reports, test results

### Quality Gates
- **Coverage**: Minimum 80% code coverage
- **Linting**: Flake8 compliance
- **Type Checking**: MyPy validation
- **Security**: Bandit security scanning

## Best Practices

### Writing Tests
1. **Arrange-Act-Assert**: Structure tests clearly
2. **Descriptive Names**: Use descriptive test function names
3. **Single Responsibility**: One assertion per test when possible
4. **Isolation**: Tests should not depend on each other
5. **Mocking**: Mock external dependencies in unit tests

### Test Markers
Use pytest markers to categorize tests:
```python
@pytest.mark.unit
def test_model_validation():
    pass

@pytest.mark.integration
def test_api_endpoint():
    pass

@pytest.mark.slow
def test_performance():
    pass
```

### Performance Testing
- Establish baseline performance metrics
- Test under realistic load conditions
- Monitor resource usage (CPU, memory)
- Set reasonable performance thresholds

## Troubleshooting

### Common Issues

1. **Import Errors**: Ensure `src` is in Python path
2. **Database Errors**: Check PostgreSQL service is running
3. **Port Conflicts**: Ensure ports 8000 and 3001 are available for e2e tests
4. **Slow Tests**: Use `--durations=10` to identify slow tests

### Debug Mode
```bash
# Run with verbose output
python run_tests.py --verbose

# Stop on first failure
python run_tests.py --failfast

# Run specific test with debugging
pytest tests/unit/test_models.py::TestPredictionRequest::test_valid_request -v -s
```

## Contributing

When adding new features:
1. Write unit tests for new functions/classes
2. Add integration tests for new API endpoints
3. Update e2e tests for new user workflows
4. Consider performance implications for new features
5. Maintain test coverage above 80%
