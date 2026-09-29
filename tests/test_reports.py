import pytest

from degree_planner.models import Course
from degree_planner.reports import (
    course_codes,
    format_required_course_group,
    format_semester_plan,
    total_credits,
)


@pytest.mark.parametrize(
    "missing, expected",
    [
        pytest.param(set(), ["Core: no missing required courses"], id="none-missing"),
        pytest.param(
            {"CS 24000", "CS 18200"},
            ["Core: missing required courses", "  CS 18200", "  CS 24000"],
            id="missing-courses-sorted",
        ),
    ],
)
def test_format_required_course_group(missing, expected):
    assert format_required_course_group("Core", missing) == expected


def test_course_codes_returns_codes_in_order():
    courses = [
        Course("CS 18000", "Problem Solving", 4, "core"),
        Course("CS 18200", "Foundations", 3, "core"),
    ]

    assert course_codes(courses) == ["CS 18000", "CS 18200"]


def test_total_credits_adds_course_credits():
    courses = [
        Course("CS 18000", "Problem Solving", 4, "core"),
        Course("CS 18200", "Foundations", 3, "core"),
    ]

    assert total_credits(courses) == 7


def test_format_semester_plan_shows_courses_and_credit_totals():
    course_b = Course("B", "Course B", 3, "core")
    course_c = Course("C", "Course C", 4, "core")
    course_a = Course("A", "Course A", 3, "core", ["B", "C"])
    lines = format_semester_plan([[course_b, course_c], [course_a]])
    assert lines == [
        "Semester 1 (7 credits)",
        "  B: Course B (3 credits)",
        "  C: Course C (4 credits)",
        "Semester 2 (3 credits)",
        "  A: Course A (3 credits)",
    ]
