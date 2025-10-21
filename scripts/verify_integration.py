#!/usr/bin/env python3
"""
Integration Verification Script
Medical Text Classification App

This script verifies that all components are properly integrated and working together.
Run this after deployment to ensure everything is functioning correctly.
"""

import sys
import time
import requests
import json
from typing import Dict, List, Tuple
from dataclasses import dataclass

@dataclass
class TestResult:
    name: str
    passed: bool
    message: str
    duration: float

class IntegrationVerifier:
    def __init__(self, base_url: str = "http://localhost:8000", api_key: str = None):
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.session = requests.Session()
        
        if api_key:
            self.session.headers.update({"X-API-Key": api_key})
        
        self.results: List[TestResult] = []

    def run_test(self, test_name: str, test_func) -> TestResult:
        """Run a single test and record the result."""
        print(f"🔍 Testing {test_name}...", end=" ")
        start_time = time.time()
        
        try:
            test_func()
            duration = time.time() - start_time
            result = TestResult(test_name, True, "✅ PASSED", duration)
            print(f"✅ PASSED ({duration:.2f}s)")
        except Exception as e:
            duration = time.time() - start_time
            result = TestResult(test_name, False, f"❌ FAILED: {str(e)}", duration)
            print(f"❌ FAILED: {str(e)}")
        
        self.results.append(result)
        return result

    def test_health_check(self):
        """Test health check endpoint."""
        response = self.session.get(f"{self.base_url}/health", timeout=10)
        response.raise_for_status()
        
        data = response.json()
        assert "status" in data, "Health response missing status"
        assert "components" in data, "Health response missing components"
        
        # Check component health
        components = data["components"]
        for component, details in components.items():
            if details.get("status") == "unhealthy":
                raise AssertionError(f"Component {component} is unhealthy")

    def test_prediction_endpoint(self):
        """Test prediction endpoint functionality."""
        test_text = "What are the symptoms of diabetes and how is it diagnosed?"
        
        response = self.session.post(
            f"{self.base_url}/predict",
            json={"text": test_text},
            timeout=30
        )
        response.raise_for_status()
        
        data = response.json()
        
        # Verify response structure
        required_fields = ["predicted_class", "confidence", "focus_group", "probabilities"]
        for field in required_fields:
            assert field in data, f"Response missing field: {field}"
        
        # Verify data types and ranges
        assert isinstance(data["predicted_class"], int), "predicted_class should be int"
        assert 0 <= data["predicted_class"] <= 4, "predicted_class out of range"
        assert isinstance(data["confidence"], (int, float)), "confidence should be numeric"
        assert 0 <= data["confidence"] <= 1, "confidence out of range"
        assert len(data["probabilities"]) == 5, "probabilities should have 5 elements"

    def test_input_validation(self):
        """Test input validation."""
        # Test empty text
        response = self.session.post(
            f"{self.base_url}/predict",
            json={"text": ""},
            timeout=10
        )
        assert response.status_code == 422, "Empty text should return 422"
        
        # Test text too long
        long_text = "a" * 5001
        response = self.session.post(
            f"{self.base_url}/predict",
            json={"text": long_text},
            timeout=10
        )
        assert response.status_code == 422, "Long text should return 422"

    def test_security_headers(self):
        """Test security headers are present."""
        response = self.session.get(f"{self.base_url}/health", timeout=10)
        response.raise_for_status()
        
        headers = response.headers
        security_headers = [
            "x-frame-options",
            "x-content-type-options",
            "x-xss-protection"
        ]
        
        missing_headers = []
        for header in security_headers:
            if header not in headers and header.replace("-", "_") not in headers:
                missing_headers.append(header)
        
        if missing_headers:
            raise AssertionError(f"Missing security headers: {missing_headers}")

    def test_cors_configuration(self):
        """Test CORS configuration."""
        response = self.session.options(
            f"{self.base_url}/predict",
            headers={
                "Origin": "http://localhost:3000",
                "Access-Control-Request-Method": "POST",
                "Access-Control-Request-Headers": "Content-Type"
            },
            timeout=10
        )
        
        # CORS preflight should not fail
        assert response.status_code in [200, 204], "CORS preflight failed"

    def test_metrics_endpoint(self):
        """Test metrics endpoint."""
        response = self.session.get(f"{self.base_url}/metrics", timeout=10)
        response.raise_for_status()
        
        metrics_text = response.text
        expected_metrics = ["http_requests_total", "http_request_duration_seconds"]
        
        for metric in expected_metrics:
            assert metric in metrics_text, f"Missing metric: {metric}"

    def test_api_documentation(self):
        """Test API documentation endpoint."""
        response = self.session.get(f"{self.base_url}/docs", timeout=10)
        response.raise_for_status()
        
        # Should return HTML content
        assert "text/html" in response.headers.get("content-type", "")
        assert "swagger" in response.text.lower() or "openapi" in response.text.lower()

    def test_performance(self):
        """Test basic performance characteristics."""
        start_time = time.time()
        
        response = self.session.post(
            f"{self.base_url}/predict",
            json={"text": "What are the symptoms of diabetes?"},
            timeout=30
        )
        
        response_time = time.time() - start_time
        response.raise_for_status()
        
        # Should respond within reasonable time
        assert response_time < 10.0, f"Response too slow: {response_time:.2f}s"
        
        data = response.json()
        if "processing_time_ms" in data:
            processing_time = data["processing_time_ms"]
            assert processing_time < 5000, f"Processing too slow: {processing_time}ms"

    def test_error_handling(self):
        """Test error handling."""
        # Test 404
        response = self.session.get(f"{self.base_url}/nonexistent", timeout=10)
        assert response.status_code == 404, "Should return 404 for nonexistent endpoint"
        
        # Test 405
        response = self.session.delete(f"{self.base_url}/predict", timeout=10)
        assert response.status_code == 405, "Should return 405 for wrong method"

    def test_classification_accuracy(self):
        """Test classification accuracy with known examples."""
        test_cases = [
            ("What are the symptoms of diabetes?", "Metabolic & Endocrine Disorders"),
            ("Heart attack symptoms and treatment", "Cardiovascular Diseases"),
            ("Alzheimer's disease progression", "Neurological & Cognitive Disorders"),
            ("Breast cancer screening", "Cancers"),
            ("Arthritis pain management", "Other Age-Related & Immune Disorders")
        ]
        
        correct_predictions = 0
        
        for text, expected_group in test_cases:
            response = self.session.post(
                f"{self.base_url}/predict",
                json={"text": text},
                timeout=30
            )
            response.raise_for_status()
            
            data = response.json()
            predicted_group = data["focus_group"]
            
            if predicted_group == expected_group:
                correct_predictions += 1
        
        accuracy = correct_predictions / len(test_cases)
        assert accuracy >= 0.6, f"Classification accuracy too low: {accuracy:.2f}"

    def run_all_tests(self) -> bool:
        """Run all integration tests."""
        print(f"🚀 Starting integration verification for {self.base_url}")
        print("=" * 60)
        
        # Define all tests
        tests = [
            ("Health Check", self.test_health_check),
            ("Prediction Endpoint", self.test_prediction_endpoint),
            ("Input Validation", self.test_input_validation),
            ("Security Headers", self.test_security_headers),
            ("CORS Configuration", self.test_cors_configuration),
            ("Metrics Endpoint", self.test_metrics_endpoint),
            ("API Documentation", self.test_api_documentation),
            ("Performance", self.test_performance),
            ("Error Handling", self.test_error_handling),
            ("Classification Accuracy", self.test_classification_accuracy)
        ]
        
        # Run all tests
        for test_name, test_func in tests:
            self.run_test(test_name, test_func)
        
        # Print summary
        self.print_summary()
        
        # Return overall success
        return all(result.passed for result in self.results)

    def print_summary(self):
        """Print test summary."""
        print("\n" + "=" * 60)
        print("📊 INTEGRATION VERIFICATION SUMMARY")
        print("=" * 60)
        
        passed = sum(1 for r in self.results if r.passed)
        total = len(self.results)
        
        print(f"Total Tests: {total}")
        print(f"Passed: {passed}")
        print(f"Failed: {total - passed}")
        print(f"Success Rate: {passed/total*100:.1f}%")
        
        total_time = sum(r.duration for r in self.results)
        print(f"Total Time: {total_time:.2f}s")
        
        if total - passed > 0:
            print("\n❌ FAILED TESTS:")
            for result in self.results:
                if not result.passed:
                    print(f"  • {result.name}: {result.message}")
        
        print("\n" + "=" * 60)
        
        if passed == total:
            print("🎉 ALL TESTS PASSED! System is ready for production.")
        else:
            print("⚠️  SOME TESTS FAILED! Please review and fix issues.")

def main():
    """Main function."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Verify Medical Text Classification integration")
    parser.add_argument("--url", default="http://localhost:8000", help="API base URL")
    parser.add_argument("--api-key", help="API key for authentication")
    parser.add_argument("--timeout", type=int, default=30, help="Request timeout in seconds")
    
    args = parser.parse_args()
    
    # Create verifier
    verifier = IntegrationVerifier(args.url, args.api_key)
    
    # Run tests
    try:
        success = verifier.run_all_tests()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Verification interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Verification failed with error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
