"""
Pytest configuration and shared fixtures for testing.
"""
import os
import sys
import pytest
import tempfile
import shutil
from unittest.mock import Mock, patch
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# Add src to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.db import Base, MedicalText
from src.api.main import app
from src.api.inference import MedicalTextClassifier


@pytest.fixture(scope="session")
def test_db_engine():
    """Create a test database engine using SQLite in memory."""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    return engine


@pytest.fixture(scope="function")
def test_db_session(test_db_engine):
    """Create a test database session."""
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_db_engine)
    session = TestingSessionLocal()
    
    # Add some test data
    test_records = [
        MedicalText(
            question="What are the symptoms of diabetes?",
            answer="Common symptoms include increased thirst, frequent urination, and fatigue.",
            source="test",
            focusarea="Diabetes",
            focusgroup="Metabolic & Endocrine Disorders"
        ),
        MedicalText(
            question="How is heart disease diagnosed?",
            answer="Heart disease is diagnosed through various tests including ECG and blood tests.",
            source="test",
            focusarea="Heart Disease",
            focusgroup="Cardiovascular Diseases"
        ),
        MedicalText(
            question="What causes Alzheimer's disease?",
            answer="The exact cause is unknown but involves brain protein abnormalities.",
            source="test",
            focusarea="Alzheimer's Disease",
            focusgroup="Neurological & Cognitive Disorders"
        )
    ]
    
    for record in test_records:
        session.add(record)
    session.commit()
    
    yield session
    session.close()


@pytest.fixture
def mock_classifier():
    """Create a mock classifier for testing."""
    classifier = Mock(spec=MedicalTextClassifier)
    classifier.is_loaded.return_value = True
    classifier.predict.return_value = (
        "Metabolic & Endocrine Disorders",
        0.85,
        {
            "Metabolic & Endocrine Disorders": 0.85,
            "Cardiovascular Diseases": 0.10,
            "Neurological & Cognitive Disorders": 0.03,
            "Cancers": 0.01,
            "Other Age-Related & Immune Disorders": 0.01
        }
    )
    return classifier


@pytest.fixture
def client(mock_classifier):
    """Create a test client for the FastAPI app with mocked classifier."""
    with patch('src.api.main.get_classifier', return_value=mock_classifier):
        with patch('src.api.main.SessionLocal') as mock_session:
            # Mock database session
            mock_db = Mock()
            mock_db.execute.return_value = None
            mock_session.return_value = mock_db

            with TestClient(app) as test_client:
                yield test_client


@pytest.fixture
def integration_client():
    """Create a test client for integration tests with real classifier."""
    with patch('src.api.main.SessionLocal') as mock_session:
        # Mock database session
        mock_db = Mock()
        mock_db.execute.return_value = None
        mock_session.return_value = mock_db

        with TestClient(app) as test_client:
            yield test_client


@pytest.fixture
def sample_medical_texts():
    """Sample medical texts for testing."""
    return [
        {
            "text": "What are the symptoms of diabetes?",
            "expected_category": "Metabolic & Endocrine Disorders"
        },
        {
            "text": "I have chest pain and shortness of breath",
            "expected_category": "Cardiovascular Diseases"
        },
        {
            "text": "What are the treatment options for breast cancer?",
            "expected_category": "Cancers"
        },
        {
            "text": "My grandmother has Alzheimer's disease",
            "expected_category": "Neurological & Cognitive Disorders"
        },
        {
            "text": "How to manage arthritis symptoms?",
            "expected_category": "Other Age-Related & Immune Disorders"
        }
    ]


@pytest.fixture
def temp_model_dir():
    """Create a temporary directory for model files."""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir)


@pytest.fixture
def mock_label_encoder():
    """Create a mock label encoder."""
    mock_encoder = Mock()
    mock_encoder.classes_ = [
        "Cancers",
        "Cardiovascular Diseases", 
        "Metabolic & Endocrine Disorders",
        "Neurological & Cognitive Disorders",
        "Other Age-Related & Immune Disorders"
    ]
    mock_encoder.transform.return_value = [0, 1, 2, 3, 4]
    mock_encoder.inverse_transform.return_value = mock_encoder.classes_
    return mock_encoder


# Test configuration
pytest_plugins = []

def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line(
        "markers", "unit: mark test as a unit test"
    )
    config.addinivalue_line(
        "markers", "integration: mark test as an integration test"
    )
    config.addinivalue_line(
        "markers", "e2e: mark test as an end-to-end test"
    )
    config.addinivalue_line(
        "markers", "performance: mark test as a performance test"
    )
    config.addinivalue_line(
        "markers", "api: mark test as an API test"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow running"
    )
    config.addinivalue_line(
        "markers", "model: mark test as model-related"
    )


# Environment setup for tests
os.environ["TESTING"] = "1"
os.environ["LOG_LEVEL"] = "WARNING"
os.environ["ALLOWED_ORIGINS"] = "http://localhost:3000,http://localhost:3001,*"
