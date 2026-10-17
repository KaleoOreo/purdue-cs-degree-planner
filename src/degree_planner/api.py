import sqlite3
from collections.abc import Iterator

from fastapi import Depends, FastAPI

from degree_planner.database import connect_database, load_courses
from degree_planner.models import Course
from degree_planner.schemas import CourseResponse


DATABASE_PATH = "data/planner.db"


app = FastAPI(title="Purdue CS Degree Planner API")


def get_database() -> Iterator[sqlite3.Connection]:
    connection = connect_database(DATABASE_PATH)
    try:
        yield connection
    finally:
        connection.close()


@app.get("/courses", response_model=list[CourseResponse])
def get_courses(
    connection: sqlite3.Connection = Depends(get_database),
) -> list[Course]:
    return load_courses(connection)


@app.get("/health")
def get_health() -> dict[str, str]:
    return {"status": "ok"}
