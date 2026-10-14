from fastapi.testclient import TestClient

from backend.app.main import app

client = TestClient(app)


def test_root_returns_project_name() -> None:
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["name"] == "Cafe Aramesh API"


def test_liveness_endpoint() -> None:
    response = client.get("/api/v1/health/live")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_readiness_endpoint_returns_success_or_service_unavailable() -> None:
    # PostgreSQL does not need to be running to execute the foundation tests.
    response = client.get("/api/v1/health/ready")
    assert response.status_code in (200, 503)
    if response.status_code == 503:
        assert response.json()["detail"] == "Database is unavailable"
