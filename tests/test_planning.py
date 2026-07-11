from degree_planner.models import Course
from degree_planner.planning import find_available_courses


def test_find_available_courses_excludes_locked_courses():
    courses = [
        Course("CS 18000", "Problem Solving", 4, "core"),
        Course("CS 18200", "Foundations", 3, "core", ["CS 18000"]),
    ]

    available = find_available_courses(courses, set())

    assert [course.code for course in available] == ["CS 18000"]


def test_find_available_courses_excludes_completed_courses():
    courses = [
        Course("CS 18000", "Problem Solving", 4, "core"),
        Course("CS 18200", "Foundations", 3, "core", ["CS 18000"]),
    ]

    available = find_available_courses(courses, {"CS 18000"})

    assert [course.code for course in available] == ["CS 18200"]
