"""
Performance and load tests for the medical text classification API.
"""
import pytest
import time
import statistics
import concurrent.futures
from typing import List, Dict, Any
from fastapi.testclient import TestClient


class TestAPIPerformance:
    """Test API performance characteristics."""
    
    @pytest.mark.slow
    @pytest.mark.performance
    def test_prediction_response_time(self, client):
        """Test individual prediction response time."""
        test_text = "What are the symptoms of diabetes?"
        response_times = []
        
        # Warm up
        for _ in range(3):
            client.post("/predict", json={"text": test_text})
        
        # Measure response times
        for _ in range(10):
            start_time = time.time()
            response = client.post("/predict", json={"text": test_text})
            end_time = time.time()
            
            assert response.status_code == 200
            response_times.append(end_time - start_time)
        
        # Analyze performance
        avg_time = statistics.mean(response_times)
        max_time = max(response_times)
        min_time = min(response_times)
        
        # Rule-based classification should be very fast
        assert avg_time < 0.1  # Average under 100ms
        assert max_time < 0.5  # Max under 500ms
        assert min_time < 0.05  # Min under 50ms
        
        print(f"Response time stats: avg={avg_time:.3f}s, min={min_time:.3f}s, max={max_time:.3f}s")
    
    @pytest.mark.slow
    @pytest.mark.performance
    def test_health_check_performance(self, client):
        """Test health check endpoint performance."""
        response_times = []
        
        # Measure health check response times
        for _ in range(20):
            start_time = time.time()
            response = client.get("/health")
            end_time = time.time()
            
            assert response.status_code == 200
            response_times.append(end_time - start_time)
        
        # Health check should be very fast
        avg_time = statistics.mean(response_times)
        max_time = max(response_times)
        
        assert avg_time < 0.05  # Average under 50ms
        assert max_time < 0.1   # Max under 100ms
        
        print(f"Health check time stats: avg={avg_time:.3f}s, max={max_time:.3f}s")
    
    @pytest.mark.slow
    @pytest.mark.performance
    def test_concurrent_predictions(self, client):
        """Test performance under concurrent load."""
        def make_prediction(text: str) -> Dict[str, Any]:
            """Make a single prediction and measure time."""
            start_time = time.time()
            response = client.post("/predict", json={"text": text})
            end_time = time.time()
            
            return {
                "status_code": response.status_code,
                "response_time": end_time - start_time,
                "success": response.status_code == 200
            }
        
        # Test texts
        test_texts = [
            "What are the symptoms of diabetes?",
            "I have chest pain and shortness of breath",
            "What are the treatment options for breast cancer?",
            "My grandmother has Alzheimer's disease",
            "How to manage arthritis symptoms?"
        ] * 4  # 20 total requests
        
        # Execute concurrent requests
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(make_prediction, text) for text in test_texts]
            results = [future.result() for future in concurrent.futures.as_completed(futures)]
        
        # Analyze results
        successful_requests = [r for r in results if r["success"]]
        response_times = [r["response_time"] for r in successful_requests]
        
        assert len(successful_requests) == len(test_texts)  # All should succeed
        
        avg_time = statistics.mean(response_times)
        max_time = max(response_times)
        p95_time = statistics.quantiles(response_times, n=20)[18]  # 95th percentile
        
        # Performance should not degrade significantly under load
        assert avg_time < 0.2   # Average under 200ms
        assert max_time < 1.0   # Max under 1s
        assert p95_time < 0.5   # 95th percentile under 500ms
        
        print(f"Concurrent load stats: avg={avg_time:.3f}s, max={max_time:.3f}s, p95={p95_time:.3f}s")
    
    @pytest.mark.slow
    @pytest.mark.performance
    def test_memory_usage_stability(self, client):
        """Test that memory usage remains stable under repeated requests."""
        import psutil
        import os
        
        # Get current process
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # Make many requests
        for i in range(100):
            response = client.post(
                "/predict", 
                json={"text": f"Test medical text number {i} about diabetes symptoms"}
            )
            assert response.status_code == 200
            
            # Check memory every 20 requests
            if i % 20 == 0:
                current_memory = process.memory_info().rss / 1024 / 1024  # MB
                memory_increase = current_memory - initial_memory
                
                # Memory should not increase significantly (allow 50MB increase)
                assert memory_increase < 50, f"Memory increased by {memory_increase:.1f}MB"
        
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        total_increase = final_memory - initial_memory
        
        print(f"Memory usage: initial={initial_memory:.1f}MB, final={final_memory:.1f}MB, increase={total_increase:.1f}MB")
    
    @pytest.mark.slow
    @pytest.mark.performance
    def test_throughput(self, client):
        """Test API throughput (requests per second)."""
        num_requests = 50
        test_text = "What are the symptoms of diabetes?"
        
        start_time = time.time()
        
        for _ in range(num_requests):
            response = client.post("/predict", json={"text": test_text})
            assert response.status_code == 200
        
        end_time = time.time()
        total_time = end_time - start_time
        throughput = num_requests / total_time
        
        # Should handle at least 20 requests per second
        assert throughput >= 20, f"Throughput too low: {throughput:.1f} req/s"
        
        print(f"Throughput: {throughput:.1f} requests/second")


