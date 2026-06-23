"""
Integration tests for the web API.

These assert the *current* contract of the FastAPI app built by
``nmap_ai.web.main.create_app`` — a development server that exposes a
landing page, a health check, and a status endpoint. Scan/results
endpoints are on the roadmap (Phase 1) and intentionally not yet present.
"""
import pytest

fastapi_testclient = pytest.importorskip("fastapi.testclient")
from fastapi.testclient import TestClient  # noqa: E402

from nmap_ai.web.main import app  # noqa: E402

client = TestClient(app)


class TestAPIEndpoints:
    """Test suite for the API endpoints that exist today."""

    def test_root_page(self):
        """Root returns the landing page."""
        response = client.get("/")
        assert response.status_code == 200
        assert "NMAP-AI" in response.text

    def test_health_check(self):
        """Health endpoint reports a healthy service."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "nmap-ai-web"

    def test_status_endpoint(self):
        """Status endpoint advertises planned features."""
        response = client.get("/api/v1/status")
        assert response.status_code == 200
        data = response.json()
        assert data["service"] == "NMAP-AI API"
        assert "features" in data
        assert "scanning" in data["features"]

    def test_unknown_endpoint_404(self):
        """Endpoints that are not implemented yet return 404, not 501 stubs."""
        # The scan API is on the roadmap; until then it must not exist.
        response = client.post("/api/v1/scan", json={"targets": ["127.0.0.1"]})
        assert response.status_code == 404


def test_app_is_constructed():
    """The module-level app must be importable for ASGI servers/tests."""
    assert app is not None
