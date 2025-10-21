# 🧪 Testing Guide
## Medical Text Classification App

Comprehensive testing strategy and implementation guide for ensuring code quality, reliability, and performance.

## 🎯 Testing Strategy

### Testing Pyramid
```
                    E2E Tests (5%)
                 ┌─────────────────┐
                 │   Integration   │ (15%)
               ┌─────────────────────┐
               │    Unit Tests       │ (80%)
             ┌─────────────────────────┐
```

### Test Types
1. **Unit Tests** - Individual functions and components
2. **Integration Tests** - API endpoints and database operations
3. **End-to-End Tests** - Complete user workflows
4. **Performance Tests** - Load testing and benchmarks
5. **Security Tests** - Vulnerability and penetration testing

## 🔧 Testing Setup

### Backend Testing (Python)

**Dependencies**:
```bash
pip install pytest pytest-asyncio pytest-cov httpx
```

**Configuration** (`pytest.ini`):
```ini
[tool:pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = 
    --cov=src
    --cov-report=html
    --cov-report=term-missing
    --cov-fail-under=80
    -v
asyncio_mode = auto
```

### Frontend Testing (React)

**Dependencies**:
```bash
npm install --save-dev @testing-library/react @testing-library/jest-dom @testing-library/user-event
```

**Configuration** (`src/setupTests.ts`):
```typescript
import '@testing-library/jest-dom';
import { configure } from '@testing-library/react';

configure({ testIdAttribute: 'data-testid' });

// Mock environment variables
process.env.REACT_APP_API_URL = 'http://localhost:8000';
```

## 🧪 Unit Testing

### Backend Unit Tests

#### Testing API Endpoints
```python
import pytest
from fastapi.testclient import TestClient
from src.api.main import app

client = TestClient(app)

class TestPredictionEndpoint:
    def test_predict_valid_text(self):
        """Test prediction with valid medical text."""
        response = client.post(
            "/predict",
            json={"text": "What are the symptoms of diabetes?"}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert "predicted_class" in data
        assert "confidence" in data
        assert "focus_group" in data
        assert "probabilities" in data
        assert len(data["probabilities"]) == 5
        assert 0 <= data["confidence"] <= 1
        assert 0 <= data["predicted_class"] <= 4

    def test_predict_empty_text(self):
        """Test prediction with empty text."""
        response = client.post(
            "/predict",
            json={"text": ""}
        )
        
        assert response.status_code == 422
        assert "validation error" in response.json()["detail"][0]["msg"].lower()

    def test_predict_text_too_long(self):
        """Test prediction with text exceeding maximum length."""
        long_text = "a" * 5001
        response = client.post(
            "/predict",
            json={"text": long_text}
        )
        
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_predict_with_api_key(self):
        """Test prediction with API key authentication."""
        headers = {"X-API-Key": "test-api-key"}
        response = client.post(
            "/predict",
            json={"text": "Test medical text"},
            headers=headers
        )
        
        assert response.status_code == 200
```

#### Testing ML Model
```python
import pytest
import torch
from src.ml.model import MedicalTextClassifier

class TestMedicalTextClassifier:
    @pytest.fixture
    def classifier(self):
        """Create classifier instance for testing."""
        return MedicalTextClassifier()

    def test_model_loading(self, classifier):
        """Test that model loads successfully."""
        assert classifier.model is not None
        assert classifier.tokenizer is not None
        assert classifier.label_mapping is not None

    def test_prediction_format(self, classifier):
        """Test prediction output format."""
        text = "What are the symptoms of diabetes?"
        result = classifier.predict(text)
        
        assert isinstance(result, dict)
        assert "predicted_class" in result
        assert "confidence" in result
        assert "probabilities" in result
        assert len(result["probabilities"]) == 5

    def test_prediction_confidence_range(self, classifier):
        """Test that confidence scores are in valid range."""
        text = "Heart disease symptoms and treatment"
        result = classifier.predict(text)
        
        assert 0 <= result["confidence"] <= 1
        for prob in result["probabilities"]:
            assert 0 <= prob <= 1
        
        # Probabilities should sum to approximately 1
        assert abs(sum(result["probabilities"]) - 1.0) < 0.001

    @pytest.mark.parametrize("text,expected_class", [
        ("diabetes symptoms", 3),  # Metabolic & Endocrine
        ("heart attack signs", 2),  # Cardiovascular
        ("brain tumor", 1),         # Cancers
        ("alzheimer disease", 0),   # Neurological
        ("arthritis pain", 4),      # Other Age-Related
    ])
    def test_classification_accuracy(self, classifier, text, expected_class):
        """Test classification accuracy for known examples."""
        result = classifier.predict(text)
        assert result["predicted_class"] == expected_class
```

