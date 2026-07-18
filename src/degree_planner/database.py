import sqlite3


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
