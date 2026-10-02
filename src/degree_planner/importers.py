import csv
import json
import sqlite3

from degree_planner.database import save_course
from degree_planner.exceptions import DuplicateCourseError, RequirementsLoadError
from degree_planner.models import Course
from degree_planner.requirements import (
    CourseChoiceGroup,
    CourseOption,
    CourseOptionGroup,
    Curriculum,
    RequiredCourseGroup,
)


def _load_json_object(path: str) -> dict:
    try:
        with open(path, encoding="utf-8") as file:
            data = json.load(file)
    except json.JSONDecodeError as error:
        raise RequirementsLoadError(
            f"Invalid requirements JSON at line {error.lineno}: {error.msg}"
        ) from error
    if not isinstance(data, dict):
        raise RequirementsLoadError("Requirements JSON must contain an object")
    return data


def _load_requirement_data(path: str) -> dict:
    data = _load_json_object(path)
    _validate_requirement_data(data)
    return data


def _validate_requirement_data(data: object) -> None:
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


def _validate_curriculum_data(data: dict) -> None:
    for field in ("name", "required_groups", "choice_groups", "option_groups"):
        if field not in data:
            raise RequirementsLoadError(f"Missing required field: {field}")
    if not isinstance(data["name"], str):
        raise RequirementsLoadError("Field 'name' must be a string")
    for field in ("required_groups", "choice_groups", "option_groups"):
        if not isinstance(data[field], list):
            raise RequirementsLoadError(f"Field '{field}' must be a list")


def load_required_course_group(path: str) -> RequiredCourseGroup:
    data = _load_requirement_data(path)
    return _required_course_group_from_data(data)


def _required_course_group_from_data(data: dict) -> RequiredCourseGroup:
    return RequiredCourseGroup(
        name=data["name"],
        course_codes=set(data["course_codes"]),
    )


def load_course_choice_group(path: str) -> CourseChoiceGroup:
    data = _load_requirement_data(path)
    return _course_choice_group_from_data(data)


def _course_choice_group_from_data(data: dict) -> CourseChoiceGroup:
    if "required_count" not in data:
        raise RequirementsLoadError("Missing required field: required_count")
    if not isinstance(data["required_count"], int):
        raise RequirementsLoadError("Field 'required_count' must be an integer")
    try:
        return CourseChoiceGroup(
            data["name"], set(data["course_codes"]), data["required_count"]
        )
    except ValueError as error:
        raise RequirementsLoadError(str(error)) from error


def _course_option_from_data(data: object) -> CourseOption:
    if not isinstance(data, list):
        raise RequirementsLoadError("Each course option must be a list")
    if not all(isinstance(code, str) for code in data):
        raise RequirementsLoadError("Every option course code must be a string")
    if len(set(data)) != len(data):
        raise RequirementsLoadError("Course option cannot contain duplicate course codes")
    try:
        return CourseOption(frozenset(data))
    except ValueError as error:
        raise RequirementsLoadError(str(error)) from error


def _course_option_group_from_data(data: object) -> CourseOptionGroup:
    if not isinstance(data, dict):
        raise RequirementsLoadError("Each option group must be an object")
    for field in ("name", "options", "required_count"):
        if field not in data:
            raise RequirementsLoadError(f"Missing required field: {field}")
    if not isinstance(data["name"], str):
        raise RequirementsLoadError("Field 'name' must be a string")
    if not isinstance(data["options"], list):
        raise RequirementsLoadError("Field 'options' must be a list")
    if not isinstance(data["required_count"], int):
        raise RequirementsLoadError("Field 'required_count' must be an integer")
    options = [_course_option_from_data(option) for option in data["options"]]
    try:
        return CourseOptionGroup(data["name"], options, data["required_count"])
    except ValueError as error:
        raise RequirementsLoadError(str(error)) from error


def load_curriculum(path: str) -> Curriculum:
    data = _load_json_object(path)
    _validate_curriculum_data(data)
    required_groups = []
    for group_data in data["required_groups"]:
        _validate_requirement_data(group_data)
        required_groups.append(_required_course_group_from_data(group_data))
    choice_groups = []
    for group_data in data["choice_groups"]:
        _validate_requirement_data(group_data)
        choice_groups.append(_course_choice_group_from_data(group_data))
    option_groups = [
        _course_option_group_from_data(group_data)
        for group_data in data["option_groups"]
    ]
    return Curriculum(data["name"], required_groups, choice_groups, option_groups)


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
