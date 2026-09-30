import csv
import json
import sqlite3

from degree_planner.database import save_course
from degree_planner.exceptions import DuplicateCourseError, RequirementsLoadError
from degree_planner.models import Course
from degree_planner.requirements import RequiredCourseGroup


def load_required_course_group(path: str) -> RequiredCourseGroup:
    try:
        with open(path, encoding="utf-8") as file:
            data = json.load(file)
    except json.JSONDecodeError as error:
        raise RequirementsLoadError(
            f"Invalid requirements JSON at line {error.lineno}: {error.msg}"
        ) from error
    if not isinstance(data, dict):
        raise RequirementsLoadError("Requirements JSON must contain an object")
    for field in ("name", "course_codes"):
        if field not in data:
            raise RequirementsLoadError(f"Missing required field: {field}")
    if not isinstance(data["name"], str):
        raise RequirementsLoadError("Field 'name' must be a string")
    if not isinstance(data["course_codes"], list):
        raise RequirementsLoadError("Field 'course_codes' must be a list")
    for code in data["course_codes"]:
        if not isinstance(code, str):
            raise RequirementsLoadError("Every course code must be a string")
    return RequiredCourseGroup(
        name=data["name"],
        course_codes=set(data["course_codes"]),
    )


def parse_prerequisites(value: str) -> list[str]:
    if not value.strip():
        return []

    return [
        prerequisite.strip()
        for prerequisite in value.split(";")
        if prerequisite.strip()
    ]


def course_from_row(row: dict[str, str]) -> Course:
    return Course(
        row["code"],
        row["title"],
        int(row["credits"]),
        row["category"],
        parse_prerequisites(row["prerequisites"]),
    )


def load_courses_from_csv(path: str) -> list[Course]:
    with open(path, newline="") as file:
        reader = csv.DictReader(file)
        return [
            course_from_row(row)
            for row in reader
        ]


def import_courses_from_csv(connection: sqlite3.Connection, path: str) -> int:
    courses = load_courses_from_csv(path)
    for course in courses:
        try:
            save_course(connection, course)
        except sqlite3.IntegrityError as error:
            raise DuplicateCourseError("duplicate course code during import") from error
    return len(courses)
