import sqlite3

from degree_planner.database import (
    connect_database,
    initialize_database,
    load_completed_courses,
    load_courses,
    load_prerequisites,
    mark_completed,
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
    assert ("completed_courses",) in tables


def test_connect_database_initializes_database_file():
    database_path = "data/test_planner.db"

    connection = connect_database(str(database_path))
    tables = connection.execute(
        "SELECT name FROM sqlite_master WHERE type = 'table'"
    ).fetchall()

    assert ("courses",) in tables


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


def test_mark_completed_inserts_completed_course():
    connection = sqlite3.connect(":memory:")
    initialize_database(connection)

    mark_completed(connection, "CS 18000")
    row = connection.execute(
        "SELECT course_code FROM completed_courses"
    ).fetchone()

    assert row == ("CS 18000",)


def test_load_completed_courses_returns_completed_codes():
    connection = sqlite3.connect(":memory:")
    initialize_database(connection)

    mark_completed(connection, "CS 18000")
    mark_completed(connection, "CS 18200")

    assert load_completed_courses(connection) == {"CS 18000", "CS 18200"}


def test_mark_completed_ignores_duplicate_course_code():
    connection = sqlite3.connect(":memory:")
    initialize_database(connection)

    mark_completed(connection, "CS 18000")
    mark_completed(connection, "CS 18000")

    assert load_completed_courses(connection) == {"CS 18000"}
