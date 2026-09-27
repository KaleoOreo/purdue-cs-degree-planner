import sqlite3

from degree_planner.database import initialize_database, mark_completed, save_course
from degree_planner.models import Course
from degree_planner.services import (
    plan_multiple_semesters_from_database,
    plan_next_semester_from_database,
)


def test_plan_next_semester_from_database_uses_saved_data():
    connection = sqlite3.connect(":memory:")
    initialize_database(connection)

    save_course(connection, Course("CS 18000", "Problem Solving", 4, "core"))
    save_course(connection, Course("CS 18200", "Foundations", 3, "core", ["CS 18000"]))
    mark_completed(connection, "CS 18000")

    plan = plan_next_semester_from_database(connection, max_credits=3)

    assert [course.code for course in plan] == ["CS 18200"]


def test_plan_multiple_semesters_from_database_uses_saved_data():
    connection = sqlite3.connect(":memory:")
    try:
        initialize_database(connection)
        prerequisite = Course("B", "Course B", 3, "core")
        dependent = Course("A", "Course A", 3, "core", ["B"])
        save_course(connection, prerequisite)
        save_course(connection, dependent)
        mark_completed(connection, "B")
        semesters = plan_multiple_semesters_from_database(connection, max_credits=6)
        assert semesters == [[dependent]]
    finally:
        connection.close()
