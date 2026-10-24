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
from degree_planner.requirements import (
    CourseChoiceGroup,
    CourseOption,
    CourseOptionGroup,
    Curriculum,
    CurriculumProgress,
    RequirementAllocation,
    RequiredCourseGroup,
)


client = TestClient(api_module.app)


def test_api_has_project_title():
    assert api_module.app.title == "Purdue CS Degree Planner API"


def test_required_group_progress_response_includes_definition_and_progress():
    group = RequiredCourseGroup(
        "Computer Science Core",
        {"CS 18200", "CS 18000"},
    )

    response = api_module._required_group_progress_response(
        group,
        {"CS 18000"},
    )

    assert response.course_codes == ["CS 18000", "CS 18200"]
    assert response.missing_course_codes == ["CS 18200"]


def test_choice_group_progress_response_includes_definition_and_progress():
    group = CourseChoiceGroup(
        "Software Engineering Electives",
        {"CS 35200", "CS 34800", "CS 30700"},
        2,
    )

    response = api_module._choice_group_progress_response(group, {"CS 30700"})

    assert response.required_count == 2
    assert response.remaining_count == 1
    assert response.remaining_course_codes == ["CS 34800", "CS 35200"]


def test_course_option_response_preserves_paired_course_boundary():
    option = CourseOption(frozenset({"CS 41100", "CS 31100"}))

    response = api_module._course_option_response(option)

    assert response.course_codes == ["CS 31100", "CS 41100"]


def test_option_group_progress_response_preserves_nested_options():
    group = CourseOptionGroup(
        "Systems Sequences",
        [
            CourseOption(frozenset({"CS 41100", "CS 31100"})),
            CourseOption(frozenset({"CS 35200"})),
        ],
        1,
    )

    response = api_module._option_group_progress_response(group, {"CS 35200"})

    assert response.remaining_count == 0
    assert [option.course_codes for option in response.options] == [
        ["CS 31100", "CS 41100"],
        ["CS 35200"],
    ]
    assert response.remaining_options[0].course_codes == ["CS 31100", "CS 41100"]


def test_requirement_allocation_response_identifies_group_and_option():
    allocation = RequirementAllocation(
        "Systems Sequences",
        CourseOption(frozenset({"CS 41100", "CS 31100"})),
    )

    response = api_module._requirement_allocation_response(allocation)

    assert response.group_name == "Systems Sequences"
    assert response.course_codes == ["CS 31100", "CS 41100"]


@pytest.mark.parametrize(
    ("completed", "expected"),
    [
        pytest.param({"A"}, None, id="no-complete-allocation"),
        pytest.param(
            {"A", "B"},
            [("Core", ["A"]), ("Elective", ["B"])],
            id="complete-allocation",
        ),
    ],
)
def test_requirement_allocation_responses_reports_global_result(completed, expected):
    curriculum = Curriculum(
        "Example",
        [RequiredCourseGroup("Core", {"A"})],
        [CourseChoiceGroup("Elective", {"A", "B"}, 1)],
        [],
    )

    responses = api_module._requirement_allocation_responses(curriculum, completed)

    if responses is None:
        assert expected is None
    else:
        assert [(item.group_name, item.course_codes) for item in responses] == expected


def test_curriculum_progress_response_combines_all_group_types():
    curriculum = Curriculum(
        "Example Curriculum",
        [RequiredCourseGroup("Core", {"A"})],
        [CourseChoiceGroup("Elective", {"B", "C"}, 1)],
        [CourseOptionGroup(
            "Sequence",
            [
                CourseOption(frozenset({"D", "E"})),
                CourseOption(frozenset({"F"})),
            ],
            1,
        )],
    )
    progress = CurriculumProgress(curriculum, {"E", "D", "B", "A"})

    response = api_module._curriculum_progress_response(progress)

    assert response.is_complete is True
    assert response.completed_course_codes == ["A", "B", "D", "E"]
    assert [group.name for group in response.required_groups] == ["Core"]
    assert [group.name for group in response.choice_groups] == ["Elective"]
    assert [group.name for group in response.option_groups] == ["Sequence"]
    assert response.allocations is not None
    assert [item.group_name for item in response.allocations] == [
        "Core", "Elective", "Sequence"
    ]


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


