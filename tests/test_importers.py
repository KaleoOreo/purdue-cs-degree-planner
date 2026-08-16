import sqlite3

from degree_planner.database import initialize_database, load_courses
from degree_planner.importers import (
    course_from_row,
    import_courses_from_csv,
    load_courses_from_csv,
    parse_prerequisites,
)


def test_parse_prerequisites_splits_semicolon_values():
    assert parse_prerequisites("CS 18000;CS 18200") == ["CS 18000", "CS 18200"]


def test_parse_prerequisites_returns_empty_list_for_empty_value():
    assert parse_prerequisites("") == []


def test_parse_prerequisites_returns_empty_list_for_spaces():
    assert parse_prerequisites("   ") == []


def test_course_from_row_converts_csv_row_to_course():
    row = {
        "code": "CS 24000",
        "title": "Programming in C",
        "credits": "3",
        "category": "core",
        "prerequisites": "CS 18000;CS 18200",
    }

    course = course_from_row(row)

    assert course.code == "CS 24000"
    assert course.credits == 3
    assert course.prerequisites == ["CS 18000", "CS 18200"]


def test_load_courses_from_csv_returns_courses():
    courses = load_courses_from_csv("tests/fixtures/courses.csv")

    assert [course.code for course in courses] == ["CS 18000", "CS 18200"]
    assert courses[1].prerequisites == ["CS 18000"]


def test_import_courses_from_csv_saves_courses_to_database():
    connection = sqlite3.connect(":memory:")
    initialize_database(connection)

    import_courses_from_csv(connection, "tests/fixtures/courses.csv")
    courses = load_courses(connection)

    assert [course.code for course in courses] == ["CS 18000", "CS 18200"]
    assert courses[1].prerequisites == ["CS 18000"]