class TestScalabilityLimits:
    """Test scalability limits and edge cases."""
    
    @pytest.mark.slow
    @pytest.mark.performance
    def test_large_text_input(self, client):
        """Test performance with large text inputs."""
        # Test with maximum allowed text length
        large_text = "This is a medical text about diabetes symptoms. " * 100  # ~4700 chars
        
        start_time = time.time()
        response = client.post("/predict", json={"text": large_text})
        end_time = time.time()
        
        assert response.status_code == 200
        response_time = end_time - start_time
        
        # Should still be reasonably fast even with large input
        assert response_time < 1.0  # Under 1 second
        
        print(f"Large text ({len(large_text)} chars) response time: {response_time:.3f}s")
    
    @pytest.mark.slow
    @pytest.mark.performance
    def test_rapid_sequential_requests(self, client):
        """Test performance with rapid sequential requests."""
        response_times = []
        
        for i in range(50):
            start_time = time.time()
            response = client.post(
                "/predict", 
                json={"text": f"Medical text {i} about various symptoms"}
            )
            end_time = time.time()
            
            assert response.status_code == 200
            response_times.append(end_time - start_time)
        
        # Check for performance degradation
        first_10_avg = statistics.mean(response_times[:10])
        last_10_avg = statistics.mean(response_times[-10:])
        
        # Performance should not degrade significantly
        degradation_ratio = last_10_avg / first_10_avg
        assert degradation_ratio < 2.0, f"Performance degraded by {degradation_ratio:.1f}x"
        
        print(f"Sequential requests: first_10_avg={first_10_avg:.3f}s, last_10_avg={last_10_avg:.3f}s")
    
    @pytest.mark.slow
    @pytest.mark.performance
    def test_stress_test(self, client):
        """Stress test with high concurrent load."""
        def stress_worker(worker_id: int, num_requests: int) -> List[float]:
            """Worker function for stress testing."""
            response_times = []
            
            for i in range(num_requests):
                start_time = time.time()
                response = client.post(
                    "/predict",
                    json={"text": f"Worker {worker_id} request {i} about medical symptoms"}
                )
                end_time = time.time()
                
                if response.status_code == 200:
                    response_times.append(end_time - start_time)
            
            return response_times
        
        # High concurrent load
        num_workers = 20
        requests_per_worker = 10
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=num_workers) as executor:
            futures = [
                executor.submit(stress_worker, worker_id, requests_per_worker)
                for worker_id in range(num_workers)
            ]
            
            all_response_times = []
            for future in concurrent.futures.as_completed(futures):
                worker_times = future.result()
                all_response_times.extend(worker_times)
        
        # Analyze stress test results
        total_requests = num_workers * requests_per_worker
        successful_requests = len(all_response_times)
        success_rate = successful_requests / total_requests
        
        assert success_rate >= 0.95  # At least 95% success rate
        
        if all_response_times:
            avg_time = statistics.mean(all_response_times)
            max_time = max(all_response_times)
            p99_time = statistics.quantiles(all_response_times, n=100)[98]  # 99th percentile
            
            # Performance under stress should still be reasonable
            assert avg_time < 1.0   # Average under 1s
            assert p99_time < 2.0   # 99th percentile under 2s
            
            print(f"Stress test: {successful_requests}/{total_requests} successful, "
                  f"avg={avg_time:.3f}s, max={max_time:.3f}s, p99={p99_time:.3f}s")


class TestResourceUsage:
    """Test resource usage patterns."""
    
    @pytest.mark.slow
    @pytest.mark.performance
    def test_cpu_usage(self, client):
        """Test CPU usage during load."""
        import psutil
        import threading
        
        cpu_percentages = []
        monitoring = True
        
        def monitor_cpu():
            """Monitor CPU usage in background."""
            while monitoring:
                cpu_percent = psutil.cpu_percent(interval=0.1)
                cpu_percentages.append(cpu_percent)
        
        # Start CPU monitoring
        monitor_thread = threading.Thread(target=monitor_cpu)
        monitor_thread.start()
        
        try:
            # Generate load
            for _ in range(30):
                response = client.post(
                    "/predict",
                    json={"text": "What are the symptoms of diabetes?"}
                )
                assert response.status_code == 200
                time.sleep(0.1)  # Small delay between requests
        finally:
            monitoring = False
            monitor_thread.join()
        
        if cpu_percentages:
            avg_cpu = statistics.mean(cpu_percentages)
            max_cpu = max(cpu_percentages)
            
            # CPU usage should be reasonable
            assert avg_cpu < 80  # Average under 80%
            assert max_cpu < 95  # Max under 95%
            
            print(f"CPU usage: avg={avg_cpu:.1f}%, max={max_cpu:.1f}%")
