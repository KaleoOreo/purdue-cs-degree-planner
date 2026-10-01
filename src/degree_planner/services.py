import sqlite3

from degree_planner.database import load_completed_courses, load_courses
from degree_planner.models import Course
from degree_planner.planning import plan_multiple_semesters, plan_next_semester
from degree_planner.requirements import CourseChoiceGroup, RequiredCourseGroup


def find_remaining_choice_count_from_database(
    connection: sqlite3.Connection,
    group: CourseChoiceGroup,
) -> int:
    completed = load_completed_courses(connection)
    return group.remaining_count(completed)


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
