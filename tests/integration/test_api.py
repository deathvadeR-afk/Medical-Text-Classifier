"""
Integration tests for FastAPI application.
"""
import pytest
import json
from fastapi.testclient import TestClient


class TestHealthEndpoint:
    """Test cases for health check endpoint."""
    
    @pytest.mark.integration
    def test_health_check_success(self, client):
        """Test successful health check."""
        response = client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "status" in data
        assert "model_loaded" in data
        assert "database_connected" in data
        assert data["status"] == "healthy"
        assert isinstance(data["model_loaded"], bool)
        assert isinstance(data["database_connected"], bool)
    
    @pytest.mark.integration
    def test_health_check_response_schema(self, client):
        """Test that health check response matches expected schema."""
        response = client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify all required fields are present
        required_fields = ["status", "model_loaded", "database_connected"]
        for field in required_fields:
            assert field in data
        
        # Verify field types
        assert isinstance(data["status"], str)
        assert isinstance(data["model_loaded"], bool)
        assert isinstance(data["database_connected"], bool)


class TestPredictionEndpoint:
    """Test cases for prediction endpoint."""
    
    @pytest.mark.integration
    def test_predict_success(self, integration_client, sample_medical_texts):
        """Test successful prediction."""
        test_case = sample_medical_texts[0]  # Diabetes text

        response = integration_client.post(
            "/predict",
            json={"text": test_case["text"]}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert "predicted_class" in data
        assert "confidence" in data
        assert "probabilities" in data
        
        assert isinstance(data["predicted_class"], str)
        assert isinstance(data["confidence"], float)
        assert isinstance(data["probabilities"], dict)
        
        # Verify confidence is in valid range
        assert 0.0 <= data["confidence"] <= 1.0
        
        # Verify probabilities sum to approximately 1
        total_prob = sum(data["probabilities"].values())
        assert abs(total_prob - 1.0) < 0.01
    
    @pytest.mark.integration
    def test_predict_all_sample_texts(self, integration_client, sample_medical_texts):
        """Test prediction for all sample medical texts."""
        for test_case in sample_medical_texts:
            response = integration_client.post(
                "/predict",
                json={"text": test_case["text"]}
            )
            
            assert response.status_code == 200
            data = response.json()
            
            # Verify response structure
            assert "predicted_class" in data
            assert "confidence" in data
            assert "probabilities" in data
            
            # Verify the predicted class is one of the expected categories
            expected_categories = [
                "Cancers",
                "Cardiovascular Diseases",
                "Metabolic & Endocrine Disorders",
                "Neurological & Cognitive Disorders",
                "Other Age-Related & Immune Disorders"
            ]
            assert data["predicted_class"] in expected_categories
    
    @pytest.mark.integration
    def test_predict_empty_text(self, integration_client):
        """Test prediction with empty text."""
        response = integration_client.post(
            "/predict",
            json={"text": ""}
        )
        
        # Should return validation error
        assert response.status_code == 422
        data = response.json()
        assert "detail" in data
    
    @pytest.mark.integration
    def test_predict_text_too_long(self, integration_client):
        """Test prediction with text exceeding maximum length."""
        long_text = "a" * 5001  # Exceeds max_length of 5000

        response = integration_client.post(
            "/predict",
            json={"text": long_text}
        )
        
        # Should return validation error
        assert response.status_code == 422
        data = response.json()
        assert "detail" in data
    
    @pytest.mark.integration
    def test_predict_missing_text_field(self, integration_client):
        """Test prediction with missing text field."""
        response = integration_client.post(
            "/predict",
            json={}
        )
        
        # Should return validation error
        assert response.status_code == 422
        data = response.json()
        assert "detail" in data
    
    @pytest.mark.integration
    def test_predict_invalid_json(self, integration_client):
        """Test prediction with invalid JSON."""
        response = integration_client.post(
            "/predict",
            data="invalid json",
            headers={"Content-Type": "application/json"}
        )
        
        # Should return validation error
        assert response.status_code == 422
    
    @pytest.mark.integration
    def test_predict_unicode_text(self, integration_client):
        """Test prediction with unicode text."""
        unicode_text = "¿Cuáles son los síntomas de la diabetes? 糖尿病の症状は何ですか？"

        response = integration_client.post(
            "/predict",
            json={"text": unicode_text}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert "predicted_class" in data
        assert "confidence" in data
        assert "probabilities" in data
    
    @pytest.mark.integration
    def test_predict_whitespace_text(self, integration_client):
        """Test prediction with whitespace-only text."""
        response = integration_client.post(
            "/predict",
            json={"text": "   \n\t  "}
        )

        # Whitespace-only text should be treated as empty and return an error
        assert response.status_code == 500
        data = response.json()
        assert "detail" in data
        assert "empty" in data["detail"].lower()
    
    @pytest.mark.integration
    def test_predict_response_schema(self, integration_client):
        """Test that prediction response matches expected schema."""
        response = integration_client.post(
            "/predict",
            json={"text": "What are the symptoms of diabetes?"}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify all required fields are present
        required_fields = ["predicted_class", "confidence", "probabilities"]
        for field in required_fields:
            assert field in data
        
        # Verify field types
        assert isinstance(data["predicted_class"], str)
        assert isinstance(data["confidence"], float)
        assert isinstance(data["probabilities"], dict)
        
        # Verify confidence bounds
        assert 0.0 <= data["confidence"] <= 1.0
        
        # Verify probabilities structure
        assert len(data["probabilities"]) == 5  # Should have all 5 categories
        for category, prob in data["probabilities"].items():
            assert isinstance(category, str)
            assert isinstance(prob, float)
            assert 0.0 <= prob <= 1.0


class TestRootEndpoint:
    """Test cases for root endpoint."""
    
    @pytest.mark.integration
    def test_root_endpoint(self, client):
        """Test root endpoint returns API information."""
        response = client.get("/")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "message" in data
        assert "version" in data
        assert "docs" in data
        assert "health" in data
        assert "predict" in data
        
        assert data["message"] == "Medical Text Classification API"
        assert data["version"] == "1.0.0"
        assert data["docs"] == "/docs"
        assert data["health"] == "/health"
        assert data["predict"] == "/predict"


class TestMetricsEndpoint:
    """Test cases for metrics endpoint."""
    
    @pytest.mark.integration
    def test_metrics_endpoint(self, client):
        """Test metrics endpoint returns Prometheus metrics."""
        response = client.get("/metrics")
        
        assert response.status_code == 200
        
        # Should return text/plain content type for Prometheus
        content_type = response.headers.get("content-type")
        assert "text/plain" in content_type or "application/openmetrics-text" in content_type
        
        # Response should contain metrics data
        content = response.text
        assert len(content) > 0


class TestCORSHeaders:
    """Test cases for CORS headers."""
    
    @pytest.mark.integration
    def test_cors_headers_present(self, client):
        """Test that CORS headers are present in responses."""
        # Make a request with Origin header to trigger CORS
        response = client.get(
            "/health",
            headers={"Origin": "http://localhost:3001"}
        )

        assert response.status_code == 200

        # Check for CORS headers
        headers = response.headers
        # CORS headers might be lowercase in test client
        header_keys = [key.lower() for key in headers.keys()]
        assert any("access-control-allow-origin" in key for key in header_keys)
    
    @pytest.mark.integration
    def test_options_request(self, client):
        """Test OPTIONS request for CORS preflight."""
        response = client.options(
            "/predict",
            headers={
                "Origin": "http://localhost:3001",
                "Access-Control-Request-Method": "POST",
                "Access-Control-Request-Headers": "Content-Type"
            }
        )
        
        # Should handle OPTIONS request
        assert response.status_code in [200, 204]


class TestErrorHandling:
    """Test cases for error handling."""
    
    @pytest.mark.integration
    def test_404_error(self, client):
        """Test 404 error for non-existent endpoint."""
        response = client.get("/nonexistent")
        
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
    
    @pytest.mark.integration
    def test_method_not_allowed(self, client):
        """Test 405 error for wrong HTTP method."""
        response = client.get("/predict")  # Should be POST
        
        assert response.status_code == 405
        data = response.json()
        assert "detail" in data
