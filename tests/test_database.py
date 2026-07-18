import sqlite3

from degree_planner.database import (
    initialize_database,
    load_courses,
    load_prerequisites,
    save_course,
)
from degree_planner.models import Course


def test_initialize_database_creates_courses_table():
    connection = sqlite3.connect(":memory:")

    initialize_database(connection)
    tables = connection.execute(
        "SELECT name FROM sqlite_master WHERE type = 'table'"
    ).fetchall()

    assert ("courses",) in tables
    assert ("prerequisites",) in tables


def test_save_course_inserts_course_row():
    connection = sqlite3.connect(":memory:")
    initialize_database(connection)

    save_course(connection, Course("CS 18000", "Problem Solving", 4, "core"))
    row = connection.execute(
        "SELECT code, title, credits, category FROM courses"
    ).fetchone()

    assert row == ("CS 18000", "Problem Solving", 4, "core")


def test_save_course_inserts_prerequisite_rows():
    connection = sqlite3.connect(":memory:")
    initialize_database(connection)

    save_course(connection, Course("CS 24000", "Programming in C", 3, "core", ["CS 18000", "CS 18200"]))
    rows = connection.execute(
        "SELECT course_code, prerequisite_code FROM prerequisites ORDER BY prerequisite_code"
    ).fetchall()

    assert rows == [("CS 24000", "CS 18000"), ("CS 24000", "CS 18200")]


def test_load_prerequisites_returns_codes_for_course():
    connection = sqlite3.connect(":memory:")
    initialize_database(connection)

    save_course(connection, Course("CS 24000", "Programming in C", 3, "core", ["CS 18000", "CS 18200"]))

    assert load_prerequisites(connection, "CS 24000") == ["CS 18000", "CS 18200"]


def test_load_courses_returns_course_objects():
    connection = sqlite3.connect(":memory:")
    initialize_database(connection)

    save_course(connection, Course("CS 18200", "Foundations", 3, "core"))
    save_course(connection, Course("CS 18000", "Problem Solving", 4, "core"))

    courses = load_courses(connection)

    assert [course.code for course in courses] == ["CS 18000", "CS 18200"]


def test_load_courses_includes_prerequisites():
    connection = sqlite3.connect(":memory:")
    initialize_database(connection)

    save_course(connection, Course("CS 18200", "Foundations", 3, "core", ["CS 18000"]))

    courses = load_courses(connection)

    assert courses[0].prerequisites == ["CS 18000"]
