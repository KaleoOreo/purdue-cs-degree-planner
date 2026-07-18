import sqlite3

from degree_planner.models import Course


CREATE_COURSES_TABLE = """
CREATE TABLE IF NOT EXISTS courses (
    code TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    credits INTEGER NOT NULL,
    category TEXT NOT NULL
);
"""


def initialize_database(connection: sqlite3.Connection) -> None:
    connection.execute(CREATE_COURSES_TABLE)
    connection.commit()


def save_course(connection: sqlite3.Connection, course: Course) -> None:
    connection.execute(
        "INSERT INTO courses (code, title, credits, category) VALUES (?, ?, ?, ?)",
        (course.code, course.title, course.credits, course.category),
    )
    connection.commit()
