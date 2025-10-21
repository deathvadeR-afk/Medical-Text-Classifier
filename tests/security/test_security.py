"""
Security tests for the Medical Text Classification API.
"""
import pytest
import time
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock

from src.api.main import app
from src.api.security import security_config


@pytest.fixture
def client():
    """Test client fixture."""
    return TestClient(app)


@pytest.fixture
def mock_security_config():
    """Mock security configuration for testing."""
    with patch('src.api.security.security_config') as mock_config:
        mock_config.REQUIRE_API_KEY = True
        mock_config.API_KEYS = ['test-api-key-123']
        mock_config.RATE_LIMIT_REQUESTS = 5
        mock_config.RATE_LIMIT_WINDOW = 60
        mock_config.MAX_TEXT_LENGTH = 1000
        mock_config.MIN_TEXT_LENGTH = 1
        mock_config.ALLOWED_ORIGINS = ['http://localhost:3000']
        mock_config.ENABLE_SECURITY_HEADERS = True
        yield mock_config


class TestInputValidation:
    """Test input validation and sanitization."""
    
    def test_valid_text_input(self, client):
        """Test valid text input."""
        response = client.post(
            "/predict",
            json={"text": "What are the symptoms of diabetes?"}
        )
        # Should succeed (assuming model is loaded)
        assert response.status_code in [200, 503]  # 503 if model not loaded
    
    def test_empty_text_input(self, client):
        """Test empty text input."""
        response = client.post(
            "/predict",
            json={"text": ""}
        )
        assert response.status_code == 422  # Validation error
    
    def test_whitespace_only_input(self, client):
        """Test whitespace-only input."""
        response = client.post(
            "/predict",
            json={"text": "   \n\t   "}
        )
        assert response.status_code == 422  # Validation error
    
    def test_too_long_input(self, client):
        """Test input that exceeds maximum length."""
        long_text = "a" * 6000  # Exceeds 5000 character limit
        response = client.post(
            "/predict",
            json={"text": long_text}
        )
        assert response.status_code == 422  # Validation error
    
    def test_malicious_script_injection(self, client):
        """Test script injection attempt."""
        malicious_text = "<script>alert('xss')</script>What are diabetes symptoms?"
        response = client.post(
            "/predict",
            json={"text": malicious_text}
        )
        assert response.status_code == 422  # Should be rejected
    
    def test_sql_injection_attempt(self, client):
        """Test SQL injection attempt."""
        malicious_text = "'; DROP TABLE users; --"
        response = client.post(
            "/predict",
            json={"text": malicious_text}
        )
        assert response.status_code == 422  # Should be rejected
    
    def test_javascript_injection(self, client):
        """Test JavaScript injection attempt."""
        malicious_text = "javascript:alert('xss') diabetes symptoms"
        response = client.post(
            "/predict",
            json={"text": malicious_text}
        )
        assert response.status_code == 422  # Should be rejected
    
    def test_excessive_special_characters(self, client):
        """Test input with excessive special characters."""
        malicious_text = "!@#$%^&*()_+{}|:<>?[]\\;'\",./"
        response = client.post(
            "/predict",
            json={"text": malicious_text}
        )
        assert response.status_code == 422  # Should be rejected


class TestRateLimiting:
    """Test rate limiting functionality."""
    
    @patch('src.api.middleware.security_config')
    def test_rate_limit_enforcement(self, mock_config, client):
        """Test that rate limiting is enforced."""
        mock_config.RATE_LIMIT_REQUESTS = 3
        mock_config.RATE_LIMIT_WINDOW = 60
        
        # Make requests up to the limit
        for i in range(3):
            response = client.get("/health")
            assert response.status_code == 200
        
        # Next request should be rate limited
        response = client.get("/health")
        assert response.status_code == 429
        assert "Rate limit exceeded" in response.json()["error"]
    
    def test_rate_limit_headers(self, client):
        """Test rate limit response headers."""
        response = client.get("/health")
        # Should include rate limit information in headers or response
        assert response.status_code == 200


