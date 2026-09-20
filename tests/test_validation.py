from degree_planner.models import Course
from degree_planner.validation import (
    ValidationResult,
    find_cycle_path,
    find_missing_prerequisites,
    find_two_course_cycles,
    has_cycle,
)


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


def test_has_cycle_returns_true_for_two_course_cycle():
    courses = [
        Course("CS 18000", "Problem Solving", 4, "core", ["CS 18200"]),
        Course("CS 18200", "Foundations", 3, "core", ["CS 18000"]),
    ]

    assert has_cycle(courses) is True


def test_find_two_course_cycles_returns_cycle_pair():
    courses = [
        Course("CS 18000", "Problem Solving", 4, "core", ["CS 18200"]),
        Course("CS 18200", "Foundations", 3, "core", ["CS 18000"]),
    ]

    assert find_two_course_cycles(courses) == [("CS 18000", "CS 18200")]


def test_has_cycle_returns_true_for_three_course_cycle():
    courses = [
        Course("CS 18000", "Problem Solving", 4, "core", ["CS 24000"]),
        Course("CS 24000", "Programming in C", 3, "core", ["CS 25100"]),
        Course("CS 25100", "Data Structures", 3, "core", ["CS 18000"]),
    ]

    assert has_cycle(courses) is True


def test_has_cycle_returns_false_for_branching_safe_graph():
    courses = [
        Course("CS 10000", "Starting Course", 3, "core"),
        Course("MATH 10000", "Starting Math", 3, "core"),
        Course("CS 20000", "Middle Course", 3, "core",
               ["CS 10000", "MATH 10000"]),
        Course("CS 30000", "Advanced Course", 3, "core",
               ["CS 20000", "CS 10000"]),
    ]

    assert has_cycle(courses) is False


def test_has_cycle_returns_true_when_one_branch_contains_cycle():
    courses = [
        Course("CS 30000", "Branching Course", 3, "core",
               ["CS 10000", "CS 20000"]),
        Course("CS 10000", "Safe Course", 3, "core"),
        Course("CS 20000", "Cycle Part One", 3, "core", ["CS 25000"]),
        Course("CS 25000", "Cycle Part Two", 3, "core", ["CS 20000"]),
    ]

    assert has_cycle(courses) is True


def test_has_cycle_returns_true_for_self_prerequisite():
    courses = [
        Course("CS 18000", "Problem Solving", 4, "core", ["CS 18000"]),
    ]

    assert has_cycle(courses) is True


def test_find_cycle_path_returns_only_the_closed_cycle():
    courses = [
        Course("CS 30000", "Branching Course", 3, "core",
               ["CS 10000", "CS 20000"]),
        Course("CS 10000", "Safe Course", 3, "core"),
        Course("CS 20000", "Cycle Part One", 3, "core", ["CS 25000"]),
        Course("CS 25000", "Cycle Part Two", 3, "core", ["CS 20000"]),
    ]

    assert find_cycle_path(courses) == ["CS 20000", "CS 25000", "CS 20000"]


def test_find_cycle_path_returns_empty_list_without_cycle():
    courses = [
        Course("CS 18000", "Problem Solving", 4, "core"),
        Course("CS 18200", "Foundations", 3, "core", ["CS 18000"]),
    ]

    assert find_cycle_path(courses) == []


def test_validation_result_is_valid_without_problems():
    result = ValidationResult(missing_prerequisites=[], cycle_path=[])

    assert result.is_valid is True


def test_validation_result_is_invalid_with_missing_prerequisite():
    result = ValidationResult([("CS 18200", "CS 18000")], [])

    assert result.is_valid is False


def test_validation_result_is_invalid_with_cycle():
    result = ValidationResult([], ["CS 18000", "CS 18200", "CS 18000"])

    assert result.is_valid is False
