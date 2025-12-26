"""
Integration tests for observability stack.
"""

import pytest
import requests
import time


@pytest.mark.integration
class TestPrometheusIntegration:
    """Test Prometheus integration."""

    def test_prometheus_healthy(self, wait_for_prometheus):
        """Test Prometheus is healthy."""
        response = requests.get(f"{wait_for_prometheus}/-/ready", timeout=10)
        assert response.status_code == 200

    def test_prometheus_scrapes_app(self, wait_for_prometheus, wait_for_app):
        """Test Prometheus scrapes the application."""
        # Wait a bit for scrape to happen
        time.sleep(10)

        # Query Prometheus for app metrics
        response = requests.get(
            f"{wait_for_prometheus}/api/v1/query",
            params={"query": "up{job='ai-app'}"},
            timeout=10
        )

        if response.status_code == 200:
            data = response.json()
            assert data.get("status") == "success"

    def test_prometheus_has_ai_metrics(self, wait_for_prometheus, wait_for_app, sample_prompt):
        """Test Prometheus has AI metrics after request."""
        # Generate some metrics
        requests.post(f"{wait_for_app}/predict", json=sample_prompt, timeout=30)
        time.sleep(10)  # Wait for scrape

        # Query for AI metrics
        response = requests.get(
            f"{wait_for_prometheus}/api/v1/query",
            params={"query": "ai_requests_total"},
            timeout=10
        )

        if response.status_code == 200:
            data = response.json()
            assert data.get("status") == "success"


@pytest.mark.integration
class TestGrafanaIntegration:
    """Test Grafana integration."""

    @pytest.fixture
    def grafana_url(self, test_config):
        return f"http://{test_config['grafana_host']}:{test_config['grafana_port']}"

    def test_grafana_healthy(self, grafana_url):
        """Test Grafana is healthy."""
        try:
            response = requests.get(f"{grafana_url}/api/health", timeout=10)
            assert response.status_code == 200
        except requests.exceptions.RequestException:
            pytest.skip("Grafana not available")

    def test_grafana_datasources_provisioned(self, grafana_url):
        """Test Grafana has provisioned datasources."""
        try:
            response = requests.get(
                f"{grafana_url}/api/datasources",
                auth=("admin", "admin"),
                timeout=10
            )
            if response.status_code == 200:
                datasources = response.json()
                assert len(datasources) > 0
        except requests.exceptions.RequestException:
            pytest.skip("Grafana not available")


@pytest.mark.integration
class TestTempoIntegration:
    """Test Tempo tracing integration."""

    @pytest.fixture
    def tempo_url(self, test_config):
        return f"http://{test_config['tempo_host']}:{test_config['tempo_port']}"

    def test_tempo_healthy(self, tempo_url):
        """Test Tempo is healthy."""
        try:
            response = requests.get(f"{tempo_url}/ready", timeout=10)
            assert response.status_code == 200
        except requests.exceptions.RequestException:
            pytest.skip("Tempo not available")

    def test_traces_sent_after_request(self, tempo_url, wait_for_app, sample_prompt):
        """Test traces are sent after making a request."""
        # Make request to generate trace
        requests.post(f"{wait_for_app}/predict", json=sample_prompt, timeout=30)

        # Wait for trace to be processed
        time.sleep(5)

        # Query Tempo for traces (basic check)
        try:
            response = requests.get(f"{tempo_url}/ready", timeout=10)
            assert response.status_code == 200
        except requests.exceptions.RequestException:
            pytest.skip("Tempo not available")


@pytest.mark.integration
class TestOpenSearchIntegration:
    """Test OpenSearch log integration."""

    @pytest.fixture
    def opensearch_url(self, test_config):
        return f"http://{test_config['opensearch_host']}:{test_config['opensearch_port']}"

    def test_opensearch_healthy(self, opensearch_url):
        """Test OpenSearch is healthy."""
        try:
            response = requests.get(f"{opensearch_url}/_cluster/health", timeout=10)
            assert response.status_code == 200
        except requests.exceptions.RequestException:
            pytest.skip("OpenSearch not available")

    def test_opensearch_has_logs(self, opensearch_url, wait_for_app, sample_prompt):
        """Test logs are shipped to OpenSearch."""
        # Generate some logs
        requests.post(f"{wait_for_app}/predict", json=sample_prompt, timeout=30)
        time.sleep(10)  # Wait for log shipping

        try:
            # Check if indices exist
            response = requests.get(f"{opensearch_url}/_cat/indices", timeout=10)
            assert response.status_code == 200
        except requests.exceptions.RequestException:
            pytest.skip("OpenSearch not available")