def test_validation_endpoint_reports_missing_prerequisite(tmp_path, monkeypatch):
    database_path = str(tmp_path / "planner.db")
    connection = connect_database(database_path)
    try:
        save_course(
            connection,
            Course("CS 18200", "Foundations", 3, "core", ["CS 18000"]),
        )
    finally:
        connection.close()
    monkeypatch.setattr(api_module, "DATABASE_PATH", database_path)

    response = client.get("/validation")

    assert response.status_code == 200
    assert response.json() == {
        "is_valid": False,
        "missing_prerequisites": [
            {
                "course_code": "CS 18200",
                "prerequisite_code": "CS 18000",
            }
        ],
        "cycle_path": [],
    }


def test_validation_endpoint_reports_valid_graph(tmp_path, monkeypatch):
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

    response = client.get("/validation")

    assert response.status_code == 200
    assert response.json() == {
        "is_valid": True,
        "missing_prerequisites": [],
        "cycle_path": [],
    }


def test_validation_endpoint_reports_cycle_path(tmp_path, monkeypatch):
    database_path = str(tmp_path / "planner.db")
    connection = connect_database(database_path)
    try:
        save_course(
            connection,
            Course("CS 20000", "Course A", 3, "core", ["CS 25000"]),
        )
        save_course(
            connection,
            Course("CS 25000", "Course B", 3, "core", ["CS 20000"]),
        )
    finally:
        connection.close()
    monkeypatch.setattr(api_module, "DATABASE_PATH", database_path)

    response = client.get("/validation")

    assert response.status_code == 200
    assert response.json() == {
        "is_valid": False,
        "missing_prerequisites": [],
        "cycle_path": ["CS 20000", "CS 25000", "CS 20000"],
    }


def test_progress_endpoint_combines_curriculum_and_completed_courses(
    tmp_path,
    monkeypatch,
):
    curriculum_path = tmp_path / "curriculum.json"
    curriculum_path.write_text(
        '{"name": "Example", "required_groups": '
        '[{"name": "Core", "course_codes": ["A"]}], '
        '"choice_groups": [], "option_groups": []}',
        encoding="utf-8",
    )
    database_path = str(tmp_path / "planner.db")
    connection = connect_database(database_path)
    try:
        mark_completed(connection, "A")
    finally:
        connection.close()
    monkeypatch.setattr(api_module, "DATABASE_PATH", database_path)
    monkeypatch.setattr(api_module, "CURRICULUM_PATH", str(curriculum_path))

    response = client.get("/progress")

    assert response.status_code == 200
    assert response.json()["is_complete"] is True
    assert response.json()["completed_course_codes"] == ["A"]
    assert response.json()["allocations"] == [
        {"group_name": "Core", "course_codes": ["A"]}
    ]


@pytest.mark.parametrize(
    ("contents", "expected_status", "expected_detail"),
    [
        pytest.param(None, 404, "Curriculum file not found", id="missing-file"),
        pytest.param(
            "{}",
            422,
            "Missing required field: name",
            id="invalid-curriculum",
        ),
    ],
)
def test_progress_endpoint_reports_curriculum_load_error(
    contents,
    expected_status,
    expected_detail,
    tmp_path,
    monkeypatch,
):
    curriculum_path = tmp_path / "curriculum.json"
    if contents is not None:
        curriculum_path.write_text(contents, encoding="utf-8")
    monkeypatch.setattr(api_module, "DATABASE_PATH", str(tmp_path / "planner.db"))
    monkeypatch.setattr(api_module, "CURRICULUM_PATH", str(curriculum_path))

    response = client.get("/progress")

    assert response.status_code == expected_status
    assert response.json() == {"detail": expected_detail}