#### Testing Database Operations
```python
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.db import Base, MedicalText

# Test database setup
TEST_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture
def db_session():
    """Create test database session."""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)

class TestDatabaseOperations:
    def test_create_medical_text(self, db_session):
        """Test creating medical text record."""
        medical_text = MedicalText(
            question="What is diabetes?",
            answer="Diabetes is a metabolic disorder...",
            source="test",
            focusarea="endocrinology",
            focusgroup="Metabolic & Endocrine Disorders"
        )
        
        db_session.add(medical_text)
        db_session.commit()
        
        assert medical_text.id is not None
        assert medical_text.created_at is not None

    def test_query_medical_text(self, db_session):
        """Test querying medical text records."""
        # Create test data
        medical_text = MedicalText(
            question="Test question",
            answer="Test answer",
            source="test"
        )
        db_session.add(medical_text)
        db_session.commit()
        
        # Query data
        result = db_session.query(MedicalText).filter(
            MedicalText.question == "Test question"
        ).first()
        
        assert result is not None
        assert result.question == "Test question"
        assert result.answer == "Test answer"
```

### Frontend Unit Tests

#### Testing React Components
```typescript
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { ClassificationForm } from '../components/ClassificationForm';
import { apiService } from '../services/api';

// Mock API service
jest.mock('../services/api');
const mockApiService = apiService as jest.Mocked<typeof apiService>;

describe('ClassificationForm', () => {
  const mockOnResult = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
  });

  test('renders form elements', () => {
    render(<ClassificationForm onResult={mockOnResult} />);
    
    expect(screen.getByText('Enter Medical Text for Classification')).toBeInTheDocument();
    expect(screen.getByPlaceholderText(/Enter your medical question/)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /Classify Text/ })).toBeInTheDocument();
  });

  test('updates character count', async () => {
    const user = userEvent.setup();
    render(<ClassificationForm onResult={mockOnResult} />);
    
    const textInput = screen.getByPlaceholderText(/Enter your medical question/);
    await user.type(textInput, 'Test text');
    
    expect(screen.getByText('9/5000 characters')).toBeInTheDocument();
  });

  test('disables submit button when text is empty', () => {
    render(<ClassificationForm onResult={mockOnResult} />);
    
    const submitButton = screen.getByRole('button', { name: /Classify Text/ });
    expect(submitButton).toBeDisabled();
  });

  test('enables submit button when text is entered', async () => {
    const user = userEvent.setup();
    render(<ClassificationForm onResult={mockOnResult} />);
    
    const textInput = screen.getByPlaceholderText(/Enter your medical question/);
    const submitButton = screen.getByRole('button', { name: /Classify Text/ });
    
    await user.type(textInput, 'Test medical text');
    expect(submitButton).toBeEnabled();
  });

  test('submits form and calls onResult', async () => {
    const user = userEvent.setup();
    const mockResult = {
      predicted_class: 3,
      confidence: 0.95,
      focus_group: 'Metabolic & Endocrine Disorders',
      probabilities: [0.01, 0.02, 0.01, 0.95, 0.01],
      processing_time_ms: 87.3,
      model_version: 'biomedbert-v1.0',
      timestamp: '2024-01-15T10:30:00Z'
    };

    mockApiService.classifyText.mockResolvedValue(mockResult);

    render(<ClassificationForm onResult={mockOnResult} />);
    
    const textInput = screen.getByPlaceholderText(/Enter your medical question/);
    const submitButton = screen.getByRole('button', { name: /Classify Text/ });

    await user.type(textInput, 'What are the symptoms of diabetes?');
    await user.click(submitButton);

    await waitFor(() => {
      expect(mockApiService.classifyText).toHaveBeenCalledWith('What are the symptoms of diabetes?');
      expect(mockOnResult).toHaveBeenCalledWith(mockResult);
    });
  });

  test('displays error message on API failure', async () => {
    const user = userEvent.setup();
    mockApiService.classifyText.mockRejectedValue(new Error('API Error'));

    render(<ClassificationForm onResult={mockOnResult} />);
    
    const textInput = screen.getByPlaceholderText(/Enter your medical question/);
    const submitButton = screen.getByRole('button', { name: /Classify Text/ });

    await user.type(textInput, 'Test text');
    await user.click(submitButton);

    await waitFor(() => {
      expect(screen.getByText('API Error')).toBeInTheDocument();
    });
  });
});
```

