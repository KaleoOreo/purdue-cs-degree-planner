from fastapi.testclient import TestClient

import degree_planner.api as api_module
from degree_planner.database import connect_database, save_course
from degree_planner.models import Course


client = TestClient(api_module.app)


def test_api_has_project_title():
    assert api_module.app.title == "Purdue CS Degree Planner API"


def test_health_endpoint():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_courses_endpoint_returns_stored_courses(tmp_path, monkeypatch):
    database_path = str(tmp_path / "planner.db")
    connection = connect_database(database_path)
    try:
        save_course(connection, Course("CS 18000", "Problem Solving", 4, "core"))
    finally:
        connection.close()
    monkeypatch.setattr(api_module, "DATABASE_PATH", database_path)

    response = client.get("/courses")

    assert response.status_code == 200
    assert response.json() == [
        {
            "code": "CS 18000",
            "title": "Problem Solving",
            "credits": 4,
            "category": "core",
            "prerequisites": [],
        }
    ]
