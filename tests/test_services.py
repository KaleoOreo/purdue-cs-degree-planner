import sqlite3

import pytest

from degree_planner.database import initialize_database, mark_completed, save_course
from degree_planner.models import Course
from degree_planner.requirements import CourseChoiceGroup, Curriculum, RequiredCourseGroup
from degree_planner.services import (
    find_curriculum_progress_from_database,
    find_missing_required_courses_from_database,
    find_remaining_choice_count_from_database,
    find_remaining_choice_options_from_database,
    plan_multiple_semesters_from_database,
    plan_next_semester_from_database,
)


def test_curriculum_progress_uses_saved_completions():
    connection = sqlite3.connect(":memory:")
    try:
        initialize_database(connection)
        core = RequiredCourseGroup("Core", {"A", "B"})
        systems = CourseChoiceGroup("Systems", {"C", "D"}, 1)
        curriculum = Curriculum("Example", [core], [systems])
        for code in {"A", "B", "C"}:
            mark_completed(connection, code)
        progress = find_curriculum_progress_from_database(connection, curriculum)
        assert progress.completed == {"A", "B", "C"}
        assert progress.is_complete is True
    finally:
        connection.close()


@pytest.mark.parametrize(
    "completed, expected_count, expected_options",
    [
        pytest.param(set(), 1, {"CS 35200", "CS 35400"}, id="none-completed"),
        pytest.param({"OTHER 10000"}, 1, {"CS 35200", "CS 35400"}, id="unrelated-completion"),
        pytest.param({"CS 35200"}, 0, {"CS 35400"}, id="qualifying-completion"),
    ],
)
def test_choice_progress_uses_saved_completions(completed, expected_count, expected_options):
    connection = sqlite3.connect(":memory:")
    try:
        initialize_database(connection)
        group = CourseChoiceGroup("Systems choice", {"CS 35200", "CS 35400"}, 1)
        for code in completed:
            mark_completed(connection, code)
        assert find_remaining_choice_count_from_database(connection, group) == expected_count
        assert find_remaining_choice_options_from_database(connection, group) == expected_options
    finally:
        connection.close()


def test_missing_required_courses_uses_saved_completions():
    connection = sqlite3.connect(":memory:")
    try:
        initialize_database(connection)
        group = RequiredCourseGroup("Example core", {"CS 18000", "CS 18200"})
        mark_completed(connection, "CS 18000")
        mark_completed(connection, "OTHER 10000")
        missing = find_missing_required_courses_from_database(connection, group)
        assert missing == {"CS 18200"}
    finally:
        connection.close()


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