#### Testing Custom Hooks
```typescript
import { renderHook, waitFor } from '@testing-library/react';
import { useClassification } from '../hooks/useClassification';
import { apiService } from '../services/api';

jest.mock('../services/api');
const mockApiService = apiService as jest.Mocked<typeof apiService>;

describe('useClassification', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  test('initial state', () => {
    const { result } = renderHook(() => useClassification());
    
    expect(result.current.loading).toBe(false);
    expect(result.current.error).toBe(null);
    expect(result.current.result).toBe(null);
  });

  test('successful classification', async () => {
    const mockResult = {
      predicted_class: 3,
      confidence: 0.95,
      focus_group: 'Metabolic & Endocrine Disorders',
      probabilities: [0.01, 0.02, 0.01, 0.95, 0.01],
      processing_time_ms: 87.3,
      model_version: 'biomedbert-v1.0',
      timestamp: '2024-01-15T10:30:00Z'
    };

    mockApiService.classifyText.mockResolvedValue(mockResult);

    const { result } = renderHook(() => useClassification());
    
    const classifyPromise = result.current.classify('Test text');
    
    expect(result.current.loading).toBe(true);
    
    await waitFor(() => {
      expect(result.current.loading).toBe(false);
      expect(result.current.result).toEqual(mockResult);
      expect(result.current.error).toBe(null);
    });

    const returnedResult = await classifyPromise;
    expect(returnedResult).toEqual(mockResult);
  });

  test('classification error', async () => {
    mockApiService.classifyText.mockRejectedValue(new Error('API Error'));

    const { result } = renderHook(() => useClassification());
    
    const classifyPromise = result.current.classify('Test text');
    
    await waitFor(() => {
      expect(result.current.loading).toBe(false);
      expect(result.current.error).toBe('API Error');
      expect(result.current.result).toBe(null);
    });

    const returnedResult = await classifyPromise;
    expect(returnedResult).toBe(null);
  });
});
```

## 🔗 Integration Testing

### API Integration Tests
```python
import pytest
import asyncio
from httpx import AsyncClient
from src.api.main import app

@pytest.mark.asyncio
class TestAPIIntegration:
    async def test_health_check_integration(self):
        """Test health check endpoint integration."""
        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.get("/health")
            
            assert response.status_code == 200
            data = response.json()
            
            assert data["status"] in ["healthy", "degraded", "unhealthy"]
            assert "components" in data
            assert "database" in data["components"]
            assert "model" in data["components"]

    async def test_prediction_integration(self):
        """Test prediction endpoint integration."""
        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.post(
                "/predict",
                json={"text": "What are the symptoms of diabetes?"}
            )
            
            assert response.status_code == 200
            data = response.json()
            
            # Verify response structure
            required_fields = [
                "predicted_class", "confidence", "focus_group", 
                "probabilities", "processing_time_ms", "model_version"
            ]
            for field in required_fields:
                assert field in data
            
            # Verify data types and ranges
            assert isinstance(data["predicted_class"], int)
            assert 0 <= data["predicted_class"] <= 4
            assert isinstance(data["confidence"], float)
            assert 0 <= data["confidence"] <= 1
            assert isinstance(data["probabilities"], list)
            assert len(data["probabilities"]) == 5

    async def test_rate_limiting_integration(self):
        """Test rate limiting integration."""
        async with AsyncClient(app=app, base_url="http://test") as ac:
            # Make multiple requests quickly
            tasks = []
            for _ in range(10):
                task = ac.post("/predict", json={"text": "test"})
                tasks.append(task)
            
            responses = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Check that some requests succeed
            success_count = sum(1 for r in responses if hasattr(r, 'status_code') and r.status_code == 200)
            assert success_count > 0
```

