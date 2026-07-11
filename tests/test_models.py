import pytest

from degree_planner.models import Course


def test_course_stores_basic_fields():
    course = Course("CS 18000", "Problem Solving", 4, "core")

    assert course.code == "CS 18000"
    assert course.credits == 4


def test_course_rejects_zero_credits():
    with pytest.raises(ValueError):
        Course("CS 18000", "Problem Solving", 0, "core")


def test_prerequisites_satisfied_when_completed():
    course = Course("CS 18200", "Foundations", 3, "core", ["CS 18000"])

    assert course.prerequisites_satisfied({"CS 18000"})


def test_prerequisites_not_satisfied_when_missing():
    course = Course("CS 18200", "Foundations", 3, "core", ["CS 18000"])

    assert not course.prerequisites_satisfied(set())


def test_prerequisites_satisfied_when_course_has_none():
    course = Course("CS 18000", "Problem Solving", 4, "core")

    assert course.prerequisites_satisfied(set())
