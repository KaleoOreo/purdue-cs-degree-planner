import pytest

from degree_planner.models import Course
from degree_planner.planning import (
    build_semester_plan,
    find_available_courses,
    plan_next_semester,
)


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


def test_find_available_courses_requires_all_prerequisites():
    courses = [
        Course("CS 24000", "Programming in C", 3, "core", ["CS 18000", "CS 18200"]),
    ]

    available = find_available_courses(courses, {"CS 18000"})

    assert available == []


def test_build_semester_plan_respects_max_credits():
    available = [
        Course("CS 18000", "Problem Solving", 4, "core"),
        Course("CS 18200", "Foundations", 3, "core"),
    ]

    plan = build_semester_plan(available, max_credits=6)

    assert [course.code for course in plan] == ["CS 18000"]


def test_build_semester_plan_allows_exact_credit_limit():
    available = [
        Course("CS 18000", "Problem Solving", 4, "core"),
        Course("CS 18200", "Foundations", 3, "core"),
    ]

    plan = build_semester_plan(available, max_credits=7)

    assert [course.code for course in plan] == ["CS 18000", "CS 18200"]


def test_build_semester_plan_rejects_zero_max_credits():
    with pytest.raises(ValueError):
        build_semester_plan([], max_credits=0)


def test_plan_next_semester_filters_then_applies_credit_limit():
    courses = [
        Course("CS 18000", "Problem Solving", 4, "core"),
        Course("CS 18200", "Foundations", 3, "core", ["CS 18000"]),
        Course("CS 24000", "Programming in C", 3, "core", ["CS 18000", "CS 18200"]),
    ]

    plan = plan_next_semester(courses, {"CS 18000"}, max_credits=3)

    assert [course.code for course in plan] == ["CS 18200"]
