"""
End-to-end tests for the complete medical text classification pipeline.
"""
import pytest
import requests
import time
from typing import Dict, Any


class TestFullPipeline:
    """Test the complete pipeline from API to prediction."""
    
    @pytest.mark.slow
    @pytest.mark.e2e
    def test_api_server_running(self):
        """Test that the API server is running and accessible."""
        try:
            response = requests.get("http://localhost:8000/health", timeout=5)
            assert response.status_code == 200
        except requests.exceptions.ConnectionError:
            pytest.skip("API server not running on localhost:8000")
    
    @pytest.mark.slow
    @pytest.mark.e2e
    def test_health_check_e2e(self):
        """Test health check endpoint end-to-end."""
        try:
            response = requests.get("http://localhost:8000/health", timeout=5)
            assert response.status_code == 200
            
            data = response.json()
            assert "status" in data
            assert "model_loaded" in data
            assert "database_connected" in data
            
            # In a real deployment, we'd expect these to be True
            assert data["status"] == "healthy"
            
        except requests.exceptions.ConnectionError:
            pytest.skip("API server not running on localhost:8000")
    
    @pytest.mark.slow
    @pytest.mark.e2e
    def test_prediction_e2e(self):
        """Test prediction endpoint end-to-end."""
        try:
            # Test diabetes-related text
            response = requests.post(
                "http://localhost:8000/predict",
                json={"text": "What are the symptoms of diabetes?"},
                timeout=10
            )
            
            assert response.status_code == 200
            data = response.json()
            
            assert "predicted_class" in data
            assert "confidence" in data
            assert "probabilities" in data
            
            # Should predict metabolic category for diabetes
            assert data["predicted_class"] == "Metabolic & Endocrine Disorders"
            assert data["confidence"] >= 0.7  # Should have reasonable confidence
            
        except requests.exceptions.ConnectionError:
            pytest.skip("API server not running on localhost:8000")
    
    @pytest.mark.slow
    @pytest.mark.e2e
    def test_multiple_predictions_e2e(self):
        """Test multiple predictions to verify consistency."""
        test_cases = [
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
            }
        ]
        
        try:
            for test_case in test_cases:
                response = requests.post(
                    "http://localhost:8000/predict",
                    json={"text": test_case["text"]},
                    timeout=10
                )
                
                assert response.status_code == 200
                data = response.json()
                
                # Verify response structure
                assert "predicted_class" in data
                assert "confidence" in data
                assert "probabilities" in data
                
                # Verify prediction matches expected category
                assert data["predicted_class"] == test_case["expected_category"]
                
                # Add small delay between requests
                time.sleep(0.1)
                
        except requests.exceptions.ConnectionError:
            pytest.skip("API server not running on localhost:8000")
    
    @pytest.mark.slow
    @pytest.mark.e2e
    def test_api_performance(self):
        """Test API response time performance."""
        try:
            start_time = time.time()
            
            response = requests.post(
                "http://localhost:8000/predict",
                json={"text": "What are the symptoms of diabetes?"},
                timeout=10
            )
            
            end_time = time.time()
            response_time = end_time - start_time
            
            assert response.status_code == 200
            
            # API should respond within reasonable time (5 seconds for rule-based)
            assert response_time < 5.0
            
        except requests.exceptions.ConnectionError:
            pytest.skip("API server not running on localhost:8000")
    
    @pytest.mark.slow
    @pytest.mark.e2e
    def test_concurrent_requests(self):
        """Test handling of concurrent requests."""
        import concurrent.futures
        import threading
        
        def make_request(text: str) -> Dict[str, Any]:
            """Make a single prediction request."""
            try:
                response = requests.post(
                    "http://localhost:8000/predict",
                    json={"text": text},
                    timeout=10
                )
                return {
                    "status_code": response.status_code,
                    "data": response.json() if response.status_code == 200 else None,
                    "error": None
                }
            except Exception as e:
                return {
                    "status_code": None,
                    "data": None,
                    "error": str(e)
                }
        
        try:
            # Test with multiple concurrent requests
            test_texts = [
                "What are the symptoms of diabetes?",
                "I have chest pain and shortness of breath",
                "What are the treatment options for breast cancer?",
                "My grandmother has Alzheimer's disease",
                "How to manage arthritis symptoms?"
            ]
            
            with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
                futures = [executor.submit(make_request, text) for text in test_texts]
                results = [future.result() for future in concurrent.futures.as_completed(futures)]
            
            # All requests should succeed
            for result in results:
                if result["error"] and "Connection" in result["error"]:
                    pytest.skip("API server not running on localhost:8000")
                
                assert result["status_code"] == 200
                assert result["data"] is not None
                assert "predicted_class" in result["data"]
                
        except requests.exceptions.ConnectionError:
            pytest.skip("API server not running on localhost:8000")
    
    @pytest.mark.slow
    @pytest.mark.e2e
    def test_error_handling_e2e(self):
        """Test error handling in the complete pipeline."""
        try:
            # Test with invalid input
            response = requests.post(
                "http://localhost:8000/predict",
                json={"text": ""},  # Empty text should fail validation
                timeout=5
            )
            
            assert response.status_code == 422  # Validation error
            data = response.json()
            assert "detail" in data
            
        except requests.exceptions.ConnectionError:
            pytest.skip("API server not running on localhost:8000")
    
    @pytest.mark.slow
    @pytest.mark.e2e
    def test_metrics_endpoint_e2e(self):
        """Test metrics endpoint end-to-end."""
        try:
            # Make a prediction first to generate some metrics
            requests.post(
                "http://localhost:8000/predict",
                json={"text": "What are the symptoms of diabetes?"},
                timeout=5
            )
            
            # Check metrics endpoint
            response = requests.get("http://localhost:8000/metrics", timeout=5)
            assert response.status_code == 200
            
            # Should contain Prometheus metrics
            content = response.text
            assert len(content) > 0
            
            # Should contain some expected metric names
            assert "prediction_count" in content or "http_requests" in content
            
        except requests.exceptions.ConnectionError:
            pytest.skip("API server not running on localhost:8000")