### Database Integration Tests
```python
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.db import Base, MedicalText, init_db

class TestDatabaseIntegration:
    @pytest.fixture(scope="class")
    def db_engine(self):
        """Create test database engine."""
        engine = create_engine("sqlite:///./test_integration.db")
        Base.metadata.create_all(bind=engine)
        yield engine
        Base.metadata.drop_all(bind=engine)

    @pytest.fixture
    def db_session(self, db_engine):
        """Create database session for each test."""
        SessionLocal = sessionmaker(bind=db_engine)
        session = SessionLocal()
        try:
            yield session
        finally:
            session.close()

    def test_database_initialization(self, db_engine):
        """Test database initialization."""
        # Check that tables exist
        inspector = inspect(db_engine)
        tables = inspector.get_table_names()
        
        assert "medical_texts" in tables

    def test_medical_text_crud_operations(self, db_session):
        """Test CRUD operations on medical_texts table."""
        # Create
        medical_text = MedicalText(
            question="Integration test question",
            answer="Integration test answer",
            source="integration_test",
            focusarea="test_area",
            focusgroup="Test Group"
        )
        
        db_session.add(medical_text)
        db_session.commit()
        
        # Read
        retrieved = db_session.query(MedicalText).filter(
            MedicalText.question == "Integration test question"
        ).first()
        
        assert retrieved is not None
        assert retrieved.answer == "Integration test answer"
        
        # Update
        retrieved.answer = "Updated answer"
        db_session.commit()
        
        updated = db_session.query(MedicalText).filter(
            MedicalText.id == retrieved.id
        ).first()
        
        assert updated.answer == "Updated answer"
        
        # Delete
        db_session.delete(updated)
        db_session.commit()
        
        deleted = db_session.query(MedicalText).filter(
            MedicalText.id == retrieved.id
        ).first()
        
        assert deleted is None
```

## 🎭 End-to-End Testing

### Playwright E2E Tests
```typescript
import { test, expect } from '@playwright/test';

test.describe('Medical Text Classification App', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('http://localhost:3000');
  });

  test('should display the main interface', async ({ page }) => {
    await expect(page.locator('h1')).toContainText('Medical Text Classification');
    await expect(page.locator('textarea')).toBeVisible();
    await expect(page.locator('button', { hasText: 'Classify Text' })).toBeVisible();
  });

  test('should classify medical text successfully', async ({ page }) => {
    // Enter text
    await page.fill('textarea', 'What are the symptoms of diabetes?');
    
    // Submit form
    await page.click('button:has-text("Classify Text")');
    
    // Wait for results
    await expect(page.locator('[data-testid="classification-result"]')).toBeVisible();
    
    // Verify result content
    await expect(page.locator('[data-testid="focus-group"]')).toContainText('Metabolic & Endocrine Disorders');
    await expect(page.locator('[data-testid="confidence"]')).toBeVisible();
    await expect(page.locator('[data-testid="probabilities"]')).toBeVisible();
  });

  test('should show validation error for empty text', async ({ page }) => {
    // Try to submit empty form
    await page.click('button:has-text("Classify Text")');
    
    // Button should be disabled
    await expect(page.locator('button:has-text("Classify Text")')).toBeDisabled();
  });

  test('should display health status', async ({ page }) => {
    await page.click('[data-testid="health-status-toggle"]');
    
    await expect(page.locator('[data-testid="health-status"]')).toBeVisible();
    await expect(page.locator('[data-testid="system-status"]')).toContainText(/healthy|degraded|unhealthy/);
  });

  test('should handle API errors gracefully', async ({ page }) => {
    // Mock API to return error
    await page.route('**/predict', route => {
      route.fulfill({
        status: 500,
        contentType: 'application/json',
        body: JSON.stringify({ detail: 'Internal server error' })
      });
    });

    await page.fill('textarea', 'Test text');
    await page.click('button:has-text("Classify Text")');

    await expect(page.locator('[data-testid="error-message"]')).toBeVisible();
    await expect(page.locator('[data-testid="error-message"]')).toContainText('error');
  });
});
```

## ⚡ Performance Testing

### Load Testing with Locust
```python
from locust import HttpUser, task, between

class MedicalTextUser(HttpUser):
    wait_time = between(1, 3)
    
    def on_start(self):
        """Setup for each user."""
        self.headers = {
            "Content-Type": "application/json",
            "X-API-Key": "test-api-key"
        }
    
    @task(3)
    def classify_text(self):
        """Test text classification endpoint."""
        texts = [
            "What are the symptoms of diabetes?",
            "How to treat heart disease?",
            "Signs of Alzheimer's disease",
            "Cancer treatment options",
            "Arthritis pain management"
        ]
        
        import random
        text = random.choice(texts)
        
        with self.client.post(
            "/predict",
            json={"text": text},
            headers=self.headers,
            catch_response=True
        ) as response:
            if response.status_code == 200:
                data = response.json()
                if "predicted_class" in data and "confidence" in data:
                    response.success()
                else:
                    response.failure("Invalid response format")
            else:
                response.failure(f"HTTP {response.status_code}")
    
    @task(1)
    def health_check(self):
        """Test health check endpoint."""
        with self.client.get("/health", catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Health check failed: {response.status_code}")
```

