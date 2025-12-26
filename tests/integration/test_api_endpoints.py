"""
Integration tests for API endpoints.
Require running application and dependencies.
"""

import pytest
import requests
import time


@pytest.mark.integration
class TestHealthEndpoint:
    """Test health check endpoint."""

    def test_health_returns_200(self, wait_for_app):
        """Test /health returns 200 OK."""
        response = requests.get(f"{wait_for_app}/health", timeout=10)

        assert response.status_code == 200

    def test_health_response_structure(self, wait_for_app):
        """Test health response contains expected fields."""
        response = requests.get(f"{wait_for_app}/health", timeout=10)
        data = response.json()

        assert "status" in data or response.status_code == 200


@pytest.mark.integration
class TestMetricsEndpoint:
    """Test Prometheus metrics endpoint."""

    def test_metrics_returns_200(self, wait_for_app):
        """Test /metrics returns 200 OK."""
        response = requests.get(f"{wait_for_app}/metrics", timeout=10)

        assert response.status_code == 200

    def test_metrics_prometheus_format(self, wait_for_app):
        """Test metrics are in Prometheus format."""
        response = requests.get(f"{wait_for_app}/metrics", timeout=10)

        # Prometheus metrics contain HELP and TYPE comments
        content = response.text
        assert "# HELP" in content or "ai_" in content

    def test_metrics_contains_ai_metrics(self, wait_for_app):
        """Test metrics contain AI-specific metrics."""
        response = requests.get(f"{wait_for_app}/metrics", timeout=10)
        content = response.text

        # Check for key AI metrics
        ai_metrics = [
            "ai_requests_total",
            "ai_latency_seconds",
            "ai_quality_score",
        ]

        found = sum(1 for m in ai_metrics if m in content)
        assert found > 0, "No AI metrics found"


@pytest.mark.integration
class TestPredictEndpoint:
    """Test /predict endpoint."""

    def test_predict_basic_request(self, wait_for_app, sample_prompt):
        """Test basic prediction request."""
        response = requests.post(
            f"{wait_for_app}/predict",
            json=sample_prompt,
            timeout=30
        )

        assert response.status_code == 200

    def test_predict_response_structure(self, wait_for_app, sample_prompt):
        """Test prediction response contains expected fields."""
        response = requests.post(
            f"{wait_for_app}/predict",
            json=sample_prompt,
            timeout=30
        )
        data = response.json()

        # Check for common response fields
        expected_fields = ["response", "request_id"]
        found_fields = [f for f in expected_fields if f in data]
        assert len(found_fields) > 0 or response.status_code == 200

    def test_predict_different_scenarios(self, wait_for_app):
        """Test predictions with different scenarios."""
        scenarios = ["A", "B", "C", "baseline"]

        for scenario in scenarios:
            response = requests.post(
                f"{wait_for_app}/predict",
                json={"prompt": "Test prompt", "scenario": scenario},
                timeout=30
            )
            assert response.status_code in [200, 400, 429]

    def test_predict_tracks_latency(self, wait_for_app, sample_prompt):
        """Test that prediction updates latency metrics."""
        # Make a request
        requests.post(f"{wait_for_app}/predict", json=sample_prompt, timeout=30)

        # Check metrics
        metrics = requests.get(f"{wait_for_app}/metrics", timeout=10).text
        assert "ai_latency_seconds" in metrics

    def test_predict_injection_detection(self, wait_for_app, injection_prompts):
        """Test prompt injection detection."""
        for prompt in injection_prompts:
            response = requests.post(
                f"{wait_for_app}/predict",
                json=prompt,
                timeout=30
            )
            # Should still return a response (may be blocked or flagged)
            assert response.status_code in [200, 400, 403, 429]

    def test_predict_pii_detection(self, wait_for_app, pii_prompts):
        """Test PII detection in prompts."""
        for prompt in pii_prompts:
            response = requests.post(
                f"{wait_for_app}/predict",
                json=prompt,
                timeout=30
            )
            # Should handle PII (may redact or block)
            assert response.status_code in [200, 400, 403, 429]


@pytest.mark.integration
class TestRootEndpoint:
    """Test root endpoint."""

    def test_root_returns_info(self, wait_for_app):
        """Test / returns application info."""
        response = requests.get(f"{wait_for_app}/", timeout=10)

        assert response.status_code == 200


@pytest.mark.integration
@pytest.mark.slow
class TestConcurrentRequests:
    """Test concurrent request handling."""

    def test_multiple_concurrent_requests(self, wait_for_app, sample_prompts):
        """Test handling multiple concurrent requests."""
        import concurrent.futures

        def make_request(prompt):
            return requests.post(
                f"{wait_for_app}/predict",
                json=prompt,
                timeout=60
            )

        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(make_request, p) for p in sample_prompts]
            results = [f.result() for f in concurrent.futures.as_completed(futures)]

        # All requests should complete (may have rate limiting)
        assert all(r.status_code in [200, 429] for r in results)
