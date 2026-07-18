import sqlite3

from degree_planner.database import initialize_database


def test_initialize_database_creates_courses_table():
    connection = sqlite3.connect(":memory:")

    initialize_database(connection)
    table = connection.execute(
        "SELECT name FROM sqlite_master WHERE type = 'table' AND name = 'courses'"
    ).fetchone()

    assert table == ("courses",)
