import pytest

from degree_planner.models import Course


def test_course_stores_basic_fields():
    course = Course("CS 18000", "Problem Solving", 4, "core")

    assert course.code == "CS 18000"
    assert course.credits == 4


def test_course_rejects_zero_credits():
    with pytest.raises(ValueError):
        Course("CS 18000", "Problem Solving", 0, "core")
