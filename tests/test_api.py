from fastapi.testclient import TestClient
import pytest

import degree_planner.api as api_module
from degree_planner.database import (
    connect_database,
    load_completed_courses,
    mark_completed,
    save_course,
)
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


def test_completed_endpoint_returns_completed_course_codes(tmp_path, monkeypatch):
    database_path = str(tmp_path / "planner.db")
    connection = connect_database(database_path)
    try:
        mark_completed(connection, "CS 18200")
        mark_completed(connection, "CS 18000")
    finally:
        connection.close()
    monkeypatch.setattr(api_module, "DATABASE_PATH", database_path)

    response = client.get("/completed")

    assert response.status_code == 200
    assert response.json() == ["CS 18000", "CS 18200"]


def test_complete_course_endpoint_stores_course_code(tmp_path, monkeypatch):
    database_path = str(tmp_path / "planner.db")
    connection = connect_database(database_path)
    try:
        save_course(connection, Course("CS 18000", "Problem Solving", 4, "core"))
    finally:
        connection.close()
    monkeypatch.setattr(api_module, "DATABASE_PATH", database_path)

    response = client.post("/completed", json={"course_code": "CS 18000"})

    assert response.status_code == 204
    connection = connect_database(database_path)
    try:
        assert load_completed_courses(connection) == {"CS 18000"}
    finally:
        connection.close()


def test_complete_course_endpoint_rejects_unknown_course(tmp_path, monkeypatch):
    database_path = str(tmp_path / "planner.db")
    monkeypatch.setattr(api_module, "DATABASE_PATH", database_path)

    response = client.post("/completed", json={"course_code": "CS 99999"})

    assert response.status_code == 404
    assert response.json() == {"detail": "Course not found: CS 99999"}
    connection = connect_database(database_path)
    try:
        assert load_completed_courses(connection) == set()
    finally:
        connection.close()


@pytest.mark.parametrize(
    "body",
    [
        pytest.param({}, id="missing-course-code"),
        pytest.param({"course_code": 18000}, id="non-string-course-code"),
    ],
)
def test_complete_course_endpoint_rejects_invalid_body(body, tmp_path, monkeypatch):
    database_path = str(tmp_path / "planner.db")
    monkeypatch.setattr(api_module, "DATABASE_PATH", database_path)

    response = client.post("/completed", json=body)

    assert response.status_code == 422
    connection = connect_database(database_path)
    try:
        assert load_completed_courses(connection) == set()
    finally:
        connection.close()


def test_plan_endpoint_uses_max_credits_query(tmp_path, monkeypatch):
    database_path = str(tmp_path / "planner.db")
    connection = connect_database(database_path)
    try:
        save_course(connection, Course("CS 18000", "Problem Solving", 4, "core"))
        save_course(connection, Course("CS 24000", "Programming in C", 3, "core"))
    finally:
        connection.close()
    monkeypatch.setattr(api_module, "DATABASE_PATH", database_path)

    response = client.get("/plan?max_credits=3")

    assert response.status_code == 200
    assert [course["code"] for course in response.json()] == ["CS 24000"]


@pytest.mark.parametrize("max_credits", ["abc", "0", "-1"])
def test_plan_endpoint_rejects_invalid_max_credits(
    max_credits,
    tmp_path,
    monkeypatch,
):
    database_path = str(tmp_path / "planner.db")
    monkeypatch.setattr(api_module, "DATABASE_PATH", database_path)

    response = client.get(f"/plan?max_credits={max_credits}")

    assert response.status_code == 422


def test_full_plan_endpoint_returns_multiple_semesters(tmp_path, monkeypatch):
    database_path = str(tmp_path / "planner.db")
    connection = connect_database(database_path)
    try:
        save_course(connection, Course("CS 18000", "Problem Solving", 4, "core"))
        save_course(
            connection,
            Course("CS 18200", "Foundations", 3, "core", ["CS 18000"]),
        )
    finally:
        connection.close()
    monkeypatch.setattr(api_module, "DATABASE_PATH", database_path)

    response = client.get("/plan/all?max_credits=7")

    assert response.status_code == 200
    assert [
        [course["code"] for course in semester]
        for semester in response.json()
    ] == [["CS 18000"], ["CS 18200"]]
