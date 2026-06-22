"""
Integration tests for the API router's ``/config`` endpoints.

These guard against a regression where the handlers read/wrote flat
attributes (e.g. ``config.scanning_timeout``) instead of the nested
``NmapAIConfig`` layout (``config.scanning.default_timeout``), which raised
``AttributeError`` on every request.
"""
import pytest

pytest.importorskip("fastapi.testclient")
from fastapi import FastAPI  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

from nmap_ai.web.api.endpoints import router  # noqa: E402


@pytest.fixture
def client():
    app = FastAPI()
    app.include_router(router)
    return TestClient(app)


def test_get_config_returns_nested_structure(client):
    """GET /config maps the nested NmapAIConfig without AttributeError."""
    response = client.get("/config")
    assert response.status_code == 200
    data = response.json()

    assert set(data) == {"scanning", "ai", "output"}
    assert "default_timeout" in data["scanning"]
    assert "max_threads" in data["scanning"]
    assert "default_ports" in data["scanning"]
    assert "enable_smart_scanning" in data["ai"]
    assert "enable_vulnerability_detection" in data["ai"]
    assert "confidence_threshold" in data["ai"]
    assert "default_format" in data["output"]
    assert "results_directory" in data["output"]


def test_put_config_updates_nested_fields(client):
    """PUT /config accepts updates and persists them to the nested config."""
    payload = {
        "scanning": {"default_timeout": 120, "max_threads": 8},
        "ai": {"enable_smart_scanning": False, "confidence_threshold": 0.5},
    }
    response = client.put("/config", json=payload)
    assert response.status_code == 200

    # The change is reflected on the subsequent GET (shared global config).
    data = client.get("/config").json()
    assert data["scanning"]["default_timeout"] == 120
    assert data["scanning"]["max_threads"] == 8
    assert data["ai"]["enable_smart_scanning"] is False
    assert data["ai"]["confidence_threshold"] == 0.5
