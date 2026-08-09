import sqlite3

from degree_planner.database import load_completed_courses, load_courses
from degree_planner.models import Course
from degree_planner.planning import plan_next_semester


def plan_next_semester_from_database(
    connection: sqlite3.Connection,
    max_credits: int,
) -> list[Course]:
    courses = load_courses(connection)
    completed = load_completed_courses(connection)
    return plan_next_semester(courses, completed, max_credits)
