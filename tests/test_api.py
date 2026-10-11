from fastapi.testclient import TestClient

from degree_planner.api import app


client = TestClient(app)


def test_api_has_project_title():
    assert app.title == "Purdue CS Degree Planner API"


def test_health_endpoint():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