class TestFrontendIntegration:
    """Test integration with frontend application."""
    
    @pytest.mark.slow
    @pytest.mark.e2e
    def test_frontend_server_running(self):
        """Test that the frontend server is running."""
        try:
            response = requests.get("http://localhost:3001", timeout=5)
            assert response.status_code == 200
            
            # Should return HTML content
            content = response.text
            assert "<!DOCTYPE html>" in content
            assert "Medical Text Classifier" in content
            
        except requests.exceptions.ConnectionError:
            pytest.skip("Frontend server not running on localhost:3001")
    
    @pytest.mark.slow
    @pytest.mark.e2e
    def test_frontend_api_proxy(self):
        """Test that frontend can proxy requests to API."""
        try:
            # Test prediction through frontend proxy
            response = requests.post(
                "http://localhost:3001/predict",
                json={"text": "What are the symptoms of diabetes?"},
                timeout=10
            )
            
            assert response.status_code == 200
            data = response.json()
            
            assert "predicted_class" in data
            assert "confidence" in data
            assert "probabilities" in data
            
        except requests.exceptions.ConnectionError:
            pytest.skip("Frontend server not running on localhost:3001 or API proxy not configured")


class TestSystemIntegration:
    """Test complete system integration."""
    
    @pytest.mark.slow
    @pytest.mark.e2e
    def test_full_user_workflow(self):
        """Test a complete user workflow from frontend to API."""
        try:
            # 1. Check that frontend is accessible
            frontend_response = requests.get("http://localhost:3001", timeout=5)
            assert frontend_response.status_code == 200
            
            # 2. Check that API health is good
            health_response = requests.get("http://localhost:8000/health", timeout=5)
            assert health_response.status_code == 200
            health_data = health_response.json()
            assert health_data["status"] == "healthy"
            
            # 3. Make a prediction through the API
            prediction_response = requests.post(
                "http://localhost:8000/predict",
                json={"text": "What are the symptoms of diabetes?"},
                timeout=10
            )
            assert prediction_response.status_code == 200
            prediction_data = prediction_response.json()
            
            # 4. Verify prediction quality
            assert prediction_data["predicted_class"] == "Metabolic & Endocrine Disorders"
            assert prediction_data["confidence"] >= 0.7
            
            # 5. Test prediction through frontend proxy
            proxy_response = requests.post(
                "http://localhost:3001/predict",
                json={"text": "What are the symptoms of diabetes?"},
                timeout=10
            )
            assert proxy_response.status_code == 200
            proxy_data = proxy_response.json()
            
            # Results should be consistent
            assert proxy_data["predicted_class"] == prediction_data["predicted_class"]
            assert proxy_data["confidence"] == prediction_data["confidence"]
            
        except requests.exceptions.ConnectionError as e:
            pytest.skip(f"System not fully running: {e}")
