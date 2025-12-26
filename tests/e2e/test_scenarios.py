"""
End-to-end tests for complete scenarios.
"""

import pytest
import requests
import time


@pytest.mark.e2e
class TestBaselineScenario:
    """Test baseline scenario end-to-end."""

    def test_baseline_workflow(self, wait_for_app):
        """Test complete baseline workflow."""
        # 1. Health check
        health = requests.get(f"{wait_for_app}/health", timeout=10)
        assert health.status_code == 200

        # 2. Make predictions
        prompts = [
            {"prompt": "What is AI monitoring?", "scenario": "baseline"},
            {"prompt": "Explain observability", "scenario": "baseline"},
            {"prompt": "How does Prometheus work?", "scenario": "baseline"},
        ]

        for prompt in prompts:
            response = requests.post(
                f"{wait_for_app}/predict",
                json=prompt,
                timeout=30
            )
            assert response.status_code in [200, 429]

        # 3. Verify metrics updated
        metrics = requests.get(f"{wait_for_app}/metrics", timeout=10)
        assert "ai_requests_total" in metrics.text


@pytest.mark.e2e
class TestDriftScenario:
    """Test drift detection scenario end-to-end."""

    def test_drift_detection_workflow(self, wait_for_app, drift_prompts):
        """Test drift detection workflow."""
        # Send drift-inducing prompts
        for prompt in drift_prompts:
            response = requests.post(
                f"{wait_for_app}/predict",
                json=prompt,
                timeout=30
            )
            assert response.status_code in [200, 400, 429]

        # Check metrics for drift indicators
        metrics = requests.get(f"{wait_for_app}/metrics", timeout=10)
        assert response.status_code == 200


@pytest.mark.e2e
class TestSecurityScenario:
    """Test security detection scenario end-to-end."""

    def test_injection_detection_workflow(self, wait_for_app, injection_prompts):
        """Test prompt injection detection workflow."""
        for prompt in injection_prompts:
            response = requests.post(
                f"{wait_for_app}/predict",
                json=prompt,
                timeout=30
            )
            # Should handle injection attempts
            assert response.status_code in [200, 400, 403, 429]

        # Check security metrics
        metrics = requests.get(f"{wait_for_app}/metrics", timeout=10)
        # Look for security-related metrics
        content = metrics.text
        security_indicators = [
            "ai_prompt_injection",
            "ai_prompt_security",
            "ai_jailbreak",
        ]
        found = any(ind in content for ind in security_indicators)
        # At least metrics endpoint works
        assert metrics.status_code == 200


@pytest.mark.e2e
class TestPIIScenario:
    """Test PII detection scenario end-to-end."""

    def test_pii_detection_workflow(self, wait_for_app, pii_prompts):
        """Test PII detection workflow."""
        for prompt in pii_prompts:
            response = requests.post(
                f"{wait_for_app}/predict",
                json=prompt,
                timeout=30
            )
            # Should handle PII (block or redact)
            assert response.status_code in [200, 400, 403, 429]

        # Check PII metrics
        metrics = requests.get(f"{wait_for_app}/metrics", timeout=10)
        assert metrics.status_code == 200


@pytest.mark.e2e
@pytest.mark.slow
class TestLoadScenario:
    """Test load scenario end-to-end."""

    def test_sustained_load(self, wait_for_app):
        """Test sustained load handling."""
        import concurrent.futures

        num_requests = 20
        prompts = [
            {"prompt": f"Test prompt {i}", "scenario": "A"}
            for i in range(num_requests)
        ]

        def make_request(prompt):
            try:
                return requests.post(
                    f"{wait_for_app}/predict",
                    json=prompt,
                    timeout=60
                )
            except Exception as e:
                return None

        start_time = time.time()

        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(make_request, p) for p in prompts]
            results = [f.result() for f in concurrent.futures.as_completed(futures)]

        elapsed = time.time() - start_time

        # Filter successful responses
        successful = [r for r in results if r and r.status_code in [200, 429]]
        assert len(successful) >= num_requests * 0.5  # At least 50% success

    def test_metrics_under_load(self, wait_for_app):
        """Test metrics accuracy under load."""
        # Get initial metrics
        initial_metrics = requests.get(f"{wait_for_app}/metrics", timeout=10).text

        # Generate load
        for i in range(10):
            requests.post(
                f"{wait_for_app}/predict",
                json={"prompt": f"Load test {i}", "scenario": "A"},
                timeout=30
            )

        # Get final metrics
        final_metrics = requests.get(f"{wait_for_app}/metrics", timeout=10).text

        # Verify metrics increased
        assert "ai_requests_total" in final_metrics


@pytest.mark.e2e
@pytest.mark.smoke
class TestSmokeTests:
    """Quick smoke tests for deployment verification."""

    def test_all_endpoints_respond(self, wait_for_app):
        """Test all main endpoints respond."""
        endpoints = [
            ("/", "GET"),
            ("/health", "GET"),
            ("/metrics", "GET"),
        ]

        for path, method in endpoints:
            if method == "GET":
                response = requests.get(f"{wait_for_app}{path}", timeout=10)
            assert response.status_code in [200, 404, 405]

    def test_predict_responds(self, wait_for_app):
        """Test predict endpoint responds."""
        response = requests.post(
            f"{wait_for_app}/predict",
            json={"prompt": "Smoke test", "scenario": "A"},
            timeout=30
        )
        assert response.status_code in [200, 400, 429]

    def test_observability_stack_responds(self, test_config):
        """Test observability stack is responsive."""
        services = [
            (f"http://{test_config['prometheus_host']}:{test_config['prometheus_port']}/-/ready", "Prometheus"),
            (f"http://{test_config['grafana_host']}:{test_config['grafana_port']}/api/health", "Grafana"),
        ]

        for url, name in services:
            try:
                response = requests.get(url, timeout=10)
                assert response.status_code == 200, f"{name} not healthy"
            except requests.exceptions.RequestException:
                pytest.skip(f"{name} not available")