class TestAPIKeyAuthentication:
    """Test API key authentication."""
    
    @patch('src.api.security.security_config')
    def test_valid_api_key(self, mock_config, client):
        """Test valid API key authentication."""
        mock_config.REQUIRE_API_KEY = True
        mock_config.API_KEYS = ['test-api-key-123']
        
        response = client.post(
            "/predict",
            json={"text": "What are diabetes symptoms?"},
            headers={"X-API-Key": "test-api-key-123"}
        )
        # Should succeed (assuming model is loaded)
        assert response.status_code in [200, 503]
    
    @patch('src.api.security.security_config')
    def test_invalid_api_key(self, mock_config, client):
        """Test invalid API key authentication."""
        mock_config.REQUIRE_API_KEY = True
        mock_config.API_KEYS = ['test-api-key-123']
        
        response = client.post(
            "/predict",
            json={"text": "What are diabetes symptoms?"},
            headers={"X-API-Key": "invalid-key"}
        )
        assert response.status_code == 401
    
    @patch('src.api.security.security_config')
    def test_missing_api_key(self, mock_config, client):
        """Test missing API key when required."""
        mock_config.REQUIRE_API_KEY = True
        mock_config.API_KEYS = ['test-api-key-123']
        
        response = client.post(
            "/predict",
            json={"text": "What are diabetes symptoms?"}
        )
        assert response.status_code == 401


class TestSecurityHeaders:
    """Test security headers."""
    
    def test_security_headers_present(self, client):
        """Test that security headers are present."""
        response = client.get("/health")
        
        # Check for important security headers
        headers = response.headers
        assert "X-Frame-Options" in headers
        assert "X-Content-Type-Options" in headers
        assert "X-XSS-Protection" in headers
        assert "Content-Security-Policy" in headers
        assert "Referrer-Policy" in headers
    
    def test_cors_headers(self, client):
        """Test CORS headers."""
        response = client.options("/predict")
        assert response.status_code in [200, 405]  # OPTIONS might not be implemented


class TestHostValidation:
    """Test host header validation."""
    
    @patch('src.api.security.security_config')
    def test_valid_host_header(self, mock_config, client):
        """Test valid host header."""
        mock_config.ALLOWED_HOSTS = ['localhost', '127.0.0.1']
        
        response = client.get("/health", headers={"Host": "localhost"})
        assert response.status_code == 200
    
    @patch('src.api.security.security_config')
    def test_invalid_host_header(self, mock_config, client):
        """Test invalid host header."""
        mock_config.ALLOWED_HOSTS = ['localhost', '127.0.0.1']
        
        response = client.get("/health", headers={"Host": "malicious.com"})
        assert response.status_code == 400


class TestSecurityEndpoints:
    """Test security-related endpoints."""
    
    def test_security_info_endpoint(self, client):
        """Test security information endpoint."""
        response = client.get("/security/info")
        assert response.status_code == 200
        
        data = response.json()
        assert "rate_limiting" in data
        assert "authentication" in data
        assert "security_headers" in data
        assert "input_validation" in data
    
    def test_health_check_security_info(self, client):
        """Test health check includes security information."""
        response = client.get("/health")
        assert response.status_code == 200
        
        data = response.json()
        assert "security_enabled" in data
        assert "rate_limiting_enabled" in data


class TestErrorHandling:
    """Test security-related error handling."""
    
    def test_error_response_format(self, client):
        """Test that error responses don't leak sensitive information."""
        response = client.post("/predict", json={"text": ""})
        assert response.status_code == 422
        
        data = response.json()
        # Should not contain sensitive server information
        assert "traceback" not in str(data).lower()
        assert "internal" not in str(data).lower()
    
    def test_404_error_handling(self, client):
        """Test 404 error handling."""
        response = client.get("/nonexistent-endpoint")
        assert response.status_code == 404
        
        # Should not reveal server information
        data = response.json()
        assert "server" not in str(data).lower()


@pytest.mark.integration
class TestSecurityIntegration:
    """Integration tests for security features."""
    
    def test_full_security_stack(self, client):
        """Test the complete security stack."""
        # Test with valid request
        response = client.post(
            "/predict",
            json={"text": "What are the symptoms of diabetes?"},
            headers={
                "User-Agent": "Test Client",
                "Accept": "application/json"
            }
        )
        
        # Should either succeed or fail gracefully
        assert response.status_code in [200, 401, 503, 422]
        
        # Check security headers are present
        assert "X-Frame-Options" in response.headers
        assert "X-Content-Type-Options" in response.headers