## 🛡️ Security Testing

### Security Test Suite
```python
import pytest
from fastapi.testclient import TestClient
from src.api.main import app

client = TestClient(app)

class TestSecurityFeatures:
    def test_xss_protection(self):
        """Test XSS attack prevention."""
        malicious_text = "<script>alert('xss')</script>"
        response = client.post(
            "/predict",
            json={"text": malicious_text}
        )
        
        # Should either reject or sanitize
        assert response.status_code in [400, 422, 200]
        if response.status_code == 200:
            # Ensure script tags are not in response
            assert "<script>" not in response.text

    def test_sql_injection_protection(self):
        """Test SQL injection prevention."""
        malicious_text = "'; DROP TABLE medical_texts; --"
        response = client.post(
            "/predict",
            json={"text": malicious_text}
        )
        
        # Should handle gracefully
        assert response.status_code in [400, 422, 200]

    def test_rate_limiting(self):
        """Test rate limiting functionality."""
        # Make many requests quickly
        responses = []
        for _ in range(150):  # Exceed rate limit
            response = client.post(
                "/predict",
                json={"text": "test"}
            )
            responses.append(response.status_code)
        
        # Should see some 429 responses
        assert 429 in responses

    def test_api_key_authentication(self):
        """Test API key authentication."""
        # Test without API key (should work in dev)
        response = client.post(
            "/predict",
            json={"text": "test"}
        )
        assert response.status_code in [200, 401]
        
        # Test with invalid API key
        response = client.post(
            "/predict",
            json={"text": "test"},
            headers={"X-API-Key": "invalid-key"}
        )
        assert response.status_code in [200, 401]

    def test_security_headers(self):
        """Test security headers presence."""
        response = client.get("/health")
        
        # Check for security headers
        headers = response.headers
        assert "x-frame-options" in headers
        assert "x-content-type-options" in headers
        assert "x-xss-protection" in headers
```

## 📊 Test Coverage and Reporting

### Coverage Configuration
```bash
# Backend coverage
pytest --cov=src --cov-report=html --cov-report=term-missing

# Frontend coverage
npm test -- --coverage --watchAll=false
```

### Coverage Targets
- **Overall Coverage**: 80%+
- **Critical Paths**: 95%+
- **API Endpoints**: 90%+
- **ML Model**: 85%+
- **Frontend Components**: 80%+

### Test Reporting
```bash
# Generate test reports
pytest --html=reports/pytest_report.html --self-contained-html
npm test -- --coverage --coverageReporters=html --coverageReporters=text
```

## 🚀 Running Tests

### Development Testing
```bash
# Backend tests
pytest tests/ -v

# Frontend tests
cd frontend && npm test

# Integration tests
pytest tests/integration/ -v

# E2E tests
npx playwright test
```

### CI/CD Testing
```bash
# Full test suite
make test

# With coverage
make test-coverage

# Performance tests
make test-performance

# Security tests
make test-security
```

---

## 🎯 Testing Best Practices

### 1. **Test Organization**
- Group related tests in classes
- Use descriptive test names
- Follow AAA pattern (Arrange, Act, Assert)
- Keep tests independent and isolated

### 2. **Test Data Management**
- Use fixtures for test data setup
- Clean up after tests
- Use factories for complex objects
- Avoid hardcoded values

### 3. **Mocking and Stubbing**
- Mock external dependencies
- Use dependency injection
- Test both success and failure paths
- Verify mock interactions

### 4. **Performance Testing**
- Test under realistic load
- Monitor resource usage
- Set performance benchmarks
- Test scalability limits

### 5. **Security Testing**
- Test input validation
- Verify authentication/authorization
- Check for common vulnerabilities
- Regular security audits

This comprehensive testing strategy ensures the Medical Text Classification application is reliable, secure, and performant across all components and use cases.
