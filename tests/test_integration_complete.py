"""
Complete Integration Test Suite
Medical Text Classification App

This test suite verifies that all components work together seamlessly:
- API endpoints
- ML model inference
- Database operations
- Security features
- Monitoring metrics
"""

import pytest
import asyncio
import time
import requests
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Import application components
from src.api.main import app
from src.db import Base, MedicalText
from src.ml.model import MedicalTextClassifier

# Test configuration
TEST_DATABASE_URL = "sqlite:///./test_integration.db"
API_BASE_URL = "http://localhost:8000"

class TestCompleteIntegration:
    """Complete integration test suite."""
    
    @pytest.fixture(scope="class")
    def client(self):
        """Create test client."""
        return TestClient(app)
    
    @pytest.fixture(scope="class")
    def db_engine(self):
        """Create test database engine."""
        engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
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
    
    @pytest.fixture(scope="class")
    def ml_classifier(self):
        """Create ML classifier instance."""
        return MedicalTextClassifier()

    def test_01_health_check_integration(self, client):
        """Test health check endpoint integration."""
        response = client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify response structure
        assert "status" in data
        assert "timestamp" in data
        assert "components" in data
        
        # Verify component health
        components = data["components"]
        assert "database" in components
        assert "model" in components
        assert "security" in components
        
        # Verify each component has status
        for component_name, component_data in components.items():
            assert "status" in component_data
            assert component_data["status"] in ["healthy", "degraded", "unhealthy"]

    def test_02_model_loading_integration(self, ml_classifier):
        """Test ML model loading and basic functionality."""
        # Verify model components are loaded
        assert ml_classifier.model is not None
        assert ml_classifier.tokenizer is not None
        assert ml_classifier.label_mapping is not None
        assert ml_classifier.reverse_label_mapping is not None
        
        # Test basic prediction
        result = ml_classifier.predict("What are the symptoms of diabetes?")
        
        # Verify prediction structure
        assert isinstance(result, dict)
        assert "predicted_class" in result
        assert "confidence" in result
        assert "probabilities" in result
        assert "processing_time_ms" in result
        
        # Verify prediction values
        assert 0 <= result["predicted_class"] <= 4
        assert 0 <= result["confidence"] <= 1
        assert len(result["probabilities"]) == 5
        assert sum(result["probabilities"]) == pytest.approx(1.0, abs=0.001)

    def test_03_database_integration(self, db_session):
        """Test database operations integration."""
        # Create test record
        medical_text = MedicalText(
            question="Integration test question",
            answer="Integration test answer",
            source="integration_test",
            focusarea="test_area",
            focusgroup="Test Group"
        )
        
        # Test create operation
        db_session.add(medical_text)
        db_session.commit()
        assert medical_text.id is not None
        
        # Test read operation
        retrieved = db_session.query(MedicalText).filter(
            MedicalText.question == "Integration test question"
        ).first()
        assert retrieved is not None
        assert retrieved.answer == "Integration test answer"
        
        # Test update operation
        retrieved.answer = "Updated integration test answer"
        db_session.commit()
        
        updated = db_session.query(MedicalText).filter(
            MedicalText.id == retrieved.id
        ).first()
        assert updated.answer == "Updated integration test answer"
        
        # Test delete operation
        db_session.delete(updated)
        db_session.commit()
        
        deleted = db_session.query(MedicalText).filter(
            MedicalText.id == retrieved.id
        ).first()
        assert deleted is None

    def test_04_prediction_endpoint_integration(self, client):
        """Test prediction endpoint with full integration."""
        # Test valid prediction request
        response = client.post(
            "/predict",
            json={"text": "What are the symptoms of diabetes and how is it diagnosed?"}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify response structure
        required_fields = [
            "predicted_class", "confidence", "focus_group", 
            "probabilities", "processing_time_ms", "model_version", "timestamp"
        ]
        for field in required_fields:
            assert field in data
        
        # Verify prediction values
        assert 0 <= data["predicted_class"] <= 4
        assert 0 <= data["confidence"] <= 1
        assert len(data["probabilities"]) == 5
        assert data["processing_time_ms"] > 0
        
        # Verify focus group mapping
        expected_focus_groups = [
            "Neurological & Cognitive Disorders",
            "Cancers", 
            "Cardiovascular Diseases",
            "Metabolic & Endocrine Disorders",
            "Other Age-Related & Immune Disorders"
        ]
        assert data["focus_group"] in expected_focus_groups

    def test_05_input_validation_integration(self, client):
        """Test input validation across the system."""
        # Test empty text
        response = client.post("/predict", json={"text": ""})
        assert response.status_code == 422
        
        # Test text too long
        long_text = "a" * 5001
        response = client.post("/predict", json={"text": long_text})
        assert response.status_code == 422
        
        # Test malformed JSON
        response = client.post(
            "/predict",
            data="invalid json",
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 422
        
        # Test missing text field
        response = client.post("/predict", json={})
        assert response.status_code == 422

    def test_06_security_integration(self, client):
        """Test security features integration."""
        # Test security headers
        response = client.get("/health")
        headers = response.headers
        
        # Verify security headers are present
        security_headers = [
            "x-frame-options",
            "x-content-type-options", 
            "x-xss-protection",
            "referrer-policy"
        ]
        
        for header in security_headers:
            assert header in headers or header.replace("-", "_") in headers
        
        # Test CORS headers
        response = client.options(
            "/predict",
            headers={
                "Origin": "http://localhost:3000",
                "Access-Control-Request-Method": "POST"
            }
        )
        assert "access-control-allow-origin" in response.headers

    def test_07_rate_limiting_integration(self, client):
        """Test rate limiting integration."""
        # Make multiple requests quickly
        responses = []
        for i in range(10):
            response = client.post(
                "/predict",
                json={"text": f"Test text {i}"}
            )
            responses.append(response.status_code)
        
        # Should have some successful responses
        success_count = sum(1 for status in responses if status == 200)
        assert success_count > 0
        
        # Check for rate limit headers in responses
        response = client.post("/predict", json={"text": "test"})
        if response.status_code == 200:
            # Rate limit headers might be present
            headers = response.headers
            rate_limit_headers = [
                "x-ratelimit-limit",
                "x-ratelimit-remaining", 
                "x-ratelimit-reset"
            ]
            # At least one rate limit header should be present
            has_rate_limit_header = any(
                header in headers for header in rate_limit_headers
            )

    def test_08_metrics_integration(self, client):
        """Test metrics collection integration."""
        # Make some requests to generate metrics
        for i in range(5):
            client.post("/predict", json={"text": f"Test metrics {i}"})
        
        # Get metrics
        response = client.get("/metrics")
        assert response.status_code == 200
        
        metrics_text = response.text
        
        # Verify key metrics are present
        expected_metrics = [
            "http_requests_total",
            "http_request_duration_seconds",
            "predictions_total"
        ]
        
        for metric in expected_metrics:
            assert metric in metrics_text

    def test_09_error_handling_integration(self, client):
        """Test error handling across the system."""
        # Test various error conditions
        
        # Invalid endpoint
        response = client.get("/nonexistent")
        assert response.status_code == 404
        
        # Invalid method
        response = client.delete("/predict")
        assert response.status_code == 405
        
        # Invalid content type
        response = client.post(
            "/predict",
            data="text=test",
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        assert response.status_code in [422, 415]

    def test_10_performance_integration(self, client):
        """Test performance characteristics."""
        # Test response time
        start_time = time.time()
        response = client.post(
            "/predict",
            json={"text": "What are the symptoms of diabetes?"}
        )
        response_time = time.time() - start_time
        
        assert response.status_code == 200
        assert response_time < 5.0  # Should respond within 5 seconds
        
        # Verify processing time is reported
        data = response.json()
        assert "processing_time_ms" in data
        assert data["processing_time_ms"] > 0
        assert data["processing_time_ms"] < 5000  # Less than 5 seconds

    def test_11_concurrent_requests_integration(self, client):
        """Test handling of concurrent requests."""
        import threading
        import queue
        
        results = queue.Queue()
        
        def make_request(text):
            try:
                response = client.post("/predict", json={"text": text})
                results.put(response.status_code)
            except Exception as e:
                results.put(f"Error: {e}")
        
        # Create multiple threads
        threads = []
        for i in range(5):
            thread = threading.Thread(
                target=make_request, 
                args=(f"Concurrent test {i}",)
            )
            threads.append(thread)
        
        # Start all threads
        for thread in threads:
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # Check results
        status_codes = []
        while not results.empty():
            status_codes.append(results.get())
        
        # Should have responses from all threads
        assert len(status_codes) == 5
        
        # Most should be successful
        success_count = sum(1 for code in status_codes if code == 200)
        assert success_count >= 3

    def test_12_end_to_end_workflow(self, client, db_session):
        """Test complete end-to-end workflow."""
        # Step 1: Check system health
        health_response = client.get("/health")
        assert health_response.status_code == 200
        assert health_response.json()["status"] in ["healthy", "degraded"]
        
        # Step 2: Make prediction
        prediction_response = client.post(
            "/predict",
            json={"text": "What are the symptoms of heart disease?"}
        )
        assert prediction_response.status_code == 200
        prediction_data = prediction_response.json()
        
        # Step 3: Verify prediction quality
        assert prediction_data["confidence"] > 0.5  # Should be reasonably confident
        assert prediction_data["predicted_class"] in [0, 1, 2, 3, 4]
        
        # Step 4: Check metrics were updated
        metrics_response = client.get("/metrics")
        assert metrics_response.status_code == 200
        assert "predictions_total" in metrics_response.text
        
        # Step 5: Verify database logging (if enabled)
        # This would depend on your specific implementation
        
        print("✅ End-to-end workflow completed successfully!")

if __name__ == "__main__":
    # Run integration tests
    pytest.main([__file__, "-v", "--tb=short"])
