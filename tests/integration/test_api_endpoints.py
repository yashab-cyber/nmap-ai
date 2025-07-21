"""
Basic integration test for API endpoints.
Tests the interaction between FastAPI routes and core functionality.
"""
import pytest
import requests
from fastapi.testclient import TestClient
from nmap_ai.web.main import app

client = TestClient(app)


class TestAPIEndpoints:
    """Test suite for API endpoint integration."""
    
    def test_health_check(self):
        """Test the health check endpoint."""
        response = client.get("/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
    
    def test_scan_endpoint_integration(self):
        """Test scan endpoint with core scanner integration."""
        scan_request = {
            "targets": ["127.0.0.1"],
            "scan_type": "basic",
            "ports": "22,80,443"
        }
        response = client.post("/api/scan", json=scan_request)
        assert response.status_code in [200, 202]  # Accepted for async processing
    
    def test_config_endpoint_integration(self):
        """Test configuration endpoint integration."""
        response = client.get("/api/config")
        assert response.status_code == 200
        config_data = response.json()
        assert "scanning" in config_data
        assert "ai" in config_data
    
    def test_vulnerability_analysis_integration(self):
        """Test vulnerability analysis endpoint integration."""
        # This would typically use a sample scan result
        scan_id = "test_scan_123"
        response = client.get(f"/api/vulnerability/{scan_id}")
        # Endpoint might return 404 for non-existent scan, which is expected
        assert response.status_code in [200, 404]
    
    def test_export_integration(self):
        """Test export functionality integration."""
        export_request = {
            "scan_id": "test_scan_123",
            "format": "json"
        }
        response = client.post("/api/export", json=export_request)
        # Should handle non-existent scan gracefully
        assert response.status_code in [200, 404]


@pytest.fixture
def mock_scan_data():
    """Fixture providing mock scan data for testing."""
    return {
        "scan_id": "test_scan_123",
        "targets": ["192.168.1.1"],
        "status": "completed",
        "results": {
            "open_ports": [22, 80, 443],
            "services": ["ssh", "http", "https"]
        }
    }


def test_end_to_end_scan_flow(mock_scan_data):
    """Test complete scan workflow from request to results."""
    # This would be a more comprehensive test
    # involving actual scan execution (in a controlled environment)
    pass
