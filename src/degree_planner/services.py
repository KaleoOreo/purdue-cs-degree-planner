import sqlite3

from degree_planner.database import load_completed_courses, load_courses, mark_completed
from degree_planner.exceptions import CourseNotFoundError
from degree_planner.models import Course
from degree_planner.planning import plan_multiple_semesters, plan_next_semester
from degree_planner.requirements import (
    CourseChoiceGroup,
    Curriculum,
    CurriculumProgress,
    RequiredCourseGroup,
)


def mark_course_completed_from_database(
    connection: sqlite3.Connection,
    course_code: str,
) -> None:
    course_codes = {course.code for course in load_courses(connection)}
    if course_code not in course_codes:
        raise CourseNotFoundError(f"Course not found: {course_code}")
    mark_completed(connection, course_code)


def find_curriculum_progress_from_database(
    connection: sqlite3.Connection,
    curriculum: Curriculum,
) -> CurriculumProgress:
    completed = load_completed_courses(connection)
    return CurriculumProgress(curriculum, completed)


def find_remaining_choice_count_from_database(
    connection: sqlite3.Connection,
    group: CourseChoiceGroup,
) -> int:
    completed = load_completed_courses(connection)
    return group.remaining_count(completed)


def find_remaining_choice_options_from_database(
    connection: sqlite3.Connection,
    group: CourseChoiceGroup,
) -> set[str]:
    completed = load_completed_courses(connection)
    return group.remaining_options(completed)


def find_missing_required_courses_from_database(
    connection: sqlite3.Connection,
    group: RequiredCourseGroup,
) -> set[str]:
    completed = load_completed_courses(connection)
    return group.missing_courses(completed)


def plan_next_semester_from_database(
    connection: sqlite3.Connection,
    max_credits: int,
) -> list[Course]:
    courses = load_courses(connection)
    completed = load_completed_courses(connection)
    return plan_next_semester(courses, completed, max_credits)


def plan_multiple_semesters_from_database(
    connection: sqlite3.Connection,
    max_credits: int,
) -> list[list[Course]]:
    courses = load_courses(connection)
    completed = load_completed_courses(connection)
    return plan_multiple_semesters(courses, completed, max_credits)
