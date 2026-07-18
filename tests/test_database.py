import sqlite3

from degree_planner.database import initialize_database, save_course
from degree_planner.models import Course


def test_initialize_database_creates_courses_table():
    connection = sqlite3.connect(":memory:")

    initialize_database(connection)
    table = connection.execute(
        "SELECT name FROM sqlite_master WHERE type = 'table' AND name = 'courses'"
    ).fetchone()

    assert table == ("courses",)


def test_save_course_inserts_course_row():
    connection = sqlite3.connect(":memory:")
    initialize_database(connection)

    save_course(connection, Course("CS 18000", "Problem Solving", 4, "core"))
    row = connection.execute(
        "SELECT code, title, credits, category FROM courses"
    ).fetchone()

    assert row == ("CS 18000", "Problem Solving", 4, "core")
