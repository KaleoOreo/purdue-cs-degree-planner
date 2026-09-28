import csv
import json
import sqlite3

from degree_planner.database import save_course
from degree_planner.exceptions import DuplicateCourseError
from degree_planner.models import Course
from degree_planner.requirements import RequiredCourseGroup


def load_required_course_group(path: str) -> RequiredCourseGroup:
    with open(path, encoding="utf-8") as file:
        data = json.load(file)
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
