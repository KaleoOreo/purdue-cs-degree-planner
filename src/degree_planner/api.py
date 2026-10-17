import sqlite3
from collections.abc import Iterator

from fastapi import Depends, FastAPI, HTTPException

from degree_planner.database import (
    connect_database,
    load_completed_courses,
    load_courses,
)
from degree_planner.exceptions import CourseNotFoundError
from degree_planner.models import Course
from degree_planner.schemas import CourseCompletionRequest, CourseResponse
from degree_planner.services import (
    mark_course_completed_from_database,
    plan_next_semester_from_database,
)


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


@app.get("/completed", response_model=list[str])
def get_completed_courses(
    connection: sqlite3.Connection = Depends(get_database),
) -> list[str]:
    return sorted(load_completed_courses(connection))


@app.post("/completed", status_code=204)
def complete_course(
    request: CourseCompletionRequest,
    connection: sqlite3.Connection = Depends(get_database),
) -> None:
    try:
        mark_course_completed_from_database(connection, request.course_code)
    except CourseNotFoundError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error


@app.get("/plan", response_model=list[CourseResponse])
def get_next_semester_plan(
    max_credits: int = 15,
    connection: sqlite3.Connection = Depends(get_database),
) -> list[Course]:
    return plan_next_semester_from_database(connection, max_credits)


@app.get("/health")
def get_health() -> dict[str, str]:
    return {"status": "ok"}
