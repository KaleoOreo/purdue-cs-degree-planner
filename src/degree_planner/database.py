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

CREATE_PREREQUISITES_TABLE = """
CREATE TABLE IF NOT EXISTS prerequisites (
    course_code TEXT NOT NULL,
    prerequisite_code TEXT NOT NULL
);
"""

CREATE_COMPLETED_COURSES_TABLE = """
CREATE TABLE IF NOT EXISTS completed_courses (
    course_code TEXT PRIMARY KEY
);
"""


def initialize_database(connection: sqlite3.Connection) -> None:
    connection.execute(CREATE_COURSES_TABLE)
    connection.execute(CREATE_PREREQUISITES_TABLE)
    connection.execute(CREATE_COMPLETED_COURSES_TABLE)
    connection.commit()


def connect_database(path: str) -> sqlite3.Connection:
    connection = sqlite3.connect(path)
    initialize_database(connection)
    return connection


def save_course(connection: sqlite3.Connection, course: Course) -> None:
    connection.execute(
        "INSERT INTO courses (code, title, credits, category) VALUES (?, ?, ?, ?)",
        (course.code, course.title, course.credits, course.category),
    )
    for prerequisite in course.prerequisites:
        connection.execute(
            "INSERT INTO prerequisites (course_code, prerequisite_code) VALUES (?, ?)",
            (course.code, prerequisite),
        )
    connection.commit()


def load_prerequisites(connection: sqlite3.Connection, course_code: str) -> list[str]:
    rows = connection.execute(
        "SELECT prerequisite_code FROM prerequisites WHERE course_code = ? ORDER BY prerequisite_code",
        (course_code,),
    ).fetchall()
    return [
        prerequisite_code
        for (prerequisite_code,) in rows
    ]


def load_courses(connection: sqlite3.Connection) -> list[Course]:
    rows = connection.execute(
        "SELECT code, title, credits, category FROM courses ORDER BY code"
    ).fetchall()
    return [
        Course(code, title, credits, category, load_prerequisites(connection, code))
        for code, title, credits, category in rows
    ]


def mark_completed(connection: sqlite3.Connection, course_code: str) -> None:
    connection.execute(
        "INSERT OR IGNORE INTO completed_courses (course_code) VALUES (?)",
        (course_code,),
    )
    connection.commit()


def load_completed_courses(connection: sqlite3.Connection) -> set[str]:
    rows = connection.execute(
        "SELECT course_code FROM completed_courses"
    ).fetchall()
    return {
        course_code
        for (course_code,) in rows
    }
