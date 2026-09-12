from degree_planner.models import Course
from degree_planner.validation import find_missing_prerequisites


def test_find_missing_prerequisites_returns_unknown_prerequisite_codes():
    courses = [
        Course("CS 18200", "Foundations", 3, "core", ["CS 18000"]),
    ]

    assert find_missing_prerequisites(courses) == [("CS 18200", "CS 18000")]


def test_find_missing_prerequisites_returns_empty_list_when_all_exist():
    courses = [
        Course("CS 18000", "Problem Solving", 4, "core"),
        Course("CS 18200", "Foundations", 3, "core", ["CS 18000"]),
    ]

    assert find_missing_prerequisites(courses) == []


def test_find_missing_prerequisites_does_not_repeat_same_pair():
    courses = [
        Course("CS 24000", "Programming in C", 3, "core", ["CS 99999", "CS 99999"]),
    ]

    assert find_missing_prerequisites(courses) == [("CS 24000", "CS 99999")]


def test_find_missing_prerequisites_keeps_same_missing_code_for_different_courses():
    courses = [
        Course("CS 18200", "Foundations", 3, "core", ["CS 99999"]),
        Course("CS 24000", "Programming in C", 3, "core", ["CS 99999"]),
    ]

    assert find_missing_prerequisites(courses) == [
        ("CS 18200", "CS 99999"),
        ("CS 24000", "CS 99999"),
    ]
